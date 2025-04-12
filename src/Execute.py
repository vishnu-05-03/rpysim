class Execute:
    def __init__(self, memory, rat, rob):
        self.memory = memory
        self.rat = rat
        self.rob = rob

    def execute(self, rob_index):
        entry = self.rob.entries[rob_index]
        if entry['completed']:
            return True
        op, rd, rs1, rs2 = entry['instr']
        
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