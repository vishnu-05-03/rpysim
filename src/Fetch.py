class Fetch:
    _instance = None
    
    def __new__(cls, memory=None, branch_predictor=None, rob=None):
        if cls._instance is None:
            cls._instance = super(Fetch, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self, memory, branch_predictor, rob):
        if not hasattr(self, 'initialized') or not self.initialized:
            self.memory = memory
            self.branch_predictor = branch_predictor
            self.rob = rob
            self.pc = 0
            self.fetch_buffer = []
            self.initialized = True
            self.fetch_width = 2  # Consistent with code
    
    def tick(self):
        if len(self.fetch_buffer) > 0:
            print('Fetch buffer not empty, waiting...')
            return None

        # Calculate available ROB slots
        available_slots = self.rob.size - ((self.rob.tail - self.rob.head) % self.rob.size)
        num_to_fetch = min(self.fetch_width, available_slots)
        if num_to_fetch == 0:
            print(f"No slots in ROB: {available_slots} available.")
            return None

        fetched = []
        current_pc = self.pc
        for _ in range(num_to_fetch):
            instr = self.memory.read_word(current_pc)
            if instr == 0:  # End of program
                break
            fetched.append((instr, current_pc))
            
            opcode = instr & 0x7F
            if opcode == 0x63:  # Branch instruction
                predicted_taken, target_address = self.branch_predictor.predict(current_pc)
                self.pc = target_address if predicted_taken else current_pc + 4
                break
            else:
                current_pc += 4
                self.pc = current_pc
        if fetched:
            self.fetch_buffer = fetched
            print(f"fetch buffer: {self.fetch_buffer}")
            return self.fetch_buffer
        print("Fetch buffer empty, no instructions fetched.")
        return None

    def flush(self, correct_pc):
        self.fetch_buffer = []
        self.pc = correct_pc

    def clear_buffer(self):
        self.fetch_buffer = []