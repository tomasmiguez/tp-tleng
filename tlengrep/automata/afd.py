from typing import Hashable, List, Dict
from automata.af import AF

__all__ = ["AFD"]


class AFD(AF):
    """Autómata finito determinístico."""

    def add_transition(self, state1: Hashable, state2: Hashable, char: str):
        """Agrega una transición al autómata."""
        if state1 not in self.states:
            raise ValueError(f"El estado {state1} no pertenece al autómata.")
        if state2 not in self.states:
            raise ValueError(f"El estado {state2} no pertenece al autómata.")
        self.transitions[state1][char] = state2
        self.alphabet.add(char)

        return self

    def minimize(self):
        """Minimiza el autómata."""
        classes = {
            state: {'=eq': 'F' if state in self.final_states else 'N'}
            for state in self.states
        }
        q_of_classes = 0
        while True:
            prior_q_of_classes = q_of_classes
            q_of_classes = len({v['=eq'] for _, v in classes.items()})
            rows = {}
            for state in self.states:
                transitions = sorted(self._transitions_to_str(state).items())
                rows[state] = ''
                for char, to_state in transitions:
                    rows[state] += classes[to_state]['=eq']
                    classes[state][char] = classes[to_state]['=eq']
            if q_of_classes <= prior_q_of_classes:
                break
            for state in self.states:
                classes[state]['=eq'] = rows[state]

        final_states = self.final_states
        initial_state = self.initial_state
        self._reset_transitions()

        new_states = {}
        for state, v in classes.items():
            if v['=eq'] not in new_states:
                new_states[v['=eq']] = self.add_state(
                    v['=eq'], v['=eq'] in final_states
                )
            if state == initial_state:
                self.mark_initial_state(v['=eq'])
        for v in classes.values():
            for char in self.alphabet:
                self.add_transition(v['=eq'], v[char], char)
        self.normalize_states()

    def is_accepted(self, word: str) -> bool:
        raise NotImplementedError

    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        self.transitions[new_name] = self.transitions[old_name]
        del self.transitions[old_name]
        for state in self.transitions:
            for char in self.transitions[state]:
                if self.transitions[state][char] == old_name:
                    self.transitions[state][char] = new_name

        return self

    def _get_extended_alphabet(self) -> List[str]:
        """Obtiene el alfabeto extendido del autómata (incluyendo símbolos especiales)."""
        return list(self.alphabet)

    def _transitions_to_str(self, state: Hashable) -> Dict[Hashable, str]:
        """Devuelve las transiciones de un estado para cada símbolo como string."""
        transitions = {}
        for char in self._get_extended_alphabet():
            if char in self.transitions[state]:
                transitions[char] = self.transitions[state][char]
            else:
                transitions[char] = "-"
        return transitions
