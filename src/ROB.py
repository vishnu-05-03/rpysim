class ROB:
    def __init__(self, size, register_file, commit_width=4):
        self.size = size
        self.entries = [None] * size  # Circular buffer
        self.head = 0                 # Points to next commit
        self.tail = 0                 # Points to next free slot
        self.register_file = register_file
        self.commit_width = commit_width  # Maximum commits per cycle

    def allocate_multiple(self, instr_packets, count):
        """
        Allocate up to 'count' ROB entries for instructions.
        
        Args:
            instr_packets: List of Instruction objects or None
            count: Number of entries to allocate (e.g., decode_width)
            
        Returns:
            List of allocated ROB indices, or empty list if insufficient space
        """
        # Check available space
        available = self.size - ((self.tail - self.head) % self.size)
        if available < count:
            return []  # Not enough space
        
        rob_indices = []
        for i in range(count):
            rob_entry = {
                'instr': None,  # Set later in Decode
                'instr_packet': instr_packets[i] if i < len(instr_packets) else None,
                'completed': False,
                'value': None
            }
            self.entries[self.tail] = rob_entry
            rob_indices.append(self.tail)
            self.tail = (self.tail + 1) % self.size
            
        return rob_indices

    def commit(self):
        """
        Commit up to commit_width completed instructions.
        
        Returns:
            True if at least one instruction was committed, False otherwise
        """
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
                self.rat.commit(rd, self.head)  # Clear RAT mapping
            elif op == 'SW':
                # SW commits via LSQ, no register update needed here
                pass
            
            self.entries[self.head] = None
            self.head = (self.head + 1) % self.size
            committed += 1
        
        return committed > 0

    def is_empty(self):
        """
        Check if ROB is empty.
        """
        return self.head == self.tail and self.entries[self.head] is None
        
    def print_rob_table(self):
        """
        Print the ROB contents as a formatted table for debugging.
        Displays index, instruction info, completion status, and value.
        """
        print("\n===== ROB CONTENTS =====")
        print(f"Head: {self.head}, Tail: {self.tail}, Size: {self.size}")
        print("-" * 80)
        print("| {:^5} | {:^8} | {:^40} | {:^10} | {:^12} |".format(
            "Index", "Status", "Instruction", "Completed", "Value"))
        print("-" * 80)
        
        for i in range(self.size):
            entry = self.entries[i]
            if entry is not None:
                instr_str = str(entry['instr']) if entry['instr'] else "None"
                status = "HEAD" if i == self.head else "TAIL" if i == self.tail else ""
                if i == self.head and i == self.tail:
                    status = "H & T"
                    
                print("| {:^5} | {:^8} | {:<40} | {:^10} | {:^12} |".format(
                    i, status, instr_str, 
                    "Yes" if entry['completed'] else "No",
                    str(entry['value']) if entry['value'] is not None else "None"))
            else:
                status = "HEAD" if i == self.head else "TAIL" if i == self.tail else ""
                if i == self.head and i == self.tail:
                    status = "H & T"
                print("| {:^5} | {:^8} | {:<40} | {:^10} | {:^12} |".format(
                    i, status, "Empty", "-", "-"))
        
        print("-" * 80)