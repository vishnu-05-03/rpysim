# rpysim
A RISC-V Out-of-Order Python Simulator

## Overview
rpysim is a cycle-accurate, out-of-order RISC-V processor simulator implemented in Python. It models a modern processor pipeline with speculative execution, branch prediction, and register renaming. The simulator is designed for educational purposes to help understand the complexities of modern CPU microarchitecture.

## Features
- Out-of-Order execution with Register Renaming
- Branch Prediction (2-bit saturating counter)
- Load-Store Queue (LSQ) for memory operations
- Reorder Buffer (ROB) for in-order instruction retirement
- Register Alias Table (RAT) for register renaming
- Support for RV32I base instruction set
- Cycle-accurate simulation
- Speculative execution with branch misprediction recovery

## Architecture Overview

The simulator implements the following components:

- **Memory**: Simulates main memory with word, halfword, and byte access. Memory is implemented as a sparse dictionary for efficient storage, supporting aligned and unaligned accesses with proper sign extension for loads. The memory subsystem handles program loading and provides an interface for reading/writing at byte, halfword, and word granularity.

- **RegisterFile**: Models the architectural register file (32 registers) and physical register file (64 registers) with register renaming support. The architectural registers represent the programmer-visible state, while physical registers enable out-of-order execution by removing false dependencies. Register x0 is hardwired to zero as per the RISC-V specification.

- **ROB (Reorder Buffer)**: Tracks in-flight instructions and ensures proper in-order commit despite out-of-order execution. Each ROB entry contains instruction information, completion status, result value, exception flags, and PC values. The ROB maintains program order by committing instructions from the head while new instructions are inserted at the tail.

- **RAT (Register Alias Table)**: Handles register renaming for out-of-order execution by mapping architectural registers to physical registers. It maintains mappings between architectural and physical registers, manages a free list of physical registers, and tracks previous mappings to enable precise state recovery during branch mispredictions.

- **LSQ (Load-Store Queue)**: Manages memory operations and enables memory disambiguation. The LSQ enforces memory ordering constraints, allowing loads to execute speculatively while ensuring stores commit in program order. It supports memory forwarding for load-after-store dependencies and maintains program order for memory operations.

- **BranchPredictor**: Predicts branch outcomes to enable speculative execution. Implements a 2-bit saturating counter pattern prediction scheme that adapts to branch behavior over time. The predictor maintains a prediction table indexed by PC bits and updates prediction counters based on actual branch outcomes.

- **Fetch**: Retrieves instructions from memory according to the current program counter (PC) and branch predictions. It maintains a fetch buffer, handles prediction-based target addressing, and serves as the first stage of the pipeline. During branch mispredictions, the fetch unit is redirected to the correct path.

- **Decode**: Decodes machine code into internal instruction representation, identifying instruction type, source/destination registers, and immediate values. It handles register renaming by allocating physical registers for destination registers and prepares instructions for execution by setting up ROB entries.

- **Execute**: Simulates instruction execution based on the operation type (ALU, branch, load/store). For ALU operations, it computes results and writes them to physical registers. For branches, it resolves branch conditions and handles mispredictions. For loads/stores, it calculates effective addresses and interfaces with the LSQ.

The processor pipeline consists of these stages:
1. **Fetch**: Instructions are fetched from memory
2. **Decode**: Instructions are decoded and register renaming occurs
3. **Issue/Execute**: Instructions execute when operands are ready
4. **Commit**: Instructions commit in-order via the ROB

## Installation

### Prerequisites
- Python 3.6 or later

### Setup
```bash
git clone https://github.com/your-username/rpysim.git
cd rpysim
```

## Usage

### Basic Simulation
```python
from OoOProcessor import OoOProcessor

# Example program (RISC-V machine code)
instructions = [
    0x00208663,  # beq x1, x2, 12 (branch to PC+12 if x1 == x2)
    0x005201b3,  # add x3, x4, x5  (wrong path)
    0x40838333,  # sub x6, x7, x8  (wrong path)
    0x00b564b3,  # or x9, x10, x11 (correct path - branch target)
    0x00e6f633   # and x12, x13, x14 (correct path)
]

# Create and run processor
processor = OoOProcessor(instructions)
for _ in range(10):  # Run for 10 cycles
    processor.tick()
```

### Branch Prediction Testing
```bash
python3 branch_test.py
```

### Running the Simulator
```bash
python3 Simulator.py
```

## Testing

The project includes comprehensive tests that verify the functionality of individual components.

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run a specific test
make test-single TEST=MemoryTest
```

## Project Structure
```
rpysim/
├── components/
│   ├── BranchPredictor.py
│   ├── LSQ.py
│   ├── Memory.py
│   ├── RAT.py
│   ├── RegisterFile.py
│   └── ROB.py
├── OoOProcessor.py
├── Simulator.py
├── branch_test.py
└── tests/
    ├── BranchPredictorTest.py
    ├── LSQTest.py
    └── MemoryTest.py
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.