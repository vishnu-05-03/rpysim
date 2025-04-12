class RegisterFile:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegisterFile, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.arch_registers = [0] * 32
        self.arch_registers[0] = 0
        self.phys_registers = [0] * 64
        self.phys_registers[0] = 0
        self.rat = None  # Will be set by OoOProcessor

    def read_arch(self, reg_num):
        if reg_num == 0:
            return 0
        return self.arch_registers[reg_num]

    def write_arch(self, reg_num, value):
        if reg_num != 0:
            self.arch_registers[reg_num] = value & 0xFFFFFFFF

    def read_phys(self, phys_reg_num):
        if phys_reg_num == 0:
            return 0
        return self.phys_registers[phys_reg_num]

    def write_phys(self, phys_reg_num, value):
        if phys_reg_num != 0:
            self.phys_registers[phys_reg_num] = value & 0xFFFFFFFF

    def read_all_arch(self):
        return self.arch_registers.copy()