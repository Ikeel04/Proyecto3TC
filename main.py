from __future__ import annotations
import sys
from typing import Optional

from yaml_loader import load_turing_machine_from_yaml


def run_simulation(yaml_path: str, max_steps: Optional[int] = None) -> None:
    tm, inputs = load_turing_machine_from_yaml(yaml_path)

    if not inputs:
        print("No hay entradas configuradas en el archivo YAML (sección mt -> inputs).")
        return

    print(f"=== Simulador de Máquina de Turing ===")
    print(f"Archivo de configuración: {yaml_path}")
    print(f"Número de cadenas a simular: {len(inputs)}")
    print()

    for idx, input_str in enumerate(inputs, start=1):
        print(f"--- Cadena #{idx}: '{input_str}' ---")
        result = tm.run(input_str, max_steps=max_steps)

        # Imprimir todas las IDs
        for step, id_str in enumerate(result.ids):
            print(f"Paso {step:03d}: {id_str}")

        estado_final = result.final_state
        estado_aceptacion = "ACEPTADA" if result.accepted else "RECHAZADA"

        print()
        print(f"Resultado para '{result.input_string}': {estado_aceptacion}")
        print(f"Estado final: {estado_final}")
        print(f"Cinta final: {result.final_tape}")
        print("-" * 40)
        print()


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py mt_example.yaml")
        sys.exit(1)

    yaml_path = sys.argv[1]

    run_simulation(yaml_path, max_steps=None)


if __name__ == "__main__":
    main()
