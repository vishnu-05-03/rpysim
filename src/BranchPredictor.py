class BranchPredictor:
    # Singleton instance
    _instance = None
    
    def __new__(cls, size=1024):
        if cls._instance is None:
            cls._instance = super(BranchPredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, size=1024):
        if self._initialized:
            return
            
        # 2-bit saturating counters: 0-1 (not taken), 2-3 (taken)
        self.table = [2] * size  # Initialize to weakly taken
        self.mask = size - 1     # For indexing (e.g., 1023 for size=1024)
        self.memory = None  # Will be set by processor
        self._initialized = True

    def predict(self, pc):
        index = (pc >> 2) & self.mask  # Use lower PC bits as index
        prediction = self.table[index] >= 2  # Taken if 2 or 3
        
        # Default to sequential execution
        target_address = pc + 4
        
        if prediction and self.memory:
            # Properly calculate branch target if we predict taken
            instr = self.memory.read_word(pc)
            if (instr & 0x7F) == 0x63:  # Branch instruction
                # Extract immediate field from B-type instruction
                imm = (
                    (((instr >> 31) & 0x1) << 12) |  # imm[12]
                    (((instr >> 7) & 0x1) << 11) |   # imm[11]
                    (((instr >> 25) & 0x3F) << 5) |  # imm[10:5]
                    (((instr >> 8) & 0xF) << 1)      # imm[4:1|0]
                )
                # Sign extend
                if (imm & 0x1000):
                    imm |= 0xFFFFE000
                    
                target_address = pc + imm
        
        return (prediction, target_address)

    def update(self, pc, actual_taken, actual_target):
        index = (pc >> 2) & self.mask
        if actual_taken:
            self.table[index] = min(self.table[index] + 1, 3)  # Increment counter
        else:
            self.table[index] = max(self.table[index] - 1, 0)  # Decrement counter