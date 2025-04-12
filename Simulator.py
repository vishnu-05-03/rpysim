from OoOProcessor import OoOProcessor
from src.Memory import Memory

def main():
    
    # Example instructions in hex format
    instructions = [
        0x00100593,  
        0x00200613,
        0x00c586b3
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

if __name__ == "__main__":
    main()