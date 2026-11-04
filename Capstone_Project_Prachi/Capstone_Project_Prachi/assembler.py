#!/usr/bin/env python3
"""
A small two-pass Hack assembler for the Nand2Tetris project.
For K=27 (K mod 3 = 0), it writes every label and variable address
to symbols.txt.
Usage: python assembler.py Box.asm
"""
from pathlib import Path
import sys

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    **{f"R{i}": i for i in range(16)},
    "SCREEN": 16384, "KBD": 24576,
}
DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}
COMP = {
    "0":"0101010", "1":"0111111", "-1":"0111010",
    "D":"0001100", "A":"0110000", "M":"1110000",
    "!D":"0001101", "!A":"0110001", "!M":"1110001",
    "-D":"0001111", "-A":"0110011", "-M":"1110011",
    "D+1":"0011111", "A+1":"0110111", "M+1":"1110111",
    "D-1":"0001110", "A-1":"0110010", "M-1":"1110010",
    "D+A":"0000010", "D+M":"1000010",
    "D-A":"0010011", "D-M":"1010011",
    "A-D":"0000111", "M-D":"1000111",
    "D&A":"0000000", "D&M":"1000000",
    "D|A":"0010101", "D|M":"1010101",
}

def clean_lines(path):
    result = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if line:
            result.append((number, line))
    return result

def assemble(source):
    lines = clean_lines(source)
    symbols = dict(PREDEFINED)
    labels = {}
    rom = 0
    # Pass 1: collect labels.
    for line_no, line in lines:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1].strip()
            if not label or not label.replace("_", "a").isalnum():
                raise ValueError(f"Line {line_no}: invalid label")
            if label in labels:
                print(f"Warning: duplicate label '{label}' on line {line_no}; first definition kept.")
            elif label in PREDEFINED:
                print(f"Warning: label '{label}' conflicts with a predefined symbol.")
            else:
                labels[label] = rom
                symbols[label] = rom
        else:
            rom += 1

    # Pass 2: encode instructions and allocate variables.
    next_var = 16
    machine = []
    variables = {}
    for line_no, line in lines:
        if line.startswith("(") and line.endswith(")"):
            continue
        if line.startswith("@"):
            token = line[1:].strip()
            if token.isdigit():
                value = int(token)
            else:
                if token not in symbols:
                    symbols[token] = next_var
                    variables[token] = next_var
                    next_var += 1
                value = symbols[token]
            if not 0 <= value <= 32767:
                raise ValueError(f"Line {line_no}: A-instruction value out of range: {value}")
            machine.append(f"{value:016b}")
            continue

        # C-instruction: dest=comp;jump (either side may be absent).
        if line.count("=") > 1 or line.count(";") > 1:
            raise ValueError(f"Line {line_no}: invalid C-instruction")
        dest, rest = (line.split("=", 1) if "=" in line else ("", line))
        comp, jump = (rest.split(";", 1) if ";" in rest else (rest, ""))
        dest, comp, jump = dest.strip(), comp.strip(), jump.strip()
        if comp not in COMP or dest not in DEST or jump not in JUMP:
            raise ValueError(f"Line {line_no}: invalid instruction '{line}'")
        machine.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])

    return machine, symbols, labels, variables

def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        raise SystemExit(1)
    source = Path(sys.argv[1])
    if not source.exists():
        print(f"File not found: {source}")
        raise SystemExit(1)
    try:
        machine, symbols, labels, variables = assemble(source)
    except ValueError as exc:
        print(exc)
        raise SystemExit(1)
    output = source.with_suffix(".hack")
    output.write_text("\n".join(machine) + "\n", encoding="utf-8")
    # K=27 => required extra feature: export all labels and variables.
    rows = ["# Symbol table for " + source.name, "# name,address,kind"]
    for name, address in sorted(PREDEFINED.items(), key=lambda x: x[1]):
        rows.append(f"{name},{address},predefined")
    for name, address in sorted(labels.items()):
        rows.append(f"{name},{address},label")
    for name, address in sorted(variables.items(), key=lambda x: x[1]):
        rows.append(f"{name},{address},variable")
    Path("symbols.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Created {output} ({len(machine)} instructions)")
    print("Created symbols.txt")

if __name__ == "__main__":
    main()
