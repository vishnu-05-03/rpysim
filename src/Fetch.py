class Fetch:
    _instance = None
    
    def __new__(cls, memory=None, branch_predictor=None, rob=None):
        if cls._instance is None:
            cls._instance = super(Fetch, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self, memory, branch_predictor, rob):
        # Only initialize once
        if not hasattr(self, 'initialized') or not self.initialized:
            self.memory = memory
            self.branch_predictor = branch_predictor
            self.rob = rob
            self.pc = 0
            self.fetch_buffer = []
            self.initialized = True
            self.fetch_width = 2
    
    def tick(self):
        if len(self.fetch_buffer) > 0:  # Wait for Decode to consume
            print('Fetch buffer not empty, waiting...')
            return None

        available_slots = self.rob.size - ((self.rob.tail - self.rob.head) % self.rob.size)
        if available_slots < self.fetch_width:
            print(f"Not enough slots in ROB: {available_slots} available, {self.fetch_width} needed.")
            return None

        fetched = []
        current_pc = self.pc
        for _ in range(self.fetch_width):
            instr = self.memory.read_word(current_pc)
            if instr == 0:  # End of program
                break
            fetched.append((instr, current_pc))
            
            # Predict only for the first branch encountered
            opcode = instr & 0x7F
            if opcode == 0x63:  # Branch instruction
                predicted_taken, target_address = self.branch_predictor.predict(current_pc)
                self.pc = target_address if predicted_taken else current_pc + 4
                break  # Stop fetching after a branch
            # if opcode == 0x6F:  # JAL instruction
            # if opcode == 0x67:  # JALR instruction
            else:
                current_pc += 4
                self.pc = current_pc
        if fetched:
            self.fetch_buffer = fetched
            return self.fetch_buffer
        print("Fetch buffer empty, no instructions fetched.")
        return None

    def flush(self, correct_pc):
        self.fetch_buffer = []
        self.pc = correct_pc

    def clear_buffer(self):
        self.fetch_buffer = []
