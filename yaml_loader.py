from __future__ import annotations
from typing import List, Tuple
import yaml

from turing_machine import TuringMachine


def load_turing_machine_from_yaml(path: str) -> Tuple[TuringMachine, List[str]]:
    """
    Carga un archivo YAML y construye:
    - Una instancia de TuringMachine
    - La lista de inputs configurados
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if "mt" not in data:
        raise ValueError("El archivo YAML debe tener la clave raíz 'mt'.")

    mt_conf = data["mt"]
    inputs = mt_conf.get("inputs", [])

    tm = TuringMachine.from_yaml_config(data)
    return tm, inputs
