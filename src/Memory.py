class Memory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Memory, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the memory"""
        self.memory = {}  # Using a dictionary for sparse memory representation
        self.word_size = 4  # 4 bytes (32 bits) for RV32I
    
    def read_word(self, address):
        """Read a 32-bit word from memory at the given address"""
        # Ensure address is word-aligned
        if address % self.word_size != 0:
            raise ValueError(f"Misaligned memory access at address {hex(address)}")
        
        # If the address hasn't been written to yet, return 0
        word = 0
        for i in range(self.word_size):
            byte = self.memory.get(address + i, 0)
            word |= byte << (8 * i)  # Little-endian
        
        return word
    
    def read_halfword(self, address):
        """Read a 16-bit halfword from memory at the given address"""
        if address % 2 != 0:
            raise ValueError(f"Misaligned halfword access at address {hex(address)}")
        
        halfword = 0
        for i in range(2):
            byte = self.memory.get(address + i, 0)
            halfword |= byte << (8 * i)  # Little-endian
        
        # Find MSB to do sign extension
        msb = (halfword >> 15) & 1
        
        # Sign-extend the halfword
        if msb:
            halfword |= 0xFFFF0000
        else:
            halfword &= 0xFFFF
        
        return halfword
    
    def read_unsigned_halfword(self, address):
        """Read a 16-bit unsigned halfword from memory at the given address"""
        if address % 2 != 0:
            raise ValueError(f"Misaligned halfword access at address {hex(address)}")
        
        halfword = 0
        for i in range(2):
            byte = self.memory.get(address + i, 0)
            halfword |= byte << (8 * i)
        
        return halfword & 0xFFFF  # Mask to ensure it's unsigned
    
    def read_byte(self, address):
        """Read a byte from memory at the given address"""
        byte = self.memory.get(address, 0)
        msb = (byte >> 7) & 1
        # Sign-extend the byte
        if msb:
            byte |= 0xFFFFFF00
        else:
            byte &= 0xFF

        return byte
    
    def read_unsigned_byte(self, address):
        """Read an unsigned byte from memory at the given address"""
        return self.memory.get(address, 0) & 0xFF
    
    def write_word(self, address, value):
        """Write a 32-bit word to memory at the given address"""
        # Ensure address is word-aligned
        if address % self.word_size != 0:
            raise ValueError(f"Misaligned memory access at address {hex(address)}")
        
        # Ensure value is 32-bit
        value &= 0xFFFFFFFF
        
        # Write the word to memory (little-endian)
        for i in range(self.word_size):
            self.memory[address + i] = (value >> (8 * i)) & 0xFF
    
    def write_halfword(self, address, value):
        """Write a 16-bit halfword to memory at the given address"""
        if address % 2 != 0:
            raise ValueError(f"Misaligned halfword access at address {hex(address)}")
        
        value &= 0xFFFF
        
        for i in range(2):
            self.memory[address + i] = (value >> (8 * i)) & 0xFF

    def write_byte(self, address, value):
        """Write a byte to memory at the given address"""
        self.memory[address] = value & 0xFF
    
    def load_program(self, program, start_address=0):
        """
        Load a program into memory
        program: list of 32-bit instructions
        start_address: memory address to start loading program
        """
        address = start_address
        for instruction in program:
            self.write_word(address, instruction)
            address += self.word_size
    
    def dump_memory(self, start_address, num_words):
        """Dump memory contents for debugging"""
        result = {}
        for i in range(num_words):
            addr = start_address + i * self.word_size
            result[addr] = self.read_word(addr)
        return result