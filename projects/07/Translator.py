import os
import sys


class Parser:

    def __init__(self, file_name: str):
        self.current_command = ""
        self.current = -1
        self.commands = []
        file = open(file_name)
        for line in file:
            line = line.partition("//")[0]
            line = line.strip()
            if line:
                self.commands.append(line)
        file.close()

    def hasMoreCommands(self) -> bool:
        return (self.current + 1) < len(self.commands)

    def advance(self) -> None:
        self.current += 1
        self.current_command = self.commands[self.current]

    def commandType(self) -> str:
        arithmetic_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        cmd = self.current_command.split(" ")[0]
        if cmd in arithmetic_commands:
            return "C_ARITHMETIC"
        elif cmd == "push":
            return "C_PUSH"
        elif cmd == "pop":
            return "C_POP"
        else:
            raise NameError("Unknown command type")

    def arg1(self) -> str:
        if self.commandType() == "C_ARITHMETIC":
            return self.current_command.split(" ")[0]
        else:
            return self.current_command.split(" ")[1]

    def arg2(self) -> int:
        return int(self.current_command.split(" ")[2])


class CodeWriter:

    def __init__(self, file_name: str):
        self.file_name = file_name[:-4]
        self.file = open(file_name, "w")
        self.label_counter = 0
        self.symbols = {"add": "M=D+M", "sub": "M=M-D", "and": "M=D&M", "or": "M=D|M", "neg": "M=-M", "not": "M=!M", "eq": "D;JEQ", "gt": "D;JGT", "lt": "D;JLT", "local": "@LCL", "argument": "@ARG", "this": "@THIS", "that": "@THAT", "constant": "", "static": "", "pointer": "@3", "temp": "@5"}

    def comment(self, command: str):
        print("// " + command, file=self.file)

    def write_arithmetic(self, command: str):
        output = []
        if command in ["add", "sub", "and", "or"]:
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            output.append("@SP")
            output.append("A=M-1")
            output.append(self.symbols[command])
        elif command in ["neg", "not"]:
            output.append("@SP")
            output.append("A=M-1")
            output.append(self.symbols[command])
        elif command in ["eq", "gt", "lt"]:
            jump_label = "CompLabel" + str(self.label_counter)
            self.label_counter += 1
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            output.append("@SP")
            output.append("A=M-1")
            output.append("D=M-D")
            output.append("M=-1")
            output.append("@" + jump_label)
            output.append(self.symbols[command])
            output.append("@SP")
            output.append("A=M-1")
            output.append("M=0")
            output.append("(" + jump_label + ")")
        else:
            raise NameError("Unknown command")

        output.append("")

        for line in output:
            print(line, file=self.file)

    def write_push_pop(self, command: str, segment: str, index: int):
        output = []
        if command == "C_PUSH":
            if segment == "constant":
                output.append("@" + str(index))
                output.append("D=A")
                output.append("@SP")
                output.append("AM=M+1")
                output.append("A=A-1")
                output.append("M=D")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
                output.append("@" + str(index))
                output.append("D=A")
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
                    output.append(self.symbols[segment])
                    output.append("A=M")
                output.append("A=D+A")
                output.append("D=M")
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
                output.append("@SP")
                output.append("M=M+1")
            elif segment == "static":
                output.append("@" + self.file_name + "." + str(index))
                output.append("D=M")
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
                output.append("@SP")
                output.append("M=M+1")
            else:
                raise NameError("cannot push segment")
        elif command == "C_POP":
            if segment == "constant":
                raise NameError("cannot pop constant segment")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
                output.append("@" + str(index))
                output.append("D=A")
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
                    output.append(self.symbols[segment])
                    output.append("A=M")
                output.append("D=D+A")
                output.append("@R13")
                output.append("M=D")
                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
                output.append("@R13")
                output.append("A=M")
                output.append("M=D")
            elif segment == "static":
                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
                output.append("@" + self.file_name + "." + str(index))
                output.append("M=D")
            else:
                raise NameError("cannot pop this segment")
        else:
            raise NameError("unknown command")

        output.append("")

        for line in output:
            print(line, file=self.file)

    def close(self):
        self.file.close()


def main():

    if len(sys.argv) != 2 or sys.argv[1][-3:] != ".vm":
        print("Run from command line with .vm filename as args")
        print("like this: 'python " + os.path.basename(__file__) + " [file.vm]'")

        return

    input_file_name = sys.argv[1]
    output_file_name = sys.argv[1][:-3] + ".asm"

    parser = Parser(input_file_name)

    code_writer = CodeWriter(output_file_name)

    while parser.hasMoreCommands():
        parser.advance()
        code_writer.comment(parser.current_command)
        command_type = parser.commandType()
        if command_type == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())
        elif command_type in ["C_PUSH", "C_POP"]:
            argument1 = parser.arg1()
            argument2 = parser.arg2()
            code_writer.write_push_pop(command_type, argument1, argument2)
        else:
            raise NameError("Unsupported Command Type")

    code_writer.close()


if __name__ == "__main__":
    main()
