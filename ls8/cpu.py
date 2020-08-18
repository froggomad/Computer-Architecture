"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self, bits = 8):
        """Construct a new CPU."""
        self.max_value = pow(2, bits)
        # Machine State
        self.running = True
        # holds instructions (pc), registers (pc + 1), and values (pc + 2)
        self.ram = ['0b0'] * self.max_value
        # registers execute instructions
        self.reg = [0] * bits
        # Program Counter - points to first byte of running instruction in ram
        # instructions should increment this appropriately
        self.pc = 0

        self.load()
        #TODO: List all instructions/get programmatically
        self.instructions = {
            0b10000010: "LDI",
            0b01000111: "PRN",
            0b00000001: "HLT",
            0b10100010: "MUL"
        }

    def load(self):
        """Load a program into memory."""
        #init 
        address = 0

        #construct file path
        try:
            filename = sys.argv[1]
        except:
            filename = 'mult.ls8'
        
        cur_path = os.path.dirname(__file__)

        new_path = os.path.relpath(f'examples/{filename}', cur_path)
        
        #load program from file
        with open(new_path) as f:
            for line in f:
                line = line.strip()
                temp = line.split()

                if len(temp) == 0:
                    continue
                if temp[0][0] == '#':
                    continue
            
                try:
                    line = bin(int(temp[0], 2))
                    self.ram[address] = line

                except ValueError:
                    print(f"invalid number: {temp[0]}")
                except IndexError:
                    print(f"index number {address} does not exist")
                address += 1

        for line in self.ram:
            print(line)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] = (self.reg[reg_a] + self.reg[reg_b]) & 255
        elif op == "MUL":
            #255 is max_value mask
            self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b]) & 255 
        else:
            raise Exception("Unsupported ALU operation")

    def mul(self):
        self.alu("MUL", self.ram_read(self.pc+1), self.ram_read(self.pc+2))

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
        return int(value, 2)

    def ram_write(self, pc, val):
        self.ram[pc] = val
        return (pc, val)
        
    # def save_reg(self, reg, value):
    #     self.reg[reg] = value
    #     #move ptr to next instruction
    #     self.pc += 3

    #registry is always the ptr after the instruction
    def get_curr_reg(self):
        return self.ram_read(self.pc + 1)
    
    def get_curr_val(self):
        return self.ram_read(self.pc + 2)

    def ldi(self):        
        """copy the bit to the specified (current_reg) register if it fits"""
        # 8 ==   0b00001000
        # 255 == 0b11111111
        
        # 1000
       # &
        # 11111111
        # ________
        # 10000000 == 1000 (result is 8)

        # in other words, 255 is an AND mask for this machine to determine if the value fits
        int_value = self.ram_read(self.pc + 2)
        self.reg[self.pc] = int_value & 255

    def prn(self):
        print(self.reg[self.get_curr_reg()])

    def hlt(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            size = ir >> 6
            shift = size + 1
            
            if ir in self.instructions:
                # get the method associated with the value returned from self.pc 
                # the value returned from self.instructions is a string
                instruction = getattr(CPU, self.instructions[self.ram_read(self.pc)].lower())
                #pass self in to the method since self.instruction() isn't defined
                instruction(self)
                print(instruction)
                
                self.pc += shift

            else:
                print("Invalid Instruction")
                return
            
                
pc = CPU()
pc.trace()
pc.run()
pc.trace()