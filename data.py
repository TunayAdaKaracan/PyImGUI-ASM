from dataclasses import dataclass

@dataclass
class Instuction:
    name: str
    value: bytes

@dataclass
class Program:
    id: int
    name: str
    force: bool
    data: str
    selected: bool


class GuiDataHolder:
    def __init__(self):
        self.instructions = []
        self.programs = []
        self.temp = {}
        self.selected_instruction = 0
        self.edit_instruction = False

    
    def add_instruction(self, instruction: Instuction):
        self.instructions.append(instruction)

    def replace_instruction(self, index, instruction: Instuction):
        self.instructions[index] = instruction

    def add_program(self, program: Program):
        self.programs.append(program)

    def get_selected_program(self):
        for program in self.programs:
            if program.selected:
                return program