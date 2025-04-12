class RegisterFile:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegisterFile, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the register file"""
        self.registers = [0] * 32  # 32 architectural registers
        self.registers[0] = 0      # x0 is hardwired to 0

    def read(self, reg_num):
        if reg_num == 0:
            return 0
        return self.registers[reg_num]

    def write(self, reg_num, value):
        if reg_num != 0:
            self.registers[reg_num] = value
    
    def read_all(self):
        """Return a copy of all registers"""
        return self.registers.copy()