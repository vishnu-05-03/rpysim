class Execute:
    def __init__(self, memory, rat, rob, execute_width=4):
        self.memory = memory
        self.rat = rat
        self.rob = rob
        self.execute_width = execute_width  # Maximum instructions to execute per cycle

    def execute(self, rob_index):
        """
        Execute a single instruction identified by rob_index.
        Returns True if executed or already completed, False if stalled.
        """
        entry = self.rob.entries[rob_index]
        if entry['completed']:
            return True
        op, *operands = entry['instr']
        instr_packet = self.rob.entries[rob_index]['instr_packet']
        
        if op == 'ADD':
            rd, rs1, rs2 = operands
            val1 = self.get_operand_value(instr_packet.phys_rs1, rs1)
            val2 = self.get_operand_value(instr_packet.phys_rs2, rs2)
            if val1 is None or val2 is None:
                return False
            entry['value'] = val1 + val2
        elif op == 'ADDI':
            rd, rs1, imm = operands
            val1 = self.get_operand_value(instr_packet.phys_rs1, rs1)
            if val1 is None:
                return False
            entry['value'] = val1 + imm
        elif op == 'LW':
            rd, rs1, imm = operands
            val1 = self.get_operand_value(instr_packet.phys_rs1, rs1)
            if val1 is None:
                return False
            address = val1 + imm
            entry['value'] = self.memory.read_word(address)
        elif op == 'SW':
            rs1, rs2, imm = operands
            val1 = self.get_operand_value(instr_packet.phys_rs1, rs1)
            val2 = self.get_operand_value(instr_packet.phys_rs2, rs2)
            if val1 is None or val2 is None:
                return False
            entry['value'] = val2
            address = val1 + imm  # Address computed but not used until commit
            
        entry['completed'] = True
        return True
    
    def get_operand_value(self, phys_reg, arch_reg):
        """
        Retrieve the value of a register, checking renamed ROB entry or register file.
        """
        if arch_reg == 0:
            return 0
        if phys_reg is None:
            return self.rob.register_file.read(arch_reg)
        if self.rob.entries[phys_reg]['completed']:
            return self.rob.entries[phys_reg]['value']
        return None
    
    def tick(self, rob_indices):
        """
        Simulate one clock cycle of the execute stage.
        Processes up to execute_width instructions from rob_indices.
        
        Args:
            rob_indices: List of ROB indices from the decode stage or reservation stations
            
        Returns:
            List of ROB indices for instructions that completed execution
        """
        completed_indices = []
        instructions_to_process = min(self.execute_width, len(rob_indices))
        
        for i in range(instructions_to_process):
            rob_index = rob_indices[i]
            if self.execute(rob_index):
                completed_indices.append(rob_index)
            else:
                # Stop processing if an instruction stalls (dependency not ready)
                break
                
        return completed_indices