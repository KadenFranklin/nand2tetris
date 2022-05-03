#!/usr/bin/env python3

import sys
import re


def preprocess(lines):
    lines = remove_whitespaces(lines)
    lines = replace_symbols(lines)
    return lines


def replace_symbols(lines):
    symbols = {
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4",
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13",
        "R14": "14",
        "R15": "15",
        "SCREEN": "16384",
        "KBD": "24576",
    }

    # Find all labels, remove them, and add them to symbol table.
    address = 0
    re_label = re.compile("\((\S*)\)")
    lines_without_labels = []
    for line in lines:
        m = re_label.match(line)
        if m:
            label = m.groups()[0]
            if label in symbols:
                raise Exception("Multiple defines for {}.".format(line))
            symbols[label] = str(address)
        else:
            lines_without_labels.append(line)
            address += 1
    lines = lines_without_labels

    # Find all address instruction and replace symbols.
    lines_without_symbols = []
    re_symbol = re.compile("@([A-Za-z]\S*)")
    address = 16
    for line in lines:
        m = re_symbol.match(line)
        if m:
            symbol = m.groups()[0]
            if symbol in symbols:
                symbol_value = symbols[symbol]
            else:
                symbol_value = str(address)
                symbols[symbol] = symbol_value
                address += 1
            lines_without_symbols.append("@" + symbol_value)
        else:
            lines_without_symbols.append(line)
    return lines_without_symbols


def assemble(lines):
    lines = assemble_instructions(lines)
    return lines


def remove_whitespaces(lines):
    r_whitespace = re.compile("\s")
    r_comment = re.compile("//.*")
    lines = [r_whitespace.sub("", line) for line in lines]
    lines = [r_comment.sub("", line) for line in lines]
    return [line for line in lines if line]


def assemble_instructions(lines):
    return [assemble_instruction(line) for line in lines]


def assemble_instruction(line):
    if line.startswith("@"):
        return assemble_a_instruction(line)
    else:
        return assemble_c_instruction(line)
        
        
def assemble_c_instruction(line):
    r = re.compile("(\S+)=(\S+);(\S+)")
    if not ";" in line:
        line = line + ";null"
    if not "=" in line:
        line = "null=" + line
    dest, comp, jump = r.match(line).groups()
    ins_str = "111" + comp_lookup(comp) + dest_lookup(dest) + jump_lookup(jump)
    return ins_str


def assemble_a_instruction(line):
    adr_str = line.replace("@", "")
    adr_int = int(adr_str)
    adr_bin_str = bin(adr_int)[2:]
    adr_bin_str = "0" * (16 - len(adr_bin_str)) + adr_bin_str
    return adr_bin_str


def comp_lookup(comp_str):
    return {
        "0":   "0101010",
        "1":   "0111111",
        "-1":  "0111010",
        "D":   "0001100",
        "A":   "0110000",
        "M":   "1110000",
        "!D":  "0001101",
        "!A":  "0110001",
        "!M":  "1110001",
        "-D":  "0001111",
        "-A":  "0110011",
        "-M":  "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "D+M": "1000010",
        "D-A": "0010011",
        "D-M": "1010011",
        "A-D": "0000111",
        "M-D": "1000111",
        "D&A": "0000000",
        "D&M": "1000000",
        "D|A": "0010101",
        "D|M": "1010101"
    }[comp_str]


def dest_lookup(dest_str):
    return {
        "null": "000",
        "M":    "001",
        "D":    "010",
        "MD":   "011",
        "A":    "100",
        "AM":   "101",
        "AD":   "110",
        "AMD":  "111"
    }[dest_str]


def jump_lookup(jump_str):
    return {
        "null": "000",
        "JGT":  "001",
        "JEQ":  "010",
        "JGE":  "011",
        "JLT":  "100",
        "JNE":  "101",
        "JLE":  "110",
        "JMP":  "111"
    }[jump_str]


if __name__ == "__main__":
    if not sys.argv[1:]:
        sys.exit("Call: ./assembler.py <hack_asm_file>")

    for hack_asm_file in sys.argv[1:]:
        if not hack_asm_file.endswith(".asm"):
            sys.exit("Hack asm file must have a .asm file ending.")
        hack_asm_ns_file = hack_asm_file.replace(".asm", ".nosymbol.asm")
        hack_bin_file = hack_asm_file.replace(".asm", ".hack")

        with open(hack_asm_file, 'r') as f:
            assembly_lines = f.readlines()

        preprocessed_lines = preprocess(assembly_lines)
        binary_lines = assemble(preprocessed_lines)

        with open(hack_asm_ns_file, 'w') as f:
            for line in preprocessed_lines:
                f.write(line + "\n")

        with open(hack_bin_file, 'w') as f:
            for line in binary_lines:
                f.write(line + "\n")

        print(f"{hack_asm_file} -> {hack_bin_file}")

