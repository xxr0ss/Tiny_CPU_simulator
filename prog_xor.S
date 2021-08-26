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
65;mydata
66
67
68
0 ; buf
0
0
0
deadbeef; var0
start: LD N2, R1
    n2 addr
LD N8, R2
    n8 addr
LD N16, R3
    n16 addr
ADD R1, R2, R2  ; R2 = 2 + 8 = 10
SHL R2, R1, R2  ; R2 <<= 2 -> 40 = mydata addr
ADD R2, R3, R3  ; R3 = 40 + 16 == 56 -> buf addr
LD N0, R0       ; R0 = i = 0
    n0 addr
BR CHK
 chk addr
DO_JOB: LD [R2], R4
        LD var0, R5
            var0 addr
        XOR R4, R5, R5; R5 = R4 ^ 0xdeadbeef
        ST R5, [R3]
        LD n4, R1
            n4 addr
        ADD R0, R1, R0
        ADD R2, R1, R2 ; R2 += 4
        ADD R3, R1, R3 ; R3 += 4
CHK: LD N16, R6
        n16 addr
    SUB R0, R6, R7
    BNZ
        DO_JOB
HLT