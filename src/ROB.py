class ROB:
    def __init__(self, size, register_file, commit_width=1):
        self.size = size
        self.entries = [None] * size
        self.head = 0
        self.tail = 0
        self.register_file = register_file
        self.commit_width = commit_width

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
                break
            
            entry = self.entries[self.head]
            if not entry['completed']:
                break
                
            op, rd, _, _ = entry['instr']
            self.register_file.rat.commit(rd, self.head)
            
            self.entries[self.head] = None
            self.head = (self.head + 1) % self.size
            committed += 1
        
        return committed > 0

    def print_table(self):
        """Print ROB contents as a table for debugging"""
        print("\n=== Reorder Buffer (ROB) ===")
        print(f"Head: {self.head}, Tail: {self.tail}")
        print("Index | Completed | Value      | Phys Reg | Instruction")
        print("-" * 60)
        
        for i in range(self.size):
            entry = self.entries[i]
            if entry is None:
                status = "Empty"
                completed = "-"
                value = "-"
                phys_reg = "-"
                instr = "-"
            else:
                status = "→" if i == self.head else " "
                status += "←" if i == self.tail else " "
                completed = "Yes" if entry['completed'] else "No"
                value = f"0x{entry['value']:08x}" if entry['value'] is not None else "-"
                phys_reg = f"p{entry['phys_rd']}" if entry['phys_rd'] is not None else "-"
                instr = str(entry['instr']) if entry['instr'] is not None else "-"
            
            print(f"{i:2} {status} | {completed:9} | {value:10} | {phys_reg:8} | {instr}")
        
        print("=" * 60)
        
    def is_empty(self):
        return self.head == self.tail and self.entries[self.head] is None