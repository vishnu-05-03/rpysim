from OoOProcessor import OoOProcessor

def main():
    # RISC-V instructions in machine code
    instructions = [
        0x00208663,  # beq x1, x2, 12 (branch to PC+12 if x1 == x2)
        0x005201b3,  # add x3, x4, x5  (wrong path)
        0x40838333,  # sub x6, x7, x8  (wrong path)
        0x00b564b3,  # or x9, x10, x11 (correct path - branch target)
        0x00e6f633   # and x12, x13, x14 (correct path)
    ]

    # Create processor and initialize key registers to ensure branch is taken
    processor = OoOProcessor(instructions)
    processor.register_file.write_arch(1, 10)  # x1 = 10
    processor.register_file.write_arch(2, 10)  # x2 = 10 (same as x1, branch will be taken)
    
    # Initialize other registers with some values
    processor.register_file.write_arch(4, 40)  # x4 = 40
    processor.register_file.write_arch(5, 50)  # x5 = 50
    processor.register_file.write_arch(10, 100) # x10 = 100
    processor.register_file.write_arch(11, 200) # x11 = 200
    
    # Force branch predictor to always predict "not taken" for this test
    processor.branch_predictor.table = [0] * processor.branch_predictor.mask
    
    # Simulate for several cycles
    print("Starting branch misprediction test...")
    print("Registers: x1=10, x2=10 (branch will be taken)")
    print("Branch predictor set to predict 'not taken'")
    print("Expected: branch at PC=0 will be mispredicted, pipeline flushed, resume at PC=12")
    print("\n" + "-" * 60)
    
    for i in range(10):
        print(f"\nRunning cycle {i+1}:")
        processor.tick()
        # Print key register values
        if i == 9:  # Final cycle
            print("\nFinal register values:")
            print(f"x3 = {processor.register_file.read_arch(3)}")  # Should be 0 if wrong path not committed
            print(f"x6 = {processor.register_file.read_arch(6)}")  # Should be 0 if wrong path not committed
            print(f"x9 = {processor.register_file.read_arch(9)}")  # Should be 300 if correct path executed
            print(f"x12 = {processor.register_file.read_arch(12)}") # Should be non-zero if correct path executed

if __name__ == "__main__":
    main()
