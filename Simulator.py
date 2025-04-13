from OoOProcessor import OoOProcessor
from src.Memory import Memory

def main():
    
    # Example instructions in hex format
    # instructions = [
    #     0x002082b3,
    #     0x40418333,
    #     0x002093b3,
    #     0x0020a433,
    #     0x0020b4b3,
    #     0x0020c533,
    #     0x0020d5b3,
    #     0x4020d633,
    #     0x0020e6b3,
    #     0x0020f733,
    # ]
    instructions = [
        0x0c800793,
        0x00500813,
        0x0107a023,
        0x0007a883
    ]

    processor = OoOProcessor(instructions)

    # Check memory contents
    memory = processor.memory
    print(memory.dump_memory(0, 5))  # Dump first 5 words of memory
    print("Memory dump complete.")

    # Simulate a few cycles
    for _ in range(10):
        print('---------------------------------------- Cycle {} ----------------------------------'.format(processor.cycle))
        processor.tick()

if __name__ == "__main__":
    main()