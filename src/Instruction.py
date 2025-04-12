class Instruction:
    # Supported instructions with unique integer IDs
    supported_instructions = (
        # Integer Register-Immediate Instructions
        (1, 'addi'), (2, 'slti'), (3, 'sltiu'), (4, 'xori'), (5, 'ori'), (6, 'andi'), (7, 'slli'), (8, 'srli'), (9, 'srai'),

        # Integer Register-Register Instructions
        (10, 'add'), (11, 'sub'), (12, 'sll'), (13, 'slt'), (14, 'sltu'), (15, 'xor'), (16, 'srl'), (17, 'sra'), (18, 'or'), (19, 'and'),

        # Integer Load/Store Instructions
        (20, 'lb'), (21, 'lh'), (22, 'lw'), (23, 'lbu'), (24, 'lhu'), (25, 'sb'), (26, 'sh'), (27, 'sw'),

        # Integer Control Transfer Instructions
        (28, 'beq'), (29, 'bne'), (30, 'blt'), (31, 'bge'), (32, 'bltu'), (33, 'bgeu')
    )

    supported_instruction_types = (
        'ALU', 'LOAD', 'STORE', 'BRANCH'
    )

    def __init__(self):
        # Instruction Identification
        self.instr_id = None        # e.g., 'ADD', 'ADDI', 'LW', 'BEQ'
        self.instr_hardware = None      # e.g., 'ALU', 'LOAD', 'STORE', 'BRANCH'
        self.instr_format = None        # e.g., 'R', 'I', 'S', 'B'

        # Operands
        self.rs1 = None             # Source register 1 index (0-31) or None
        self.rs2 = None             # Source register 2 index (0-31) or None
        self.imm = None             # Sign-extended immediate or None
        self.shamt = None           # shamt for shift instructions
        self.rd = None              # Destination register index (0-31) or None
        self.address = None         # Memory address for load/store instructions

        # Control Information
        self.operation = None       # e.g., 'ADD', 'SUB', 'SLL', 'BEQ'
        self.mem_size = None        # For loads/stores: 'BYTE', 'HALF', 'WORD'
        self.is_signed = True       # For loads: True (lb, lh, lw) or False (lbu, lhu)
        self.is_branch = False      # True for branch instructions
        self.is_conditional = False # True for conditional branches (beq, bne, etc.)

        # OoO Metadata
        self.reads_rs1 = False      # True if rs1 is read
        self.reads_rs2 = False      # True if rs2 is read
        self.writes_rd = False      # True if rd is written
        self.rob_index = None       # ROB entry index
        self.predicted_taken = False # For branches: predicted outcome
        self.predicted_target = None # For branches: predicted target PC
        self.phys_rd = None         # Physical register index for destination