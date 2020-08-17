"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self, bits = 8):
        """Construct a new CPU."""
        max_value = 2^bits
        # Machine State
        self.running = True
        # holds instructions (pc), registers (pc + 1), and values (pc + 2)
        self.ram = [0] * max_value
        # registers execute instructions (1 reg per bit?)
        self.reg = [0] * bits

        # Program Counter - points to first byte of running instruction in ram
        # instructions should increment this appropriately
        self.pc = 0

        #address being read or written to
        self.MAR = 0
        #value at address being read or written 
        self.MDR = 0

        self.load()

        self.instructions = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "HLT": 0b00000001
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, pc):
        value = self.ram[pc]
        self.MAR = pc
        self.MDR = value
        return value

    def ram_write(self, pc, val):        
        self.MAR = pc
        self.MDR = val
        self.ram[pc] = val
        return (pc, val)
        
    def save_reg(self, reg, value):
        self.reg[reg] = value
        #move ptr to next instruction
        self.pc += 3

    #registry is always the ptr after the instruction
    def get_curr_reg(self):
        return self.ram_read(self.pc + 1)
    
    def get_curr_val(self):
        return self.ram_read(self.pc + 2)

    def ldi(self):        
        #copy the bit to the result if it exists (255 is 11111111)
        self.reg[self.get_curr_reg()] = self.get_curr_val() & 255
        self.pc += 3

    def prn(self):
        print(self.reg[self.get_curr_reg()])
        #move ptr to next instruction
        self.pc += 2

    def halt(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            #methods move ptr to next instruction
            if ir == self.instructions["LDI"]:
                self.ldi()

            elif ir == self.instructions["PRN"]:                
                self.prn()

            elif ir == self.instructions["HLT"]:
                self.halt()
                
pc = CPU()
pc.run()
pc.trace()