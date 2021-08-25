import array as arr
import sys

# TODO add bit shift operation
opcode = ["ADD", "SUB", "NOT", "AND", "OR", "XOR", "SHL", "SHR", "MOV", "LD", "ST", "B", "HLT"]

DO_NOT_SET_FLAG = 0
SET_FLAG = 1
RAM_SIZE = 1024
RF_SIZE = 32

verbose = False
debug = False

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_hex(val):
    return '{0:0{1}x}'.format(val, 8)


def init_memory():
    global mem
    mem = arr.array('I', [])
    for x in range(0, RAM_SIZE):
        mem.append(0)


def init_RF():
    global RF
    RF = arr.array('I', [])
    for x in range(0, RF_SIZE):
        RF.append(0)


def init():
    global Register
    global Signal
    Register = {
        "PC": 0,
        "A": 0,
        "B": 0,
        "C": 0,
        "MAR": 0,
        "MBR": 0,
        "RFOUT1": 0,
        "RFOUT2": 0,
        "RFIN": 0,
        "IR": 0,
        "ZERO_FLAG": 0
    }
    Signal = {
        "next_is_addr": 0,
        "src_reg_is_addr": 0,
        "dst_reg_is_addr": 0,
        "branch": 0,
        "read_RF_port_1": 0,
        "read_RF_port_2": 0,
        "write_RF": 0,
        "src_of_S1": '',
        "dst_of_S1": '',
        "src_of_S2": '',
        "dst_of_S2": '',
        "src_of_D": '',
        "dst_of_D": '',
        "doalu": 0,
        "ALU_func": '',
        "move_via_S1": 0,
        "move_via_S2": 0,
        "move_via_D": 0,
        "read_memory": 0,
        "write_memory": 0,
        "dohalt": 0
    }
    init_memory()
    init_RF()


def reset():
    Register["PC"] = 0


def incPC():
    Register["PC"] += 4
    if verbose:
        eprint("PC is increased by 4 (", get_hex(Register["PC"]), ")")


def do_move_via_S1(src, dst):
    Register[dst] = Register[src]
    if verbose:
        eprint("Move via S1: ", dst, "<-", src,
               " (", get_hex(Register[src]), ")")


def do_move_via_S2(src, dst):
    Register[dst] = Register[src]
    if verbose:
        eprint("Move via S2: ", dst, "<-", src,
               " (", get_hex(Register[src]), ")")


def do_move_via_D(src, dst):
    Register[dst] = Register[src]
    if verbose:
        eprint("Move via D: ", dst, "<-", src,
               " (", get_hex(Register[src]), ")")


def do_read_RF_port1(shift=16):
    # default register number = 0x00FF0000 & IR
    reg = (Register["IR"] >> shift) & 0xFF
    Register["RFOUT1"] = RF[reg]
    if verbose:
        eprint("Read RF Port 1 -- R", reg,
               " (", get_hex(Register["RFOUT1"]), ")")


def do_read_RF_port2(shift=8):
    reg = (Register["IR"] >> shift) & 0xFF
    Register["RFOUT2"] = RF[reg]
    if verbose:
        eprint("Read RF Port 2 -- R", reg,
               " (", get_hex(Register["RFOUT2"]), ")")


def do_write_RF(shift=0):
    reg = (Register["IR"] >> shift) & 0xFF
    RF[reg] = Register["RFIN"]
    if verbose:
        eprint("Write RF -- R", reg, " (", get_hex(Register["RFIN"]), ")")


def ALU_COPY():
    Register["C"] = Register["A"]
    if verbose:
        eprint("ALU (COPY)")


def ALU_ADD():
    Register["C"] = (Register["A"] + Register["B"]) & 0xFFFFFFFF
    if verbose:
        eprint("ALU (ADD)")


def ALU_SUB():
    Register["C"] = (Register["A"] - Register["B"]) & 0xFFFFFFFF
    if verbose:
        eprint("ALU (SUB)")


def ALU_AND():
    Register["C"] = Register["A"] & Register["B"]
    if verbose:
        eprint("ALU (AND)")


def ALU_OR():
    Register["C"] = Register["A"] | Register["B"]
    if verbose:
        eprint("ALU (OR)")


def ALU_NOT():
    Register["C"] = (Register["A"] ^ 0xFFFFFFFF) & 0xFFFFFFFF
    if verbose:
        eprint("ALU (NOT)")


def ALU_XOR():
    Register["C"] = Register["A"] ^ Register["B"]
    if verbose:
        eprint("ALU (XOR)")


def ALU_SHL():
    Register["C"] = (Register["A"] << Register["B"]) & 0xFFFFFFFF
    if verbose:
        eprint("ALU (SHL)")


def ALU_SHR():
    Register["C"] = (Register["A"] >> Register["B"])
    if verbose:
        eprint("ALU (SHR)")


def ALU_operation(opcode, setflag):
    # TODO key考虑换成数字
    switcher = {
        "OP_COPY": ALU_COPY,
        "OP_ADD": ALU_ADD,
        "OP_SUB": ALU_SUB,
        "OP_AND": ALU_AND,
        "OP_OR": ALU_OR,
        "OP_NOT": ALU_NOT,
        "OP_XOR": ALU_XOR,
        "OP_SHL": ALU_SHL,
        "OP_SHR": ALU_SHR
    }
    func = switcher.get(opcode)
    func()
    if (setflag == 1):
        if (Register["C"] == 0):
            Register["ZERO_FLAG"] = 1
        else:
            Register["ZERO_FLAG"] = 0
        if verbose:
            eprint("Zero Flag Set to ", Register["ZERO_FLAG"])


def do_read_memory():
    addr = Register["MAR"]//4
    Register["MBR"] = mem[addr]
    if verbose:
        eprint("Read Memory at ", get_hex(
            Register["MAR"]), " (", get_hex(Register["MBR"]), ")")


def do_write_memory():
    addr = Register["MAR"]//4
    mem[addr] = Register["MBR"]
    if verbose:
        eprint("Write Memory at ", get_hex(
            Register["MAR"]), " (", get_hex(Register["MBR"]), ")")


def set_ADD(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_ADD"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1  # TODO 改名D-BUS会不会好点，不然容易和ALU的ABC混淆
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_SUB(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_SUB"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_AND(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_AND"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_OR(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_OR"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_NOT(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 0
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = ""
    Signal["dst_of_S2"] = ""
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_NOT"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 0
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_MOVE(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 0
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = ""
    Signal["dst_of_S2"] = ""
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_COPY"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 0
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_LD(ctrl):
    # ctrl: 00 absolute address     80 register address
    Signal["next_is_addr"] = 1 if ctrl == 0x00 else 0
    Signal["src_reg_is_addr"] = 1 if ctrl == 0x80 else 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 0
    Signal["read_RF_port_2"] = 0
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "MBR"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = ""
    Signal["dst_of_S2"] = ""
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_COPY"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 0
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 1 if ctrl == 0x00 else 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_ST(ctrl):
    Signal["next_is_addr"] = 1 if ctrl == 0x00 else 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 1 if ctrl == 0x80 else 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 0
    Signal["write_RF"] = 0
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = ""
    Signal["dst_of_S2"] = ""
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "MBR"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_COPY"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 0
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 1
    Signal["dohalt"] = 0


def set_BR(ctrl):
    Signal["next_is_addr"] = 1
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 1
    Signal["read_RF_port_1"] = 0
    Signal["read_RF_port_2"] = 0
    Signal["write_RF"] = 0
    Signal["src_of_S1"] = ""
    Signal["dst_of_S1"] = ""
    Signal["src_of_S2"] = ""
    Signal["dst_of_S2"] = ""
    Signal["src_of_D"] = ""
    Signal["dst_of_D"] = ""
    Signal["doalu"] = 0
    Signal["ALU_func"] = ""
    Signal["move_via_S1"] = 0
    Signal["move_via_S2"] = 0
    Signal["move_via_D"] = 0
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_XOR(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_XOR"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_SHL(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_SHL"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_SHR(ctrl):
    Signal["next_is_addr"] = 0
    Signal["src_reg_is_addr"] = 0
    Signal["dst_reg_is_addr"] = 0
    Signal["branch"] = 0
    Signal["read_RF_port_1"] = 1
    Signal["read_RF_port_2"] = 1
    Signal["write_RF"] = 1
    Signal["src_of_S1"] = "RFOUT1"
    Signal["dst_of_S1"] = "A"
    Signal["src_of_S2"] = "RFOUT2"
    Signal["dst_of_S2"] = "B"
    Signal["src_of_D"] = "C"
    Signal["dst_of_D"] = "RFIN"
    Signal["doalu"] = 1
    Signal["ALU_func"] = "OP_SHR"
    Signal["move_via_S1"] = 1
    Signal["move_via_S2"] = 1
    Signal["move_via_D"] = 1
    Signal["read_memory"] = 0
    Signal["write_memory"] = 0
    Signal["dohalt"] = 0


def set_HALT(ctrl):
    Signal["dohalt"] = 1


def fetch():
    if verbose:
        eprint("[Instruction Fetch]")
    do_move_via_S1("PC", "A")
    ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
    do_move_via_D("C", "MAR")
    addr = Register["MAR"]//4
    Register["IR"] = mem[addr]
    if verbose:
        eprint("Read Instruction at ", get_hex(
            Register["MAR"]), " (", get_hex(Register["IR"]), ")")
    incPC()


def decode():
    opcode = Register["IR"] >> 24
    ctrl = (Register["IR"] >> 8) & 0xFF
    switcher = {
        0: set_ADD,
        1: set_SUB,
        2: set_NOT,
        3: set_AND,
        4: set_OR,
        5: set_XOR,
        6: set_SHL,
        7: set_SHR,
        8: set_MOVE,
        9: set_LD,
        10:set_ST,
        11:set_BR,
        12:set_HALT,
    }
    func = switcher.get(opcode)
    func(ctrl)
    if verbose:
        eprint("[Instruction Decode]")


def execute():
    if verbose:
        eprint("[Instruction Execute]")
    if (Signal["dohalt"]):
        return
    if (Signal["next_is_addr"]):
        do_move_via_S1("PC", "A")
        ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
        do_move_via_D("C", "MAR")
        do_read_memory()
        do_move_via_S1("MBR", "A")
        ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
        do_move_via_D("C", "MAR")
        incPC()
    if (Signal["src_reg_is_addr"]):
        do_read_RF_port1()
        do_move_via_S1("RFOUT1", "A")
        ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
        do_move_via_D("C", "MAR")
        do_read_memory()
    if (Signal["dst_reg_is_addr"]):
        do_read_RF_port1(shift=0)
        do_move_via_S1("RFOUT1", "A")
        ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
        do_move_via_D("C", "MAR")
    if (Signal["read_memory"]):
        do_read_memory()
    if (Signal["read_RF_port_1"]):
        do_read_RF_port1()
    if (Signal["read_RF_port_2"]):
        do_read_RF_port2()
    if (Signal["move_via_S1"]):
        do_move_via_S1(Signal["src_of_S1"], Signal["dst_of_S1"])
    if (Signal["move_via_S2"]):
        do_move_via_S1(Signal["src_of_S2"], Signal["dst_of_S2"])
    if (Signal["doalu"]):
        ALU_operation(Signal["ALU_func"], SET_FLAG)
    if (Signal["move_via_D"]):
        do_move_via_D(Signal["src_of_D"], Signal["dst_of_D"])
    if (Signal["write_RF"]):
        do_write_RF()
    if (Signal["write_memory"]):
        do_write_memory()
    if (Signal["branch"]):
        condition_code = (Register["IR"] >> 16) & 0xFF
        if (condition_code == 0):  # unconditional branch
            branch_taken = 1
        elif (condition_code == 1):  # branch if zero
            branch_taken = Register["ZERO_FLAG"]
        elif (condition_code == 2):  # branch if not zero
            branch_taken = not Register["ZERO_FLAG"]
        if (branch_taken):
            do_move_via_S1("MAR", "A")
            ALU_operation("OP_COPY", DO_NOT_SET_FLAG)
            do_move_via_D("C", "PC")


def read_program(fn):
    """
    read program from file
    """
    global nword
    i = 0
    try:
        with open(fn, "r") as f:
            content = f.read()
            content = content.replace('\n', '').replace(' ', '').strip()
            for i in range(len(content) // 8):
                mem[i] = int(content[i*8:i*8+8], 16)
            nword = i + 1
    except IOError:
        eprint("Cannot read file ", fn)
        exit()


def set_memory(addr, value):
    if addr * 4 < len(mem):
        mem[addr] = value & 0xFFFFFFFF
        return True
    return False


def read_memory(size=RAM_SIZE):
    return mem[:min(size, RAM_SIZE)]


def dump_memory():
    eprint("Content of Memory:")
    for x in range(0, nword):
        eprint(get_hex(mem[x]))


def dump_register(n):
    eprint("Content of the first ", n, " registers:")
    for x in range(0, n):
        eprint(get_hex(RF[x]))


def disassemble():
    addr = mem[Register["PC"]//4]
    IR = Register["IR"]
    op = IR >> 24
    s1 = (IR >> 16) & 0xFF
    s2 = (IR >> 8) & 0xFF
    d = IR & 0xFF
    if (op < 9):  # ALU operations
        if ((op != 2) and (op != 8)):
            eprint(opcode[op], " R", s1, ", R", s2, ", R", d)
        else:
            eprint(opcode[op], " R", s1, ", R", d)
    elif (op == 9):  # ld
        eprint(opcode[op], "R[{}]".format(s1) if s2 == 0x80 else get_hex(addr), ", R", d)
    elif (op == 10):  # st
        eprint(opcode[op], " R", s1, ", ", "R[{}]".format(d) if s2 == 0x80 else get_hex(addr))
    elif (op == 11):  # br
        condition_code = (IR >> 16) & 0xFF
        if (condition_code == 0):
            opcodebr = "BR"
        elif (condition_code == 1):
            opcodebr = "BZ"
        else:
            opcodebr = "BNZ"
        eprint(opcodebr, get_hex(addr))
    else:
        eprint(opcode[op])


def run(program):
    init()
    read_program(program)
    dump_memory()
    reset()
    while(not Signal["dohalt"]):
        if verbose:
            eprint("Executing PC at ", get_hex(Register["PC"]))
        fetch()
        decode()
        if verbose:
            eprint("IR = ", get_hex(Register["IR"]))
            disassemble()
        execute()
        if verbose:
            dump_register(14)
            if debug:
                input("Press Enter to Continue")
            print()
    eprint("Final Result:")
    dump_register(14)
    dump_memory()