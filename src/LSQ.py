class LSQ:
    def __init__(self, memory, size=8):
        self.memory = memory
        self.size = size
        self.entries = [None] * size
        self.head = 0
        self.tail = 0

    def add_load(self, rob_index, rs1, imm):
        if (self.tail + 1) % self.size == self.head:
            return None
        entry = {
            'type': 'load',
            'rob_index': rob_index,
            'rs1': rs1,
            'imm': imm,
            'address': None,
            'value': None,
            'completed': False
        }
        lsq_index = self.tail
        self.entries[lsq_index] = entry
        self.tail = (self.tail + 1) % self.size
        return lsq_index

    def add_store(self, rob_index, rs1, rs2, imm):
        if (self.tail + 1) % self.size == self.head:
            return None
        entry = {
            'type': 'store',
            'rob_index': rob_index,
            'rs1': rs1,
            'rs2': rs2,
            'imm': imm,
            'address': None,
            'value': None,
            'completed': False
        }
        lsq_index = self.tail
        self.entries[lsq_index] = entry
        self.tail = (self.tail + 1) % self.size
        return lsq_index

    def tick(self, rat):
        for i in range(self.size):
            if self.entries[i] is not None and not self.entries[i]['completed']:
                entry = self.entries[i]
                rs1_val = rat.get_value(entry['rs1'])
                if rs1_val is None:
                    continue

                entry['address'] = rs1_val + entry['imm']
                if entry['type'] == 'load':
                    for j in range(self.head, i):
                        if self.entries[j] and self.entries[j]['type'] == 'store' and \
                           self.entries[j]['address'] == entry['address'] and \
                           self.entries[j]['completed']:
                            entry['value'] = self.entries[j]['value']
                            break
                    else:
                        entry['value'] = self.memory.read_word(entry['address'])
                    entry['completed'] = True
                    self.rob.entries[entry['rob_index']]['value'] = entry['value']
                    if self.rob.entries[entry['rob_index']]['phys_rd'] is not None:
                        self.rob.register_file.write_phys(
                            self.rob.entries[entry['rob_index']]['phys_rd'],
                            entry['value']
                        )
                    self.rob.entries[entry['rob_index']]['completed'] = True

                elif entry['type'] == 'store':
                    rs2_val = rat.get_value(entry['rs2'])
                    if rs2_val is None:
                        continue
                    entry['value'] = rs2_val
                    entry['completed'] = True

    def commit(self):
        if self.entries[self.head] is None:
            return False
        entry = self.entries[self.head]
        if not entry['completed'] or entry['rob_index'] != self.rob.head:
            return False
        if entry['type'] == 'store':
            self.memory.write_word(entry['address'], entry['value'])
        self.entries[self.head] = None
        self.head = (self.head + 1) % self.size
        return True