class RAT:
    def __init__(self, rob):
        self.rat = [None] * 32  # Maps architectural reg to ROB index or None
        self.rob = rob          # Reference to ROB for value lookup
        self.rob.rat = self     # Ensure ROB can access RAT for commit

    def set_multiple_mappings(self, mappings):
        """
        Update RAT with multiple register-to-ROB-index mappings in program order.
        
        Args:
            mappings: List of (reg_num, rob_index) tuples
        """
        for reg_num, rob_index in mappings:
            if reg_num != 0:  # x0 is not renamed
                self.rat[reg_num] = rob_index

    def get_value(self, reg_num):
        """
        Get value or ROB index for operand.
        """
        if reg_num == 0:
            return 0
        rob_index = self.rat[reg_num]
        if rob_index is None:
            return self.rob.register_file.read(reg_num)
        elif self.rob.entries[rob_index]['completed']:
            return self.rob.entries[rob_index]['value']
        return None

    def commit(self, reg_num, rob_index):
        """
        Clear mapping when instruction commits.
        """
        if self.rat[reg_num] == rob_index:
            self.rat[reg_num] = None
            
    def print_rat_table(self):
        """
        Print the Register Alias Table as a formatted table for debugging.
        Shows architectural registers and their mappings to ROB entries.
        """
        print("\n===== REGISTER ALIAS TABLE =====")
        print("-" * 60)
        print("| {:^10} | {:^15} | {:^12} | {:^12} |".format(
            "Arch Reg", "ROB Index", "Completed", "Value"))
        print("-" * 60)
        
        for i in range(32):
            reg_name = f"x{i}"
            if i == 0:
                reg_name += " (zero)"
            elif i == 1:
                reg_name += " (ra)"
            elif i == 2:
                reg_name += " (sp)"
            
            rob_index = self.rat[i]
            if rob_index is not None:
                completed = "Yes" if self.rob.entries[rob_index]['completed'] else "No"
                value = str(self.rob.entries[rob_index]['value']) if self.rob.entries[rob_index]['completed'] else "N/A"
            else:
                # No renaming, show actual register value
                completed = "-"
                value = str(self.rob.register_file.read(i))
                rob_index = "-"
                
            print("| {:^10} | {:^15} | {:^12} | {:^12} |".format(
                reg_name, str(rob_index), completed, value))
        
        print("-" * 60)