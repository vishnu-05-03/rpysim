from OoOProcessor import OoOProcessor
from src.Memory import Memory

def main():
    
    # Example instructions in hex format
    instructions = [
        0x00000020,  
        0x00000001,  # ADD R1, R2, R3
        0x00000002,  # SUB R4, R5, R6
        0x00000003,  # AND R7, R8, R9
        0x00000010   # OR R10, R11, R12
    ]

    processor = OoOProcessor(instructions)

    # Check memory contents
    memory = processor.memory
    print(memory.dump_memory(0, 5))  # Dump first 5 words of memory
    print("Memory dump complete.")

    # Simulate a few cycles
    for _ in range(5):
        processor.tick()
        print(f'fetch buffer: {processor.fetch.fetch_buffer}')
        print(f"Cycle {processor.cycle}: PC={processor.fetch.pc}")
        processor.fetch.clear_buffer()

if __name__ == "__main__":
    main()