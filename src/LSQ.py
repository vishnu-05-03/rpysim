class LSQ:
    def __init__(self, memory, size=8):
        self.memory = memory
        self.size = size
        self.entries = [None] * size  # Circular queue
        self.head = 0  # Points to next commit
        self.tail = 0  # Points to next free slot

    def add_load(self, rob_index, rs1, imm):
        """Add a load to the LSQ."""
        if (self.tail + 1) % self.size == self.head:
            return None  # LSQ full
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
        """Add a store to the LSQ."""
        if (self.tail + 1) % self.size == self.head:
            return None  # LSQ full
        entry = {
            'type': 'store',
            'rob_index': rob_index,
            'rs1': rs1,
            'rs2': rs2,
            'imm': imm,
            'address': None,
            'value': None,
            'completed': False  # Address/value computed
        }
        lsq_index = self.tail
        self.entries[lsq_index] = entry
        self.tail = (self.tail + 1) % self.size
        return lsq_index

    def tick(self, rat):
        """Process LSQ entries each cycle."""
        for i in range(self.size):
            if self.entries[i] is not None and not self.entries[i]['completed']:
                entry = self.entries[i]
                rs1_val = rat.get_value(entry['rs1'])
                if rs1_val is None:
                    continue  # Stall until rs1 ready

                entry['address'] = rs1_val + entry['imm']
                if entry['type'] == 'load':
                    # Check for forwarding from earlier stores
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
                    self.rob.entries[entry['rob_index']]['completed'] = True

                elif entry['type'] == 'store':
                    rs2_val = rat.get_value(entry['rs2'])
                    if rs2_val is None:
                        continue  # Stall until rs2 ready
                    entry['value'] = rs2_val
                    entry['completed'] = True

    def commit(self):
        """Commit stores from the head of the LSQ."""
        if self.entries[self.head] is None:
            return False
        entry = self.entries[self.head]
        if not entry['completed'] or entry['rob_index'] != self.rob.head:
            return False  # Not ready or out of order
        if entry['type'] == 'store':
            self.memory.write_word(entry['address'], entry['value'])
        self.entries[self.head] = None
        self.head = (self.head + 1) % self.size
        return True