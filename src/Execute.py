class Execute:
    def __init__(self, memory, rat, rob, branch_predictor):
        self.memory = memory
        self.rat = rat
        self.rob = rob
        self.branch_predictor = branch_predictor

    def execute(self, rob_index):
        entry = self.rob.entries[rob_index]
        if entry['completed']:
            return True
            
        # Handle ALU instructions
        if len(entry['instr']) >= 2:  # ALU instructions have at least 2 elements
            op = entry['instr'][0]
            
            # Handle branch instructions
            if op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
                return self._execute_branch(entry)
                
            # Handle regular ALU operations
            rd, rs1, rs2 = entry['instr'][1:4]
            
            val1 = self.rat.get_value(rs1)
            val2 = self.rat.get_value(rs2)
            if val1 is None or val2 is None:
                return False
                
            if op == 'ADD':
                result = val1 + val2
            elif op == 'SUB':
                result = val1 - val2
            elif op == 'SLL':
                result = val1 << (val2 & 0x1F)  # Lower 5 bits of val2
            elif op == 'SLT':
                result = 1 if val1 < val2 else 0  # Signed comparison
            elif op == 'SLTU':
                result = 1 if (val1 & 0xFFFFFFFF) < (val2 & 0xFFFFFFFF) else 0  # Unsigned
            elif op == 'XOR':
                result = val1 ^ val2
            elif op == 'SRL':
                result = (val1 & 0xFFFFFFFF) >> (val2 & 0x1F)  # Logical right shift
            elif op == 'SRA':
                result = val1 >> (val2 & 0x1F)  # Arithmetic right shift
            elif op == 'OR':
                result = val1 | val2
            elif op == 'AND':
                result = val1 & val2
            else:
                return False

            entry['value'] = result & 0xFFFFFFFF  # Ensure 32-bit result
            if entry['phys_rd'] is not None:
                self.rob.register_file.write_phys(entry['phys_rd'], result)
            entry['completed'] = True
            return True
        return False

    def _execute_branch(self, entry):
        op = entry['instr'][0]
        
        # Branch instructions have the format (op_name, rs1, rs2, imm)
        if len(entry['instr']) < 4:
            print(f"Malformed branch instruction: {entry['instr']}")
            return False
        
        # Correctly parse branch instruction tuple    
        _, rs1, rs2, imm = entry['instr']
        
        val1 = self.rat.get_value(rs1)
        val2 = self.rat.get_value(rs2)
        if val1 is None or val2 is None:
            return False
        
        # Debug output to verify register values
        print(f"Evaluating {op}: x{rs1}={val1} vs x{rs2}={val2}")
        
        # Evaluate branch condition and determine branch outcome
        taken = False
        if op == 'BEQ':
            taken = val1 == val2
        elif op == 'BNE':
            taken = val1 != val2
        elif op == 'BLT':
            taken = val1 < val2  # Signed comparison
        elif op == 'BGE':
            taken = val1 >= val2  # Signed comparison
        elif op == 'BLTU':
            taken = (val1 & 0xFFFFFFFF) < (val2 & 0xFFFFFFFF)  # Unsigned
        elif op == 'BGEU':
            taken = (val1 & 0xFFFFFFFF) >= (val2 & 0xFFFFFFFF)  # Unsigned
            
        # Calculate actual next PC based on branch outcome
        if taken:
            # If branch is taken, use the branch target
            actual_next_pc = entry['branch_target']
            
            # Update debug message to show register values correctly
            print(f"Branch TAKEN: {op} x{rs1}={val1}, x{rs2}={val2}")
            print(f"branch_target = {hex(entry['branch_target'])}")
        else:
            actual_next_pc = entry['curr_pc'] + 4
            print(f"Branch NOT TAKEN: {op} x{rs1}={val1}, x{rs2}={val2}")
        
        # Check if branch was mispredicted by comparing predicted vs. actual next PC
        predicted_next_pc = entry['next_pc']  # This is already predicted next PC
        
        # Always update next_pc field based on actual branch outcome 
        entry['next_pc'] = actual_next_pc
        
        if predicted_next_pc != actual_next_pc:
            # Branch was mispredicted
            entry['exception'] = True  # Set exception bit
            print(f"Branch misprediction detected! PC={hex(entry['curr_pc'])}, "
                  f"Predicted: {hex(predicted_next_pc)}, Actual: {hex(actual_next_pc)}")
        else:
            print(f"Branch correctly predicted at PC={hex(entry['curr_pc'])}")
        
        # Additional debug output to verify our decisions
        print(f"Branch outcome: taken={taken}, exception={entry['exception']}")
        
        # Store branch outcome
        entry['branch_taken'] = taken
        entry['value'] = 1 if taken else 0  # For consistency, store branch outcome in value
        entry['completed'] = True

        # Update branch predictor
        actual_target = entry['branch_target'] if taken else entry['curr_pc'] + 4
        self.branch_predictor.update(entry['curr_pc'], taken, actual_target)

        return True