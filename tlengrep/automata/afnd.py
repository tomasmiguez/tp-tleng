from enum import Enum
from typing import FrozenSet, Hashable, Union, List, Dict, Set
from collections import deque

from automata.af import AF
from automata.afd import AFD


__all__ = ["AFND"]


class SpecialSymbol(Enum):
    Lambda = "λ"


class AFND(AF):
    """Autómata finito no determinístico (con transiciones lambda)."""

    def add_transition(
        self, state1: Hashable, state2: Hashable, char: Union[str, SpecialSymbol]
    ):
        """Agrega una transición al autómata."""
        if state1 not in self.states:
            raise ValueError(f"El estado {state1} no pertenece al autómata.")
        if state2 not in self.states:
            raise ValueError(f"El estado {state2} no pertenece al autómata.")
        if char not in self.transitions[state1]:
            self.transitions[state1][char] = set()
        self.transitions[state1][char].add(state2)
        if char is not SpecialSymbol.Lambda:
            self.alphabet.add(char)

        return self

    def determinize(self) -> AFD:
        """Determiniza el autómata."""
        if not self.initial_state:
            raise ValueError(
                f"Se requiere un estado inicial para determinizar al automata."
            )

        # States of the new automata, they are sets of states of the current one
        new_initial = frozenset(self._l_closure(set([self.initial_state])))
        new_states = set([new_initial])
        unvisited = set([new_initial])
        transitions = []

        while unvisited:
            t = unvisited.pop()

            for a in self.alphabet:
                u = self._move(t, a)

                if not u in new_states:
                    new_states.add(frozenset(u))
                    unvisited.add(frozenset(u))

                transitions.append((t, a, u))

        final_states = set()

        for new_s in new_states:
            for s in new_s:
                if s in self.final_states:
                    final_states.add(new_s)
                    break

        nonfinal_states = new_states - final_states

        afd = AFD()

        for s in nonfinal_states:
            afd.add_state(s)
        for s in final_states:
            afd.add_state(s, final=True)

        afd.mark_initial_state(new_initial)

        for org, letter, dest in transitions:
            afd.add_transition(org, dest, letter)

        afd.normalize_states()

        return afd

    def _move(self, states: FrozenSet[Hashable], letter: str):
        res = set()
        for s in states:
            if letter in self.transitions[s]:
                res = res.union(self.transitions[s][letter])

        return self._l_closure(res)

    def _l_closure(self, states: Set[Hashable]) -> Set[Hashable]:
        """Calcula la clausura lambda de un estado con BFS. (Se podria recursivamente con PD?)"""
        visited = set(states)
        q = deque(states)

        while q:
            s = q.popleft()

            if SpecialSymbol.Lambda in self.transitions[s]:
                for l_neighbour in self.transitions[s][SpecialSymbol.Lambda]:
                    if not l_neighbour in visited:
                        q.append(l_neighbour)
                        visited.add(l_neighbour)

        return visited

    def concat(self, other):
        """Dado otro AFND, devuelve un automata que reconoce el lenguaje
        resultante de la concatenacion de los lenguajes reconocidos por self seguido de other.
        """

        result = self._merge(other)

        result.mark_initial_state(self.initial_state)
        result.final_states = other.final_states

        for final_state in self.final_states:
            result.add_transition(
                final_state, other.initial_state, SpecialSymbol.Lambda
            )

        return result

    def union(self, other):
        """Dado otro AFND, devuelve un automata que reconoce el lenguahe resultante
        de la union de los lenguajes reconocidos por ambos automatas."""
        result = self._merge(other)

        # Esto es medio feito, porque implica conocimiento del funcionamiento de
        # `_merge`, ya que solo sabiendo que normaliza con prefijos p y q podemos
        # garantizar que ini no genera colision, pero es mi metodo privado y hago lo
        # que quiero (la posta seria abstraer eso de alguna forma, si fuera codigo de
        # verdad lo haria).
        result.add_state("ini")
        result.mark_initial_state("ini")

        # Tambien feardo, depende de que mute el estado de los parametros _merge, que ya
        # de por si es bastante horrible.
        result.add_transition("ini", self.initial_state, SpecialSymbol.Lambda)
        result.add_transition("ini", other.initial_state, SpecialSymbol.Lambda)

        result.final_states = self.final_states.union(other.final_states)

        return result

    def positive_closure(self):
        """Devuelve un nuevo AFND que reconoce al lenguaje resultante de aplicar
        clausura positiva al lenguaje reconocido por self."""
        for final_state in self.final_states:
            self.add_transition(final_state, self.initial_state, SpecialSymbol.Lambda)

        return self

    def kleene_closure(self):
        """Devuelve un nuevo AFND que reconoce al lenguaje resultante de aplicar
        clausura de Kleene al lenguaje reconocido por self."""
        self.positive_closure()

        self.final_states.add(self.initial_state)

        return self

    def _merge(self, other):
        """Dado otro AFND, devuelve un automate que contiene la union de ambos alfabetos,
        estados, y transiciones; evitando colisiones de nombres. No tiene estado inicial
        ni finales."""
        self.add_prefix("q")
        other.add_prefix("p")

        result = AFND()
        result.states = self.states.union(other.states)
        result.alphabet = self.alphabet.union(other.alphabet)
        result.transitions = {**self.transitions, **other.transitions}

        return result

    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        self.transitions[new_name] = self.transitions[old_name]
        del self.transitions[old_name]
        for state in self.transitions:
            for char in self.transitions[state]:
                if old_name in self.transitions[state][char]:
                    self.transitions[state][char].remove(old_name)
                    self.transitions[state][char].add(new_name)

        return self

    def _get_extended_alphabet(self) -> List[str]:
        """Obtiene el alfabeto extendido del autómata (incluyendo símbolos especiales)."""
        return list(self.alphabet) + [SpecialSymbol.Lambda]

    def _transitions_to_str(self, state: Hashable) -> Dict[Hashable, str]:
        """Devuelve las transiciones de un estado para cada símbolo como string."""
        transitions = {}
        for char in self._get_extended_alphabet():
            if char in self.transitions[state]:
                transitions[char] = ",".join(self.transitions[state][char])
            else:
                transitions[char] = "-"
        return transitions
