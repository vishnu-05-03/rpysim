class ROB:
    def __init__(self, size, register_file, commit_width=1):
        self.size = size
        self.entries = [None] * size
        self.head = 0
        self.tail = 0
        self.register_file = register_file
        self.commit_width = max(1, commit_width)  # Ensure at least 1

    def add(self, instr_info, phys_rd=None):
        if (self.tail + 1) % self.size == self.head:
            return None
        rob_entry = {
            'instr': instr_info,
            'completed': False,
            'value': None,
            'phys_rd': phys_rd
        }
        self.entries[self.tail] = rob_entry
        rob_index = self.tail
        self.tail = (self.tail + 1) % self.size
        return rob_index

    def commit(self):
        committed = 0
        for _ in range(self.commit_width):
            if self.entries[self.head] is None:
                break  # No more entries
            
            entry = self.entries[self.head]
            if not entry['completed']:
                break  # Not ready to commit
                
            # Extract destination register
            rd = None
            op = entry['instr'][0]
            if op in ['ADD', 'SUB', 'SLL', 'SLT', 'SLTU', 'XOR', 'SRL', 'SRA', 'OR', 'AND']:
                rd = entry['instr'][1]
            
            # Commit to RAT (updates arch reg, frees phys reg)
            self.register_file.rat.commit(rd, self.head)
            
            # Clear ROB entry
            self.entries[self.head] = None
            self.head = (self.head + 1) % self.size
            committed += 1
        
        return committed > 0

    def is_empty(self):
        return self.head == self.tail and self.entries[self.head] is None