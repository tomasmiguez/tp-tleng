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
            rows = {}
            # Agrego las clases de equivalencia de cada estado
            for state in self.states:
                transitions = sorted(self._transitions_to_str(state).items())
                rows[state] = classes[state]['=eq']
                for char, to_state in transitions:
                    rows[state] += classes[to_state]['=eq']
                    classes[state][char] = classes[to_state]['=eq']
            # Verifico si dejé de agregar clases de equivalencia
            q_of_classes = len({v['=eq'] for _, v in classes.items()})
            if prior_q_of_classes == q_of_classes:
                break
            # Actualizo las nuevas clases de equivalencia
            for state in self.states:
                classes[state]['=eq'] = rows[state]

        final_states = self.final_states
        initial_state = self.initial_state
        self._reset_transitions()

        new_states = set()
        # Agrego los estados y transiciones del nuevo autómata en base a las clases de equivalencia
        for state, v in classes.items():
            if v['=eq'] not in new_states:
                self.add_state(v['=eq'], state in final_states)
                new_states.add(v['=eq'])
            if state == initial_state:
                self.mark_initial_state(v['=eq'])
        # Agrego las transiciones del nuevo autómata en base a las clases de equivalencia
        for v in classes.values():
            for char in self.alphabet:
                self.add_transition(v['=eq'], v[char], char)
        return self.normalize_states()

    def minimize_hopcroft(self):
        """Minimiza el autómata usando el algoritmo de Hopcroft."""

        # Particion inicial
        P = [self.final_states, self.states - self.final_states]
        W = [self.final_states, self.states - self.final_states]

        # Particion final
        while W:
            A = W.pop()
            for char in self.alphabet:
                X = set()
                for state in self.states:
                    if self.transitions[state][char] in A:
                        X.add(state)
                for Y in P:
                    intersect = X.intersection(Y)
                    difference = Y.difference(X)

                    if not intersect or not difference:
                        continue

                    P.remove(Y)
                    P.append(intersect)
                    P.append(difference)

                    if Y in W:
                        W.remove(Y)
                        W.append(intersect)
                        W.append(difference)
                    else:
                        if len(intersect) <= len(difference):
                            W.append(intersect)
                        else:
                            W.append(difference)

        result = AFD()
        state_to_partition = {}
        for partition in P:
            is_final = len(partition.intersection(self.final_states)) != 0
            result.add_state(frozenset(partition), is_final)
            for state in partition:
                state_to_partition[state] = frozenset(partition)
                if state == self.initial_state:
                    result.mark_initial_state(frozenset(partition))

        for state in self.states:
            for char in self.alphabet:
                result.add_transition(state_to_partition[state],
                                      state_to_partition[self.transitions[state][char]],
                                      char)

        return result

    def accepts(self, word: str) -> bool:
        """Determina si una cadena es aceptada por el automata. (En tiempo lineal, duuuh.)"""
        current_state = self.initial_state
        for letter in word:
            if not letter in self.transitions[current_state]:
                return False

            current_state = self.transitions[current_state][letter]

        if current_state in self.final_states:
            return True

        return False

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
