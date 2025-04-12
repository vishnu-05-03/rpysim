from OoOProcessor import OoOProcessor
from src.Memory import Memory

def main():
    
    # Example instructions in hex format
    instructions = [
        0x002082b3,
        0x40418333,
        0x002093b3,
        0x0020a433,
        0x0020b4b3,
        0x0020c533,
        0x0020d5b3,
        0x4020d633,
        0x0020e6b3,
        0x0020f733,
    ]

    processor = OoOProcessor(instructions)

    # Check memory contents
    memory = processor.memory
    print(memory.dump_memory(0, 5))  # Dump first 5 words of memory
    print("Memory dump complete.")

    # Simulate a few cycles
    for _ in range(10):
        processor.tick()
        print(f'fetch buffer: {processor.fetch.fetch_buffer}')
        print(f"Cycle {processor.cycle}: PC={processor.fetch.pc}")
        # processor.print_rat()  # Use processor's method instead of accessing rat directly
        # processor.print_rob()  # Use processor's method instead of accessing rob directly

if __name__ == "__main__":
    main()