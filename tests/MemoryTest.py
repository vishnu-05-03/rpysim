import sys
import os
import pytest

# Modify the import to use the full module path that matches the coverage target
# Add the parent directory to path so "src" becomes a package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.Memory import Memory

class TestMemory:
    def setup_method(self):
        # Reset the singleton for each test
        Memory._instance = None
        self.mem = Memory()
    
    def test_singleton(self):
        """Test that Memory is a singleton"""
        mem1 = Memory()
        mem2 = Memory()
        assert mem1 is mem2
    
    def test_initial_state(self):
        """Test that uninitialized memory returns zeros"""
        assert self.mem.read_word(0) == 0
        assert self.mem.read_word(4) == 0
        assert self.mem.read_halfword(2) == 0
        assert self.mem.read_byte(1) == 0

    def test_word_operations(self):
        """Test 32-bit word operations"""
        # Test positive value
        self.mem.write_word(0, 0x12345678)
        assert self.mem.read_word(0) == 0x12345678
        
        # Test negative value
        self.mem.write_word(4, 0xFFFFFFFF)  # -1 in two's complement
        assert self.mem.read_word(4) == 0xFFFFFFFF
        
        # Test value truncation
        self.mem.write_word(8, 0x123456789)  # Value exceeds 32 bits
        assert self.mem.read_word(8) == 0x23456789

    def test_halfword_operations(self):
        """Test 16-bit halfword operations"""
        # Test positive value
        self.mem.write_halfword(0, 0x1234)
        assert self.mem.read_halfword(0) == 0x1234
        assert self.mem.read_unsigned_halfword(0) == 0x1234
        
        # Test negative value (sign extension)
        self.mem.write_halfword(2, 0x8000)  # -32768 in two's complement
        assert self.mem.read_halfword(2) == 0xFFFF8000  # Sign extended
        assert self.mem.read_unsigned_halfword(2) == 0x8000  # Unsigned
        
        # Test value truncation
        self.mem.write_halfword(4, 0x12345)  # Value exceeds 16 bits
        assert self.mem.read_halfword(4) == 0x2345

    def test_byte_operations(self):
        """Test 8-bit byte operations"""
        # Test positive value
        self.mem.write_byte(0, 0x12)
        assert self.mem.read_byte(0) == 0x12
        assert self.mem.read_unsigned_byte(0) == 0x12
        
        # Test negative value (sign extension)
        self.mem.write_byte(1, 0x80)  # -128 in two's complement
        assert self.mem.read_byte(1) == 0xFFFFFF80  # Sign extended
        assert self.mem.read_unsigned_byte(1) == 0x80  # Unsigned
        
        # Test value truncation
        self.mem.write_byte(2, 0x123)  # Value exceeds 8 bits
        assert self.mem.read_byte(2) == 0x23

    def test_alignment_requirements(self):
        """Test alignment requirements for memory access"""
        # Word alignment
        with pytest.raises(ValueError):
            self.mem.read_word(1)
        with pytest.raises(ValueError):
            self.mem.write_word(1, 0x12345678)
            
        # Halfword alignment
        with pytest.raises(ValueError):
            self.mem.read_halfword(1)
        with pytest.raises(ValueError):
            self.mem.write_halfword(1, 0x1234)
            
        # Byte alignment (should always work)
        try:
            self.mem.read_byte(1)
            self.mem.write_byte(1, 0x12)
        except ValueError:
            pytest.fail("Byte operations raised an alignment exception")

    def test_load_program(self):
        """Test the program loading functionality"""
        program = [0x11223344, 0x55667788, 0x99AABBCC]
        self.mem.load_program(program, start_address=0x1000)
        
        assert self.mem.read_word(0x1000) == 0x11223344
        assert self.mem.read_word(0x1004) == 0x55667788
        assert self.mem.read_word(0x1008) == 0x99AABBCC

    def test_dump_memory(self):
        """Test memory dump functionality"""
        self.mem.write_word(0x100, 0x11223344)
        self.mem.write_word(0x104, 0x55667788)
        
        dump = self.mem.dump_memory(0x100, 2)
        assert dump == {0x100: 0x11223344, 0x104: 0x55667788}

    def test_memory_independence(self):
        """Test that memory writes don't affect adjacent cells"""
        self.mem.write_byte(0, 0xFF)
        assert self.mem.read_byte(0) == 0xFFFFFFFF  # Sign-extended
        assert self.mem.read_byte(1) == 0
        
        self.mem.write_halfword(2, 0xFFFF)
        assert self.mem.read_halfword(2) == 0xFFFFFFFF  # Sign-extended
        assert self.mem.read_byte(4) == 0
