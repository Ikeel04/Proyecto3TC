from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Tape:
    """
    Cinta infinita hacia izquierda y derecha, implementada con un diccionario.
    Solo guarda las celdas que no son blanco.
    """
    blank_symbol: str = "B"
    _cells: Dict[int, str] = field(default_factory=dict)
    head: int = 0

    def load_input(self, input_string: str) -> None:
        """
        Carga una cadena en la cinta, iniciando en la posición 0.
        """
        self._cells.clear()
        for i, ch in enumerate(input_string):
            self._cells[i] = ch
        self.head = 0

    def read(self) -> str:
        """
        Lee el símbolo bajo el cabezal.
        """
        return self._cells.get(self.head, self.blank_symbol)

    def write(self, symbol: str) -> None:
        """
        Escribe un símbolo en la posición actual del cabezal.
        """
        if symbol == self.blank_symbol and self.head in self._cells:
            # Opcional: si escribimos blanco, podemos limpiar la celda
            del self._cells[self.head]
        else:
            self._cells[self.head] = symbol

    def move(self, direction: str) -> None:
        """
        Mueve el cabezal: 'L' (izquierda), 'R' (derecha), o 'S' (sin movimiento).
        """
        d = direction.upper()
        if d == "L":
            self.head -= 1
        elif d == "R":
            self.head += 1
        elif d == "S":
            # Sin movimiento
            return
        else:
            raise ValueError(f"Dirección de movimiento inválida: {direction}")

    def _used_indices(self) -> Tuple[int, int]:
        """
        Calcula el rango mínimo [min_i, max_i] que contiene las celdas usadas y el cabezal.
        Si la cinta está vacía, solo se toma en cuenta la posición del cabezal.
        """
        if not self._cells:
            return self.head, self.head
        indices = set(self._cells.keys()) | {self.head}
        return min(indices), max(indices)

    def get_view(self) -> Tuple[List[str], int]:
        """
        Devuelve una vista corta de la cinta:
        - lista de símbolos desde la posición min hasta max
        - índice del cabezal dentro de esa lista
        """
        min_i, max_i = self._used_indices()
        symbols: List[str] = []
        for i in range(min_i, max_i + 1):
            symbols.append(self._cells.get(i, self.blank_symbol))
        head_pos = self.head - min_i
        return symbols, head_pos

    def get_string(self) -> str:
        """
        Devuelve la cinta como cadena (sin marcar el cabezal),
        usando solo el rango mínimo que contiene símbolos o el cabezal.
        """
        symbols, _ = self.get_view()
        return "".join(symbols)
