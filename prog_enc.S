BR
    start addr
0
1
2
4
8
16
32
00
00000065;inputdata
00000066
00000067
00000068
facefeed; xor data
babecafe
0d15ea5e
8badf00d
0 ; buf
0
0
0
0 ; reserved
0
0
0
0
0
0
0
0
0
start: LD N32, R1
          n32 addr
    LD N8, R2
        n8 addr
    ADD R1, R2, R3  ;R3 = R1 + R2 = 32 + 8 = 40 ; input
    LD N1, R1       ; R1 = 1
        n1 addr
    SHL R2, R1, R2 ; R2 = 8 << 1 == 16
    ADD R3, R2, R4 ; R4 = 40 + 16 == 56
    ADD R4, R2, R5 ; R5 = 56 + 16 == 72
    LD RESERVED, R0
        reserved addr
    ST R3, [R0]
    ADD R0, R1, R0
    ST R4, [R0]
    ADD R0, R1, R0
    ST R5, [R0]
    SUB R0, R0, R0   ; R0 = 0  : start
    LD n4, R1   ; R1 = 4 : step, now r2: end is still 16
        n4 addr
    BR chk_xor_end
        chk_xor_end
do_xor:     LD [R3], R8
            LD [R4], R9
            XOR R8, R9, R8
            ST R8, [R5]
            ADD R3, R1, R3
            ADD R4, R1, R4
            ADD R5, R1, R5
            ADD R0, R1, R0 ; i += 4
chk_xor_end:SUB R2, R0, R7  ; if 16 - i != 0, do again
    BNZ
    do_xor addr
    SUB R5, R2, R5  ; R5 = &buf
    MOV R2, R6
    SUB R2, R2, R2
    BR chk_mix_end
        chk_mix_end addr
do_mix:     LD [R5], R3
            MOV R3, R4
            NOT R3, R3
            SHL R3, R6, R3
            SHR R4, R6, R4
            OR R3, R4, R3
            ST R3, [R5]
            ADD R5, R1, R5
            ADD R2, R1, R2
chk_mix_end:SUB R2, R0, R7
    BNZ
        do_mix addr
    SUB R5, R6, R5
    SUB R5, R6, R3 ; R3 = &xor_data
    SUB R2, R2, R2
    BR chk_sub_end
        chk_sub_end addr
do_sub:     LD [R5], R4
            LD [R3], R8
            SUB R4, R8, R4
            ST R4, [R5]
            ADD R5, R1, R5  ; R5 += 4
            ADD R3, R1, R3  ; R3 += 4
            ADD R2, R1, R2
chk_sub_end:SUB R2, R0, R7
    BNZ
        do_sub addr
HLT

flag = my_md5(b"Pyth0n'11_s4v3_th3_w0rld")
xor = [ 0xfacefeed, 0xbabecafe, 
        0x0D15EA5E, 0x8BADF00D]
def enc(flag: str):
    assert len(flag) == 32
    groups = []
    for i in range(4):
        groups.append(int(flag[i:i+4].hex(), 16) ^ xor[i])
    for i in range(4):
        groups[i] = (~(groups[i] << 16) | groups[i] >> 16) & 0xFFFFFFFF
    for i in range(4):
        groups[i] -= xor[i]
    return groups
print(enc(flag))