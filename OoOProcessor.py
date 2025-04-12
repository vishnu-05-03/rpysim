from src.Memory import Memory
from src.RegisterFile import RegisterFile
from src.Fetch import Fetch
from src.BranchPredictor import BranchPredictor
from src.ROB import ROB
from src.RAT import RAT
from src.LSQ import LSQ
from src.Decode import Decode
from src.Execute import Execute

class OoOProcessor:
    def __init__(self, program, fetch_width=2, decode_width=2, execute_width=2, commit_width=2, rob_size=8, lsq_size=8):
        # Initialize core components
        self.memory = Memory()
        self.register_file = RegisterFile()
        self.rob = ROB(size=rob_size, register_file=self.register_file, commit_width=commit_width)
        self.rat = RAT(self.rob)
        self.lsq = LSQ(self.memory, size=lsq_size)
        
        # Set cross-references
        self.lsq.rob = self.rob
        
        self.branch_predictor = BranchPredictor()
        
        # Initialize Fetch unit with provided dependencies
        self.fetch = Fetch(self.memory, self.branch_predictor, self.rob)  # fetch_width=2 hardcoded in Fetch
        self.decode = Decode(self.rat, self.rob, self.lsq, decode_width=decode_width)
        self.execute = Execute(self.memory, self.rat, self.rob, execute_width=execute_width)
        
        # Load program into memory and set initial state
        self.memory.load_program(program, 0x00000000)
        self.cycle = 0
        self.in_flight = set()  # Tracks ROB indices of dispatched instructions

    def tick(self):
        """
        Simulate one clock cycle of the out-of-order processor.
        """
        # # Commit stage: Retire completed instructions
        # self.rob.commit()

        # # LSQ commit: Commit stores to memory
        # self.lsq.commit()

        # # LSQ execute: Handle load/store execution and forwarding
        # self.lsq.tick(self.rat)

        # # Execute stage: Process in-flight instructions
        # completed = set()
        # rob_indices_to_execute = sorted(list(self.in_flight))[:self.execute.execute_width]
        # completed_indices = self.execute.tick(rob_indices_to_execute)
        # completed.update(completed_indices)
        # self.in_flight -= completed

        # Decode stage: Process instructions from fetch_buffer
        if self.fetch.fetch_buffer:  # Only proceed if fetch_buffer has instructions
            rob_indices = self.decode.tick(self.fetch.fetch_buffer)
            print(f"Decoded ROB indices: {rob_indices}")
            self.rob.print_rob_table()  # Print ROB state after decode
            self.rat.print_rat_table()  # Print RAT state after decode
            if rob_indices:
                self.in_flight.update(rob_indices)
                self.decode.clear_buffer()  # Clear decode buffer (assumed method in Decode)
                self.fetch.clear_buffer()  # Clear fetch buffer after decode consumes it

        # Fetch stage: Fetch new instructions
        self.fetch.tick()

        self.cycle += 1

    def run(self, debug=False):
        """
        Run the processor until all instructions are processed.

        Args:
            debug (bool): If True, print cycle-by-cycle state for debugging.
        """
        # Run until no more work remains
        while not self.rob.is_empty() or self.in_flight or self.fetch.fetch_buffer or self.fetch.pc < len(self.memory.memory):
            self.tick()
            if debug:
                rob_state = [f"ROB[{i}]: {entry['instr'] if entry else None}" for i, entry in enumerate(self.rob.entries)]
                print(f"Cycle {self.cycle}: PC={hex(self.fetch.pc)}, InFlight={self.in_flight}, "
                      f"FetchBuf={len(self.fetch.fetch_buffer)}, ROB={rob_state}")

    def get_state(self):
        """
        Return the current processor state for debugging.

        Returns:
            dict: Contains cycle count, PC, registers, memory, ROB entries, and in-flight instructions.
        """
        return {
            'cycle': self.cycle,
            'pc': self.fetch.pc,
            'registers': self.register_file.registers.copy(),  # Assuming we need all registers
            'memory': self.memory.dump_memory(0, len(self.memory.memory) // 4 + 1),  # Convert bytes to words
            'rob': [(i, entry['instr']) for i, entry in enumerate(self.rob.entries) if entry],
            'in_flight': list(self.in_flight)
        }