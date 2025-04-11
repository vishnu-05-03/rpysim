class ROB:
    def __init__(self, size, register_file, commit_width=1):
        self.size = size
        self.entries = [None] * size  # Circular buffer
        self.head = 0                 # Points to next commit
        self.tail = 0                 # Points to next free slot
        self.register_file = register_file
        self.commit_width = commit_width  # Maximum commits per cycle

    def add(self, instr_info):
        if (self.tail + 1) % self.size == self.head:
            return None  # ROB full
        rob_entry = {
            'instr': instr_info,
            'completed': False,
            'value': None
        }
        self.entries[self.tail] = rob_entry
        rob_index = self.tail
        self.tail = (self.tail + 1) % self.size
        return rob_index

    def commit(self):
        committed = 0
        for _ in range(self.commit_width):
            if self.entries[self.head] is None:
                break  # Nothing more to commit
            
            entry = self.entries[self.head]
            if not entry['completed']:
                break  # Not ready to commit
                
            op, *operands = entry['instr']
            if op in ['ADD', 'ADDI', 'LW']:
                rd = operands[0]
                self.register_file.write(rd, entry['value'])
            elif op == 'SW':
                rs1, rs2, imm = operands
                address = self.register_file.read(rs1) + imm
                self.register_file.memory.write_word(address, entry['value'])
            
            self.entries[self.head] = None
            self.head = (self.head + 1) % self.size
            committed += 1
        
        return committed > 0  # Return True if at least one instruction was committed

    def is_empty(self):
        return self.head == self.tail and self.entries[self.head] is None