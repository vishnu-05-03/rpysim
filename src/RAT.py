class RAT:
    def __init__(self, rob, num_phys_regs=64):
        self.rob = rob
        self.num_phys_regs = num_phys_regs
        self.rat = [None] * 32
        self.rat[0] = 0
        self.free_list = list(range(1, num_phys_regs))
        self.phys_to_rob = [None] * num_phys_regs
        self.prev_phys = [None] * 32

    def allocate_phys_reg(self, rob_index):
        if not self.free_list:
            return None
        phys_reg = self.free_list.pop(0)
        self.phys_to_rob[phys_reg] = rob_index
        return phys_reg

    def free_phys_reg(self, phys_reg):
        if phys_reg != 0 and phys_reg not in self.free_list:
            self.free_list.append(phys_reg)
            self.phys_to_rob[phys_reg] = None

    def set_mapping(self, reg_num, phys_reg, rob_index):
        if reg_num != 0:
            self.prev_phys[reg_num] = self.rat[reg_num]
            self.rat[reg_num] = phys_reg
            self.phys_to_rob[phys_reg] = rob_index

    def get_value(self, reg_num):
        if reg_num == 0:
            return 0
        phys_reg = self.rat[reg_num]
        if phys_reg is None:
            return self.rob.register_file.read_arch(reg_num)
        rob_index = self.phys_to_rob[phys_reg]
        if rob_index is not None and self.rob.entries[rob_index]['completed']:
            return self.rob.register_file.read_phys(phys_reg)
        return self.rob.register_file.read_arch(reg_num)  # Fallback to arch reg

    def commit(self, reg_num, rob_index):
        if reg_num is None or reg_num == 0:
            return
        phys_reg = self.rat[reg_num]
        if phys_reg is not None and self.phys_to_rob[phys_reg] == rob_index:
            value = self.rob.register_file.read_phys(phys_reg)
            self.rob.register_file.write_arch(reg_num, value)
            prev_phys = self.prev_phys[reg_num]
            if prev_phys is not None:
                self.free_phys_reg(prev_phys)
            self.prev_phys[reg_num] = None
            self.rat[reg_num] = None
            self.phys_to_rob[phys_reg] = None
