from .Instruction import Instruction

class Decode:
    def __init__(self, rat, rob, lsq, branch_predictor):  # Add branch_predictor parameter
        self.rat = rat
        self.rob = rob
        self.lsq = lsq
        self.branch_predictor = branch_predictor  # Store reference to branch predictor
        self.decoded_instr_list = []

    def _decode_instr(self, instr_hex):
        """
        Decode the instruction and return its type and operands.
        This is a placeholder for the actual decoding logic.
        """
        instr_packet = Instruction()
        opcode = instr_hex & 0x7F

        if opcode == 0x13:
            instr_packet.instr_hardware = 'ALU'
            instr_packet.rd = (instr_hex >> 7) & 0x1F
            instr_packet.rs1 = (instr_hex >> 15) & 0x1F
            instr_packet.instr_format = 'I'
            funct3 = (instr_hex & 0x7000) >> 12
            if funct3 == 0x0:
                instr_packet.instr_id = 1  # addi
                instr_packet.imm = (instr_hex >> 20) & 0xFFF
            elif funct3 == 0x2:
                instr_packet.instr_id = 2 # slti
                instr_packet.shamt = (instr_hex >> 20) & 0x1F
            elif funct3 == 0x3:
                instr_packet.instr_id = 3 # sltiu
                instr_packet.shamt = (instr_hex >> 20) & 0x1F
            elif funct3 == 0x4:
                instr_packet.instr_id = 4 # xori
                instr_packet.imm = (instr_hex >> 20) & 0xFFF
            elif funct3 == 0x6:
                instr_packet.instr_id = 5 # ori
                instr_packet.imm = (instr_hex >> 20) & 0xFFF
            elif funct3 == 0x7:
                instr_packet.instr_id = 6 # andi
                instr_packet.imm = (instr_hex >> 20) & 0xFFF
            elif funct3 == 0x1:
                instr_packet.instr_id = 7 # slli
                instr_packet.shamt = (instr_hex >> 20) & 0x1F
            elif funct3 == 0x5:
                instr_packet.shamt = (instr_hex >> 20) & 0x1F
                if (instr_hex & 0xFE000000) == 0x40000000:
                    instr_packet.instr_id = 9 # srai
                elif (instr_hex & 0xFE000000) == 0x00000000:
                    instr_packet.instr_id = 8 # srli

        elif opcode == 0x33:
            instr_packet.instr_hardware = 'ALU'
            instr_packet.instr_format = 'R'
            instr_packet.rd = (instr_hex >> 7) & 0x1F
            instr_packet.rs1 = (instr_hex >> 15) & 0x1F
            instr_packet.rs2 = (instr_hex >> 20) & 0x1F
            funct3 = (instr_hex & 0x7000) >> 12
            funct7 = (instr_hex & 0xFE000000) >> 25
            if funct3 == 0x0:
                if funct7 == 0x00:
                    instr_packet.instr_id = 10 # add 
                elif funct7 == 0x20:
                    instr_packet.instr_id = 11 # sub
            elif funct3 == 0x1:
                instr_packet.instr_id = 12 # sll
            elif funct3 == 0x2:
                instr_packet.instr_id = 13 # slt
            elif funct3 == 0x3:
                instr_packet.instr_id = 14 # sltu
            elif funct3 == 0x4:
                instr_packet.instr_id = 15 # xor
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    instr_packet.instr_id = 16 # srl
                elif funct7 == 0x20:
                    instr_packet.instr_id = 17 # sra
            elif funct3 == 0x6:
                instr_packet.instr_id = 18 # or
            elif funct3 == 0x7:
                instr_packet.instr_id = 19 # and

        elif opcode == 0x03:
            instr_packet.instr_hardware = 'LOAD'
            instr_packet.instr_format = 'I'
            instr_packet.rd = (instr_hex >> 7) & 0x1F
            instr_packet.rs1 = (instr_hex >> 15) & 0x1F
            instr_packet.imm = (instr_hex >> 20) & 0xFFF
            funct3 = (instr_hex & 0x7000) >> 12
            if funct3 == 0x0:
                instr_packet.instr_id = 20 # lb
            elif funct3 == 0x1:
                instr_packet.instr_id = 21 # lh
            elif funct3 == 0x2:
                instr_packet.instr_id = 22 # lw
            elif funct3 == 0x4:
                instr_packet.instr_id = 23 # lbu
            elif funct3 == 0x5:
                instr_packet.instr_id = 24 # lhu

        elif opcode == 0x23:
            instr_packet.instr_hardware = 'STORE'
            instr_packet.instr_format = 'S'
            instr_packet.rs1 = (instr_hex >> 15) & 0x1F
            instr_packet.rs2 = (instr_hex >> 20) & 0x1F
            instr_packet.imm = ((instr_hex >> 7) & 0x1F) | (((instr_hex >> 25) & 0x7F) << 5)
            funct3 = (instr_hex & 0x7000) >> 12
            if funct3 == 0x0:
                instr_packet.instr_id = 25 # sb
            elif funct3 == 0x1:
                instr_packet.instr_id = 26 # sh
            elif funct3 == 0x2:
                instr_packet.instr_id = 27 # sw

        elif opcode == 0x63:
            instr_packet.instr_hardware = 'BRANCH'
            instr_packet.instr_format = 'B'
            instr_packet.rs1 = (instr_hex >> 15) & 0x1F
            instr_packet.rs2 = (instr_hex >> 20) & 0x1F
            instr_packet.imm = (
                (((instr_hex >> 31) & 0x1) << 12) |
                (((instr_hex >> 7) & 0x1) << 11) |
                (((instr_hex >> 25) & 0x3F) << 5) |
                (((instr_hex >> 8) & 0xF) << 1)
            )
            funct3 = (instr_hex & 0x7000) >> 12
            if funct3 == 0x0:
                instr_packet.instr_id = 28 # beq
            elif funct3 == 0x1:
                instr_packet.instr_id = 29 # bne
            elif funct3 == 0x4:
                instr_packet.instr_id = 30 # blt
            elif funct3 == 0x5:
                instr_packet.instr_id = 31 # bge
            elif funct3 == 0x6: 
                instr_packet.instr_id = 32 # bltu
            elif funct3 == 0x7:
                instr_packet.instr_id = 33 # bgeu

        else:
            raise ValueError(f"Unsupported opcode: {hex(opcode)}")
            
        return instr_packet

    def tick(self, fetch_buffer):
        if not fetch_buffer:
            return []
        
        if self.decoded_instr_list:
            return []
            
        rob_indices = []
        
        for instr_hex, pc in fetch_buffer:
            # Default sequential execution - will be overridden for branches if needed
            next_pc = pc + 4
            
            # Pre-check opcode to identify if this is a branch
            opcode = instr_hex & 0x7F
            if opcode == 0x63:  # Branch instruction
                # Extract branch immediate
                imm = (
                    (((instr_hex >> 31) & 0x1) << 12) |  # imm[12]
                    (((instr_hex >> 7) & 0x1) << 11) |   # imm[11]
                    (((instr_hex >> 25) & 0x3F) << 5) |  # imm[10:5]
                    (((instr_hex >> 8) & 0xF) << 1)      # imm[4:1|0]
                )
                # Sign extend
                if (imm & 0x1000):
                    imm |= 0xFFFFE000
                
                # Get branch prediction from branch predictor
                predicted_taken, predicted_target = self.branch_predictor.predict(pc)
                
                # If branch is predicted taken, use the calculated target
                if predicted_taken:
                    next_pc = pc + imm
                
                print(f"Branch at PC={hex(pc)}: imm={hex(imm)}, target={hex(pc+imm)}, predicted_taken={predicted_taken}, next_pc={hex(next_pc)}")
            
            # Allocate ROB entry with PC information (including branch prediction)
            rob_index = self.rob.add(None, curr_pc=pc, next_pc=next_pc)
            if rob_index is None:
                break
                
            try:
                instr_packet = self._decode_instr(instr_hex)
                instr_packet.rob_index = rob_index
                
                # Allocate physical register for destination
                phys_rd = None
                if instr_packet.rd is not None and instr_packet.rd != 0:
                    phys_rd = self.rat.allocate_phys_reg(rob_index)
                    if phys_rd is None:  # No free physical registers
                        self.rob.entries[rob_index] = None
                        self.rob.tail = (self.rob.tail - 1) % self.rob.size
                        break
                    self.rat.set_mapping(instr_packet.rd, phys_rd, rob_index)
                    
                # Handle memory operations with LSQ
                if instr_packet.instr_hardware == 'LOAD':
                    lsq_index = self.lsq.add_load(rob_index, instr_packet.rs1, instr_packet.imm)
                    if lsq_index is None:
                        if phys_rd is not None:
                            self.rat.free_phys_reg(phys_rd)
                        self.rob.entries[rob_index] = None
                        self.rob.tail = (self.rob.tail - 1) % self.rob.size
                        break
                        
                elif instr_packet.instr_hardware == 'STORE':
                    lsq_index = self.lsq.add_store(rob_index, instr_packet.rs1, instr_packet.rs2, instr_packet.imm)
                    if lsq_index is None:
                        if phys_rd is not None:
                            self.rat.free_phys_reg(phys_rd)
                        self.rob.entries[rob_index] = None
                        self.rob.tail = (self.rob.tail - 1) % self.rob.size
                        break
                        
                if instr_packet.instr_hardware == 'BRANCH':
                    instr_packet.address = pc
                    # For branches, store the immediate as potential branch target
                    # This will be used in the Execute unit
                    target_offset = instr_packet.imm if instr_packet.imm is not None else 0
                    # Correctly calculate and store the branch target
                    self.rob.entries[rob_index]['branch_target'] = pc + target_offset
                    # Store branch prediction information
                    instr_packet.predicted_taken = (next_pc != pc + 4)
                    instr_packet.predicted_target = next_pc
                
                # Store instruction info in ROB
                instr_info = self._create_instr_info(instr_packet)
                self.rob.entries[rob_index]['instr'] = instr_info
                self.rob.entries[rob_index]['phys_rd'] = phys_rd
                
                self.decoded_instr_list.append((instr_packet, rob_index))
                rob_indices.append(rob_index)
                
            except ValueError as e:
                print(f"Error decoding instruction at PC {hex(pc)}: {e}")
                self.rob.entries[rob_index] = None
                self.rob.tail = (self.rob.tail - 1) % self.rob.size
        
        return rob_indices

    def _create_instr_info(self, instr_packet):
        instr_name = None
        for id_val, name in Instruction.supported_instructions:
            if id_val == instr_packet.instr_id:
                instr_name = name.upper()
                break
        
        if instr_packet.instr_hardware == 'ALU' and instr_packet.instr_format == 'R':
            return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.rs2)
        elif instr_packet.instr_hardware == 'ALU' and instr_packet.instr_format == 'I':
            return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.imm)
        elif instr_packet.instr_hardware == 'LOAD':
            return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.imm)
        elif instr_packet.instr_hardware == 'STORE':
            return (instr_name, instr_packet.rs1, instr_packet.rs2, instr_packet.imm)
        elif instr_packet.instr_hardware == 'BRANCH':
            return (instr_name, instr_packet.rs1, instr_packet.rs2, instr_packet.imm)
        
        return (instr_name,)

    def clear_buffer(self):
        self.decoded_instr_list = []