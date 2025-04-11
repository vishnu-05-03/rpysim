from src.Memory import Memory
from src.RegisterFile import RegisterFile
from src.Fetch import Fetch
from src.BranchPredictor import BranchPredictor
from src.ROB import ROB
# from src.RAT import RAT
# from src.LSQ import LSQ
# from src.Decode import Decode

class OoOProcessor:
    def __init__(self, program):
        self.memory = Memory()
        self.register_file = RegisterFile()
        self.rob = ROB(size=8, register_file=self.register_file)
        # self.rat = RAT(self.rob)
        # self.lsq = LSQ(self.memory, size=8)
        self.branch_predictor = BranchPredictor()  # Assume a simple predictor
        self.fetch = Fetch(self.memory, self.branch_predictor, self.rob)
        # self.decode = Decode(self.rat, self.rob, self.lsq)
        # self.execute = Execute(self.memory, self.rat, self.rob)
        self.memory.load_program(program,0x00000000)
        self.cycle = 0
        self.in_flight = set()

    def tick(self):

        # # LSQ stage
        # self.rob.commit()
        # self.lsq.commit()
        # self.lsq.tick(self.rat)
        
        # # Commit stage
        # if self.rob.commit():
        #     self.rat.commit(self.rob.entries[self.rob.head]['instr'][1] if self.rob.entries[self.rob.head]['instr'][0] != 'SW' else None, self.rob.head)

        # # Execute stage
        # completed = set()
        # for rob_index in self.in_flight:
        #     if self.execute.execute(rob_index):
        #         completed.add(rob_index)
        # self.in_flight -= completed

        # # Decode stage
        # if self.fetch.fetch_buffer is not None:
        #     rob_index = self.decode.tick(self.fetch.fetch_buffer)
        #     if rob_index is not None:
        #         self.in_flight.add(rob_index)
        #     self.fetch.clear_buffer()

        # Fetch stage
        self.fetch.tick()

        self.cycle += 1
    
    # def run(self):
    #     while not self.rob.is_empty() or self.fetch.pc < len(self.memory.memory):
    #         self.tick()
    #         print(f"Cycle {self.cycle}: PC={self.fetch.pc}, ROB={self.rob.entries}")