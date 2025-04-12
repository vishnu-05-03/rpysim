from .Instruction import Instruction

class Decode:
    def __init__(self, rat, rob, lsq, decode_width=2):
        self.rat = rat    # Register Alias Table for renaming
        self.rob = rob    # Reorder Buffer for in-order commit
        self.lsq = lsq    # Load/Store Queue for memory ops
        self.decoded_instr_list = []  # Holds decoded instruction for Execute
        self.decode_width = decode_width  # Maximum instructions to decode per cycle

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
            funct3 = instr_hex & 0x7000
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
            funct3 = instr_hex & 0x7000
            funct7 = instr_hex & 0xFE000000
            if funct3 == 0x0:
                if funct7 == 0x00000000:
                    instr_packet.instr_id = 10 # add 
                elif funct7 == 0x40000000:
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
                if funct7 == 0x00000000:
                    instr_packet.instr_id = 16 # srl
                elif funct7 == 0x40000000:
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
            funct3 = instr_hex & 0x7000
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
            funct3 = instr_hex & 0x7000
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
            funct3 = instr_hex & 0x7000
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
        """
        Simulate one clock cycle of the decode stage.
        Processes up to decode_width instructions from fetch_buffer.
        
        Args:
            fetch_buffer: List of (instruction_hex, pc) tuples from Fetch stage
            
        Returns:
            List of ROB indices for successfully decoded instructions
        """
        if not fetch_buffer:  # No instructions to decode
            return []
        
        # Check if we're still waiting for Execute to consume previous instructions
        if self.decoded_instr_list:
            return []
            
        instructions_to_process = min(self.decode_width, len(fetch_buffer))
        instr_packets = []
        mappings = []
        rob_indices = []
        
        # Decode instructions first to ensure we have packets
        for i in range(instructions_to_process):
            instr_hex, pc = fetch_buffer[i]
            try:
                instr_packet = self._decode_instr(instr_hex)
                instr_packets.append(instr_packet)
            except ValueError as e:
                print(f"Error decoding instruction at PC {hex(pc)}: {e}")
                return []  # Stop if any instruction fails
        
        # Allocate ROB entries
        rob_indices = self.rob.allocate_multiple(instr_packets, instructions_to_process)
        if not rob_indices:  # ROB full
            return []
        
        # Process each instruction
        for i, (instr_hex, pc) in enumerate(fetch_buffer[:instructions_to_process]):
            instr_packet = instr_packets[i]
            rob_index = rob_indices[i]
            instr_packet.rob_index = rob_index
            
            # Rename source registers
            instr_packet.phys_rs1 = self.rat.rat[instr_packet.rs1] if instr_packet.rs1 is not None else None
            instr_packet.phys_rs2 = self.rat.rat[instr_packet.rs2] if instr_packet.rs2 is not None else None
            
            # Collect destination register mapping
            if instr_packet.rd is not None and instr_packet.rd != 0:
                mappings.append((instr_packet.rd, rob_index))
                
            # Handle memory operations with LSQ
            if instr_packet.instr_hardware == 'LOAD':
                lsq_index = self.lsq.add_load(rob_index, instr_packet.rs1, instr_packet.imm)
                if lsq_index is None:
                    # Undo ROB allocations
                    for j in range(i + 1):
                        self.rob.entries[rob_indices[j]] = None
                    self.rob.tail = (self.rob.tail - i - 1) % self.rob.size
                    return []
                    
            elif instr_packet.instr_hardware == 'STORE':
                lsq_index = self.lsq.add_store(rob_index, instr_packet.rs1, instr_packet.rs2, instr_packet.imm)
                if lsq_index is None:
                    for j in range(i + 1):
                        self.rob.entries[rob_indices[j]] = None
                    self.rob.tail = (self.rob.tail - i - 1) % self.rob.size
                    return []
                    
            # For branch instructions
            if instr_packet.instr_hardware == 'BRANCH':
                instr_packet.address = pc
                
            # Store instruction info in ROB
            instr_info = self._create_instr_info(instr_packet)
            self.rob.entries[rob_index]['instr'] = instr_info
            
            # Add to decoded instructions list
            self.decoded_instr_list.append((instr_packet, rob_index))
        
        # Update RAT with all mappings
        self.rat.set_multiple_mappings(mappings)
        
        # Remove processed instructions from fetch_buffer
        del fetch_buffer[:instructions_to_process]
        
        return rob_indices

    def _create_instr_info(self, instr_packet):
        """
        Create instruction info tuple from Instruction object for the ROB
        """
        # Find instruction name from ID
        instr_name = None
        for id_val, name in Instruction.supported_instructions:
            if id_val == instr_packet.instr_id:
                instr_name = name.upper()
                break
        
        if instr_packet.instr_hardware == 'ALU':
            if instr_packet.instr_format == 'I':  # Immediate instruction
                return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.imm or instr_packet.shamt)
            elif instr_packet.instr_format == 'R':  # Register-register instruction
                return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.rs2)
        elif instr_packet.instr_hardware == 'LOAD':
            return (instr_name, instr_packet.rd, instr_packet.rs1, instr_packet.imm)
        elif instr_packet.instr_hardware == 'STORE':
            return (instr_name, instr_packet.rs1, instr_packet.rs2, instr_packet.imm)
        elif instr_packet.instr_hardware == 'BRANCH':
            return (instr_name, instr_packet.rs1, instr_packet.rs2, instr_packet.imm, instr_packet.address)
        
        return (instr_name,)

    def clear_buffer(self):
        """Clear decoded instruction buffer after Execute consumes it."""
        self.decoded_instr_list = []