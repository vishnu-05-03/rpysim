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
    def __init__(self, program, commit_width=2):
        self.memory = Memory()
        self.register_file = RegisterFile()
        self.rob = ROB(size=8, register_file=self.register_file, commit_width=commit_width)
        self.register_file.rat = RAT(self.rob, num_phys_regs=64)
        self.lsq = LSQ(self.memory, size=8)
        self.branch_predictor = BranchPredictor()
        self.fetch = Fetch(self.memory, self.branch_predictor, self.rob)
        self.decode = Decode(self.register_file.rat, self.rob, self.lsq)
        self.execute = Execute(self.memory, self.register_file.rat, self.rob)
        self.memory.load_program(program, 0x00000000)
        self.cycle = 0
        self.in_flight = set()
        # Optional: Initialize registers for testing
        self.register_file.write_arch(1, 10)  # x1 = 10
        self.register_file.write_arch(2, 20)  # x2 = 20
        self.register_file.write_arch(3, 30)  # x3 = 30
        self.register_file.write_arch(4, 40)  # x4 = 40

    def tick(self):
        # Commit stage
        self.rob.commit()

        # LSQ stage (not used in this program)
        self.lsq.tick(self.register_file.rat)
        self.lsq.commit()
        
        # Execute stage
        completed = set()
        for rob_index in self.in_flight:
            if self.execute.execute(rob_index):
                completed.add(rob_index)
        self.in_flight -= completed

        # Decode stage
        if self.fetch.fetch_buffer:
            rob_indices = self.decode.tick(self.fetch.fetch_buffer)
            for rob_index in rob_indices:
                self.in_flight.add(rob_index)
            self.decode.clear_buffer()
            self.fetch.clear_buffer()

        # Fetch stage
        self.fetch.tick()

        self.cycle += 1
        
        # Debugging output
        print(f"\nCycle {self.cycle}: PC={self.fetch.pc}")
        # self.print_rat()
        self.print_rob()

    def print_rat(self):
        print("\n=== Register Alias Table (RAT) ===")
        print("Arch Reg | Phys Reg | Previous Phys")
        print("-----------------------------------")
        for i in range(32):
            reg_name = f"x{i}"
            if i == 0:
                reg_name = "x0 (zero)"
            elif i == 1:
                reg_name = "x1 (ra)"
            elif i == 2:
                reg_name = "x2 (sp)"
            phys_reg = f"p{self.register_file.rat.rat[i]}" if self.register_file.rat.rat[i] is not None else "arch"
            prev_phys = f"p{self.register_file.rat.prev_phys[i]}" if self.register_file.rat.prev_phys[i] is not None else "-"
            print(f"{reg_name:<9} | {phys_reg:<8} | {prev_phys}")
        print("\n=== Free Physical Registers ===")
        print(" ".join(f"p{i}" for i in self.register_file.rat.free_list))
        print("===================================")

    def print_rob(self):
        print("\n=== Reorder Buffer (ROB) ===")
        print(f"Head: {self.rob.head}, Tail: {self.rob.tail}")
        print("Index | Completed | Value      | Phys Reg | Instruction")
        print("------------------------------------------------------------")
        for i in range(self.rob.size):
            if self.rob.entries[i] is None:
                print(f" {i:<5} | Empty     | -          | -        | -")
            else:
                completed = "Yes" if self.rob.entries[i]['completed'] else "No"
                value = f"0x{self.rob.entries[i]['value']:08x}" if self.rob.entries[i]['value'] is not None else "-"
                phys_reg = f"p{self.rob.entries[i]['phys_rd']}" if self.rob.entries[i]['phys_rd'] is not None else "-"
                instr = str(self.rob.entries[i]['instr'])
                arrow = "→" if i == self.rob.head else " "
                print(f" {i:<2} {arrow:<2} | {completed:<9} | {value:<10} | {phys_reg:<8} | {instr}")
        print("============================================================")

    def run(self):
        while not self.rob.is_empty() or self.fetch.pc < len(self.memory.memory) * 4:
            self.tick()