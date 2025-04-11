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
        self._initialized = True

    def predict(self, pc):
        index = (pc >> 2) & self.mask  # Use lower PC bits as index
        prediction = self.table[index] >= 2  # Taken if 2 or 3
        target_address = pc + 4  # Simplified: assume sequential for now
        if prediction:
            # In a real predictor, compute target from instruction
            target_address = pc + 8  # Dummy target for demo
        return (prediction, target_address)

    def update(self, pc, actual_taken, actual_target):
        index = (pc >> 2) & self.mask
        if actual_taken:
            self.table[index] = min(self.table[index] + 1, 3)  # Increment counter
        else:
            self.table[index] = max(self.table[index] - 1, 0)  # Decrement counter