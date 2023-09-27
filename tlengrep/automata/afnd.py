from enum import Enum
from typing import Hashable, Union, List, Dict
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
            raise ValueError(f"Se requiere un estado inicial para determinizar al automata.")

        # States of the new automata, they are sets of states of the current one
        new_initial = frozenset(self._l_closure(set([self.initial_state])))
        new_states = set([new_initial])
        unvisited = set([new_initial])
        transitions = []

        while unvisited:
            t = unvisited.pop()

            for a in self.alphabet:
                u = self._move(t, a)

                if not u == set():
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
            afd.add_state(s, final = True)

        afd.mark_initial_state(new_initial)

        for (org, letter, dest) in transitions:
            afd.add_transition(org, dest, letter)

        afd.normalize_states()

        return afd

    def _move(self, states: frozenset[Hashable], letter: str):
        res = set()
        for s in states:
            if letter in self.transitions[s]:
                res = res.union(self.transitions[s][letter])

        return self._l_closure(res)

    def _l_closure(self, states: set[Hashable]) -> set[Hashable]:
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
