from abc import ABC, abstractmethod

from automata import AFND

__all__ = ["RegEx", "Empty", "Lambda", "Char", "Union", "Concat", "Star", "Plus"]


class RegEx(ABC):
    """Clase abstracta para representar expresiones regulares."""

    @abstractmethod
    def naive_match(self, word: str) -> bool:
        """
        Indica si la expresión regular acepta la cadena dada.
        Implementación recursiva, poco eficiente.
        """
        pass

    def match(self, word: str) -> bool:
        """Indica si la expresión regular acepta la cadena dada."""
        return self.to_afnd().determinize().minimize_hopcroft().accepts(word)

    @abstractmethod
    def to_afnd(self) -> AFND:
        """Convierte la expresión regular a un AFND."""
        pass

    @abstractmethod
    def _atomic(self) -> bool:
        """
        (Interno) Indica si la expresión regular es atómica. Útil para
        implementar la función __str__.
        """
        pass


class Empty(RegEx):
    """Expresión regular que denota el lenguaje vacío (∅)."""

    def naive_match(self, word: str):
        return False

    def to_afnd(self) -> AFND:
        # No es minimal pero no es necesario ya que tenemos minimize.
        # Es el minimal que no complejiza determinize.
        return AFND().add_state('q0').mark_initial_state('q0')

    def _atomic(self):
        return True

    def __str__(self):
        return "∅"


class Lambda(RegEx):
    """Expresión regular que denota el lenguaje de la cadena vacía (Λ)."""

    def naive_match(self, word: str):
        return word == ""

    def to_afnd(self) -> AFND:
        return AFND().add_state('q0', final=True).mark_initial_state('q0')

    def _atomic(self):
        return True

    def __str__(self):
        return "λ"


class Char(RegEx):
    """Expresión regular que denota el lenguaje de un determinado carácter."""

    def __init__(self, char: str):
        assert len(char) == 1
        self.char = char

    def naive_match(self, word: str):
        return word == self.char

    def to_afnd(self) -> AFND:
        return (
            AFND()
            .add_state('q0')
            .mark_initial_state('q0')
            .add_state('q1', final=True)
            .add_transition('q0', 'q1', self.char)
        )

    def _atomic(self):
        return True

    def __str__(self):
        return self.char


class Concat(RegEx):
    """Expresión regular que denota la concatenación de dos expresiones regulares."""

    def __init__(self, exp1: RegEx, exp2: RegEx):
        self.exp1 = exp1
        self.exp2 = exp2

    def naive_match(self, word: str):
        for i in range(len(word) + 1):
            if self.exp1.naive_match(word[:i]) and self.exp2.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:
        return self.exp1.to_afnd().concat(self.exp2.to_afnd())

    def _atomic(self):
        return False

    def __str__(self):
        return (
            f"{f'({self.exp1})' if not self.exp1._atomic() else self.exp1}"
            f"{f'({self.exp2})' if not self.exp2._atomic() else self.exp2}"
        )


class Union(RegEx):
    """Expresión regular que denota la unión de dos expresiones regulares."""

    def __init__(self, exp1: RegEx, exp2: RegEx):
        self.exp1 = exp1
        self.exp2 = exp2

    def naive_match(self, word: str):
        return self.exp1.naive_match(word) or self.exp2.naive_match(word)

    def to_afnd(self) -> AFND:
        return self.exp1.to_afnd().union(self.exp2.to_afnd())

    def _atomic(self):
        return False

    def __str__(self):
        return (
            f"{f'({self.exp1})' if not self.exp1._atomic() else self.exp1}"
            f"|{f'({self.exp2})' if not self.exp2._atomic() else self.exp2}"
        )


class Star(RegEx):
    """Expresión regular que denota la clausura de Kleene de otra expresión regular."""

    def __init__(self, exp: RegEx):
        self.exp = exp

    def naive_match(self, word: str):
        if word == "" or self.exp.naive_match(word):
            return True
        for i in range(1, len(word) + 1):
            if self.exp.naive_match(word[:i]) and self.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:
        return self.exp.to_afnd().kleene_closure()

    def _atomic(self):
        return False

    def __str__(self):
        return f"({self.exp})*" if not self.exp._atomic() else f"{self.exp}*"


class Plus(RegEx):
    """Expresión regular que denota la clausura positiva de otra expresión regular."""

    def __init__(self, exp: RegEx):
        self.exp = exp

    def naive_match(self, word: str):
        if self.exp.naive_match(word):
            return True
        for i in range(1, len(word) + 1):
            if self.exp.naive_match(word[:i]) and self.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:
        return self.exp.to_afnd().positive_closure()

    def _atomic(self) -> bool:
        return False

    def __str__(self):
        return f"({self.exp})+" if not self.exp._atomic() else f"{self.exp}+"

class RegClass(RegEx):
    """Expresión regular que denota una clase de caracteres."""

    def __init__(self, chars: set):
        self.chars = chars

    def naive_match(self, word: str):
        return word in self.chars

    def to_afnd(self) -> AFND:
        afnd = AFND().add_state('q0').mark_initial_state('q0').add_state('q1', final=True)

        for char in self.chars:
            afnd.add_transition('q0', 'q1', char)

        return afnd

    def _atomic(self):
        return True

    def __str__(self):
        return f"[{self.chars}]"
