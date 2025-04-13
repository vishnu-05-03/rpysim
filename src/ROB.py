class ROB:
    def __init__(self, size, register_file, commit_width=1):
        self.size = size
        self.entries = [None] * size
        self.head = 0
        self.tail = 0
        self.register_file = register_file
        self.commit_width = max(1, commit_width)  # Ensure at least 1
        self.last_committed_next_pc = 0  # Track last committed instruction's next PC

    def add(self, instr_info, phys_rd=None, curr_pc=None, next_pc=None):
        if (self.tail + 1) % self.size == self.head:
            return None
        rob_entry = {
            'instr': instr_info,
            'completed': False,
            'value': None,
            'phys_rd': phys_rd,
            'curr_pc': curr_pc,
            'next_pc': next_pc,
            'branch_target': None,
            'branch_taken': False,
            'exception': False  # Add exception bit for branch mispredictions
        }
        self.entries[self.tail] = rob_entry
        rob_index = self.tail
        self.tail = (self.tail + 1) % self.size
        return rob_index

    def commit(self):
        for _ in range(self.commit_width):
            if self.entries[self.head] is None:
                break  # No more entries
            
            entry = self.entries[self.head]
            if not entry['completed']:
                break  # Not ready to commit
            
            # Check if this instruction has an exception
            if entry['exception']:
                # Return flush signal with the correct next PC
                return {
                    'flush': True,
                    'next_pc': entry['next_pc']
                }
                
            # Extract destination register
            rd = None
            op = entry['instr'][0]
            if op in ['ADD', 'SUB', 'SLL', 'SLT', 'SLTU', 'XOR', 'SRL', 'SRA', 'OR', 'AND', 'ADDI', 'SLTI', 'SLTIU', 'XORI', 'ORI', 'ANDI', 'SLLI', 'SRLI', 'SRAI', 'LB', 'LH', 'LW', 'LBU', 'LHU']:
                rd = entry['instr'][1]
            
            # Commit to RAT (updates arch reg, frees phys reg)
            self.register_file.rat.commit(rd, self.head)
            
            # Update last committed next PC
            self.last_committed_next_pc = entry['next_pc']
            
            # Clear ROB entry
            self.entries[self.head] = None
            self.head = (self.head + 1) % self.size
        
        # Return normal completion signal
        return {'flush': False, 'committed': True}

    def is_empty(self):
        return self.head == self.tail and self.entries[self.head] is None