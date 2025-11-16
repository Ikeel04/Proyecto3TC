from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Any, Iterable, Optional

from tape import Tape


@dataclass
class Transition:
    next_state: str
    write_symbol: str
    move: str  # 'L', 'R' o 'S'


@dataclass
class RunResult:
    input_string: str
    accepted: bool
    final_state: str
    final_tape: str
    ids: List[str]


class TuringMachine:
    def __init__(
        self,
        states: Iterable[str],
        input_alphabet: Iterable[str],
        tape_alphabet: Iterable[str],
        initial_state: str,
        accept_states: Iterable[str],
        transitions: Dict[Tuple[str, str], Transition],
        blank_symbol: str = "B",
        name: str = "MT",
    ) -> None:
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.initial_state = initial_state
        self.accept_states = set(accept_states)
        self.transitions = transitions
        self.blank_symbol = blank_symbol
        self.name = name

        if self.initial_state not in self.states:
            raise ValueError(f"Estado inicial inválido: {self.initial_state}")

        if not self.accept_states.issubset(self.states):
            raise ValueError("Hay estados de aceptación que no están en el conjunto de estados.")

        if self.blank_symbol not in self.tape_alphabet:
            raise ValueError("El símbolo blanco debe estar en el alfabeto de cinta.")

    def _format_id(self, tape: Tape, state: str) -> str:
        """
        Construye una descripción instantánea (ID) como cadena.
        Ejemplo: 'BB[q0]aabbB'
        """
        symbols, head_pos = tape.get_view()
        parts: List[str] = []
        for i, sym in enumerate(symbols):
            if i == head_pos:
                parts.append(f"[{state}]{sym}")
            else:
                parts.append(sym)
        return "".join(parts)

    def run(self, input_string: str, max_steps: Optional[int] = None) -> RunResult:
        """
        Ejecuta la MT sobre una cadena de entrada.
        - max_steps: límite opcional para evitar bucles infinitos.
        """
        tape = Tape(blank_symbol=self.blank_symbol)
        tape.load_input(input_string)

        current_state = self.initial_state
        steps = 0
        ids: List[str] = [self._format_id(tape, current_state)]

        while True:
            symbol_under_head = tape.read()
            key = (current_state, symbol_under_head)

            transition = self.transitions.get(key)
            if transition is None:
                # No hay transición definida → se detiene
                break

            # Aplicar transición
            tape.write(transition.write_symbol)
            tape.move(transition.move)
            current_state = transition.next_state

            ids.append(self._format_id(tape, current_state))

            steps += 1
            if max_steps is not None and steps >= max_steps:
                # Límite de seguridad para bucles infinitos
                ids.append(">>> Límite de pasos alcanzado, posible lazo infinito.")
                break

        final_tape_str = tape.get_string()
        accepted = current_state in self.accept_states

        return RunResult(
            input_string=input_string,
            accepted=accepted,
            final_state=current_state,
            final_tape=final_tape_str,
            ids=ids,
        )

    @classmethod
    def from_yaml_config(cls, config: dict) -> "TuringMachine":
        """
        Crea una MT a partir de un diccionario cargado desde YAML con la forma:

        mt:
          states: [...]
          input_alphabet: [...]
          tape_alphabet: [...]
          initial_state: q0
          accept_states: [qf]
          transitions:
            - state: q0
              read: a / [a, B]
              write: X / [X, B]
              move: R
              next: q1
          inputs:
            - "aabb"
        """
        mt_conf = config["mt"]

        states = mt_conf["states"]
        input_alphabet = mt_conf["input_alphabet"]
        tape_alphabet = mt_conf["tape_alphabet"]
        initial_state = mt_conf["initial_state"]
        accept_states = mt_conf["accept_states"]
        transitions_list = mt_conf["transitions"]

        blank_symbol = "B"
        if "blank_symbol" in mt_conf:
            blank_symbol = mt_conf["blank_symbol"]

        transitions: Dict[Tuple[str, str], Transition] = {}

        for t in transitions_list:
            state = t["state"]
            read_field: Any = t["read"]
            write_field: Any = t["write"]
            move: str = t["move"]
            next_state: str = t["next"]

            # Soportar:
            #   read: "a"
            #   write: "X"
            # o
            #   read: [a, B]
            #   write: [X, B]
            if isinstance(read_field, list):
                read_symbols = list(read_field)
            else:
                read_symbols = [read_field]

            if isinstance(write_field, list):
                write_symbols = list(write_field)
            else:
                # Si solo dan un símbolo de escritura, lo replicamos
                write_symbols = [write_field] * len(read_symbols)

            if len(read_symbols) != len(write_symbols):
                raise ValueError(
                    f"Transición inconsistente (state={state}): "
                    f"read={read_symbols}, write={write_symbols}"
                )

            for r_sym, w_sym in zip(read_symbols, write_symbols):
                if r_sym not in tape_alphabet:
                    raise ValueError(
                        f"Símbolo de lectura '{r_sym}' no está en el alfabeto de cinta."
                    )
                if w_sym not in tape_alphabet:
                    raise ValueError(
                        f"Símbolo de escritura '{w_sym}' no está en el alfabeto de cinta."
                    )

                key = (state, r_sym)
                transitions[key] = Transition(
                    next_state=next_state,
                    write_symbol=w_sym,
                    move=move,
                )

        return cls(
            states=states,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
            initial_state=initial_state,
            accept_states=accept_states,
            transitions=transitions,
            blank_symbol=blank_symbol,
        )
