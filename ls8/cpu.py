"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self, bits = 8):
        """Construct a new CPU."""
        self.memory_size = pow(2, bits)
        #not sure if this would be true for all machines without VM, but it seems like it
        self.max_value = self.memory_size - 1
        # Machine State
        self.running = True
        # Machine Architecture
        # holds instructions (pc), registers (pc + 1), and values (pc + 2)
        self.ram = [0] * self.memory_size
        # registers execute instructions
        self.num_registers = bits
        self.reg = [0] * self.num_registers
        
        # Stack Pointer
        #init SP
        self.SP = self.num_registers - 1
        self.reg_write(self.SP, 0xf4) #F4 in hex        

        # Program Counter - points to first byte of running instruction in ram
        # instructions should increment this appropriately
        self.pc = 0

        self.load()
        #TODO: List all instructions/get programmatically
        self.instructions = {
            0b10000010: "LDI",
            0b01000111: "PRN",
            0b00000001: "HLT",
            0b10100010: "MUL",
            0b01000101: "PUSH",
            0b01000110: "POP",
            0b01010000: "CALL",
            0b00010001: "RET",
            0b10100000: "ADD"
        }

    def load(self):
        """Load a program into memory."""
        #init 
        address = 0
        #construct file path
        try:
            filename = sys.argv[1]
        except:
            filename = 'call.ls8'
        
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
                    line = int(temp[0], 2)
                    print(line)
                    self.ram_write(address, line)

                except ValueError:
                    print(f"invalid number: {temp[0]}")
                except IndexError:
                    print(f"index number {address} does not exist")
                address += 1
            
        f.close()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            value = (self.reg_read(reg_a) + self.reg_read(reg_b) & self.max_value)
            self.reg_write(reg_a, value)
        elif op == "MUL":
            value = (self.reg_read(reg_a) * self.reg_read(reg_b)) & self.max_value
            self.reg_write(reg_a, value)             
        else:
            raise Exception("Unsupported ALU operation")

    def add(self):
        self.alu("ADD", self.get_curr_reg(), self.ram_read(self.pc+2))

    def mul(self):
        self.alu("MUL", self.get_curr_reg(), self.ram_read(self.pc+2))

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(self.pc)
        print(self.ram[self.pc])
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.get_curr_reg(),
            self.get_curr_val()
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, pc):
        value = self.ram[pc]
        return value

    def ram_write(self, pc, val):
        self.ram[pc] = val
        return (pc, val)

    def reg_read(self, pc):
        value = self.reg[pc]
        return value

    def reg_write(self, pc, val):
        self.reg[pc] = val
        return (pc, val)

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

        # 256 == 0b100000000

        # 100000000
       # &
        # 011111111
        # ___________
        # 0000000000 == 0 (result is 0)

        # in other words, 255 is an AND mask for this machine to determine if the value fits
        int_value = self.get_curr_val()
        self.reg_write(self.get_curr_reg(), int_value & self.max_value)

    def prn(self):
        print(self.reg_read(self.get_curr_reg()))

    def hlt(self):
        self.running = False

    def pop(self):
        # set the value at the top of the stack to the value in the registry in the instruction
        self.reg_write(self.get_curr_reg(), self.ram_read(self.reg_read(self.SP)))        
        # increment the current register on the stack
        self.reg[self.SP] += 1

    def push(self):
        #decrement the current register on the stack
        self.reg[self.SP] -= 1
        #set the address in ram to the value in the registry from the instruction
        self.ram_write(self.reg_read(self.SP), self.reg_read(self.get_curr_reg()))

    def call(self):
        ret_addr = self.pc + 2
        self.reg[self.SP] -= 1
        self.ram_write(self.reg_read(self.SP), ret_addr)
        #call
        reg_num = self.ram_read(self.get_curr_reg())
        self.pc = self.reg_read(reg_num)

    def ret(self):
        ret_addr = self.ram_read(self.reg_read(self.SP))
        self.reg[self.SP] += 1
        self.pc = ret_addr

    def shift_bytes_by_ins_size(self, ir):
        size = ir >> 6
        shift = size + 1
        self.pc += shift

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            
            if ir in self.instructions:
                # get the method associated with the value returned from self.pc 
                # the value returned from self.instructions is an uppercase string
                instruction = getattr(CPU, self.instructions[self.ram_read(self.pc)].lower())
                # pass self in to the method since self.instruction() isn't defined (run the method)
                instruction(self)
                print(instruction)
                #move the instruction pointer
                if ir & 0b0010000 == 0:
                    self.shift_bytes_by_ins_size(ir)

            else:
                print(f"Invalid Instruction: {ir}")
                self.running = False
                self.pc = 0
                return

            
            
                
pc = CPU()
pc.run()