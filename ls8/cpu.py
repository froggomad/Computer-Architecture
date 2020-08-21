import sys
import os

class CPU:
    """Main CPU class."""

    # MARK: Init
    def __init__(self, bits = 8):
        """Construct a new CPU."""
        # Machine State
        self.running = True
        # Program Counter - points to first byte of running instruction in ram
        # instructions should increment this appropriately
        self.pc = 0
        # Comparison register - used to store comparison values
        self.fl = 6
        
        # Machine Architecture
        self.memory_size = pow(2, bits)        
        #not sure if this would be true for all machines without VM, but it seems like it
        self.max_value = self.memory_size - 1
        # RAM holds instructions (pc), registers (pc + 1), and values (pc + 2)
        self.ram = [0] * self.memory_size
        # registers execute instructions
        self.num_registers = bits
        self.reg = [0] * self.num_registers
        # init SP (Stack Pointer)
        self.SP = self.num_registers - 1
        self.reg_write(self.SP, 0xf4) #F4 in hex        

        # Load Instructions into RAM
        self.load()
        
        self.instructions = {
            0b10000010: "LDI",
            0b01000111: "PRN",
            0b00000001: "HLT",
            0b10100010: "MUL",
            0b01000101: "PUSH",
            0b01000110: "POP",
            0b01010000: "CALL",
            0b00010001: "RET",
            0b10100000: "ADD",
            0b10100111: "CMP2",
            0b01010100: "JMP",
            0b01010101: "JEQ",
            0b01010110: "JNE",
            0b10100011: "XOR2"
        }

    # MARK: Debug
    def trace(self):
        """
        Print the current CPU State.
        """
        print(self.pc)
        print(self.ram[self.pc])
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.get_curr_reg(),
            self.get_curr_val()
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # MARK: Create
    def load(self):
        """Load a program into memory."""
        #init 
        address = 0
        #construct file path
        try:
            filename = sys.argv[1]
        except:
            filename = 'XOR.ls8'
        
        cur_path = os.path.dirname(__file__)

        new_path = os.path.relpath(f'examples/{filename}', cur_path)
      
        # load program from file
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
                    #print(line)
                    self.ram_write(address, line)

                except ValueError:
                    print(f"invalid number: {temp[0]}")
                except IndexError:
                    print(f"index number {address} does not exist")
                address += 1
            
        f.close()

    # MARK: Math Co-Processor
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            value = (self.reg_read(reg_a) + self.reg_read(reg_b) & self.max_value)
            self.reg_write(reg_a, value)
        elif op == "MUL":
            value = (self.reg_read(reg_a) * self.reg_read(reg_b)) & self.max_value
            self.reg_write(reg_a, value)
        elif op == "XOR":
            self.cmp2()
            value = 0
            if self.reg_read(self.fl) != 1:                
                value = 1
            self.reg_write(reg_a, value)
        else:
            raise Exception("Unsupported ALU operation")

    def add(self):
        #TODO: get_cur_val instead of ram_read
        """add 2 registry values together and write the result to the first registry"""
        self.alu("ADD", self.get_curr_reg(), self.ram_read(self.pc+2))

    def mul(self):
        """multiply 2 registry values together and write the result to the first registry"""
        #TODO: get_cur_val instead of ram_read
        self.alu("MUL", self.get_curr_reg(), self.ram_read(self.pc+2))

    def and2(self):
        pass

    def or2(self):
        pass

    def xor2(self): 
        #None could really be passed in for the 2nd arg since this is using CMP       
        self.alu("XOR", self.get_curr_reg(), self.get_curr_val())

        # if value1 == value2:
        #     #write 0
        # else:
        #     #write 1

    def not2(self):
        pass

    def shl(self):
        pass

    def shr(self):
        pass

    def mod(self):
        pass
    
    # MARK: Read
    def ram_read(self, pc):
        """Read a value from RAM given a program counter"""
        value = self.ram[pc]
        return value

    def cmp2(self):
        """Compare 2 given values
           Returns:
            1 if equal (1 in the last byte) E
            2 if greater (1 in the 2nd to last byte) G
            4 if less (1 in the 3rd to last byte) L
        """
        value1 = self.reg_read(self.get_curr_reg())
        value2 = self.reg_read(self.get_curr_val())

        if value1 == value2:
            self.reg_write(self.fl, 1)
        elif value1 > value2:
            self.reg_write(self.fl, 2)            
        else:
            self.reg_write(self.fl, 4)            
    
    def jmp(self):
        """Jump to the given register"""
        self.pc = self.reg_read(self.get_curr_reg())

    def jeq(self):
        """see if the value from the comparison is equal"""
        if self.reg_read(self.fl) == 1:
            self.jmp()
        # move the pointer if we aren't jumping
        else:
            self.pc += 2

    def jne(self):
        """see if the value from the comparison is not equal"""
        if self.reg_read(self.fl) != 1:
            self.jmp()
        # move the pointer if we aren't jumping
        else:
            self.pc += 2

    def reg_read(self, pc):
        """Read a value from the registry given a program counter"""
        value = self.reg[pc]
        return value

    # MARK: Update/Write
    def ram_write(self, pc, val):
        """Write a value to RAM given a program counter and value"""
        self.ram[pc] = val
        return (pc, val)

    def reg_write(self, pc, val):
        """Write a value to the registry given a program counter and value"""
        self.reg[pc] = val
        return (pc, val)

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
        """Print the program's current registry value"""
        print(self.reg_read(self.get_curr_reg()))

    def hlt(self):
        """Stop running the machine"""
        self.running = False

    def pop(self):
        """set the value at the top of the stack to the value
         in the current registry per the instruction and increment
         the current register on the stack (Stack Pointer)"""
        self.reg_write(self.get_curr_reg(), self.ram_read(self.reg_read(self.SP)))        
        
        self.reg[self.SP] += 1

    def push(self):
        """Decrement the current register on the stack (Stack Pointer) 
        and set the address in RAM to the value in the current registry
        """        
        self.reg[self.SP] -= 1
        
        self.ram_write(self.reg_read(self.SP), self.reg_read(self.get_curr_reg()))

    def call(self):
        """Call a Subroutine (function) in the registry stack"""
        ret_addr = self.pc + 2
        self.reg[self.SP] -= 1
        self.ram_write(self.reg_read(self.SP), ret_addr)
        #call
        reg_num = self.ram_read(self.get_curr_reg())
        self.pc = self.reg_read(reg_num)

    def ret(self):
        """Set a return value in the registry stack"""
        ret_addr = self.ram_read(self.reg_read(self.SP))
        self.reg[self.SP] += 1
        self.pc = ret_addr

    # MARK: Helpers    
    def get_curr_reg(self):
        """Get the current registry from the instruction"""
        return self.ram_read(self.pc + 1)

    def get_curr_val(self):
        """Get the current value from the instruction"""
        return self.ram_read(self.pc + 2)

    def shift_bytes_by_ins_size(self, ir):
        """Shift the ir to the next instruction"""
        size = ir >> 6
        shift = size + 1
        self.pc += shift
    
    # MARK: Main Run Loop
    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            
            if ir in self.instructions:                
                # get the method associated with the value returned from self.pc 
                # the value returned from self.instructions is an uppercase string
                ins_name = self.instructions[self.ram_read(self.pc)]
                instruction = getattr(CPU, ins_name.lower())                  
                # pass self in to the method since self.instruction() isn't defined (run the method)
                instruction(self)

                # move the instruction pointer if this isn't a call or return                
                if ir & 0b0010000 == 0:
                    self.shift_bytes_by_ins_size(ir)

            else:
                print(f"Invalid Instruction: {ir}")
                self.running = False
                self.pc = 0
                return

pc = CPU()
pc.run()