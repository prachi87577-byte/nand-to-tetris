// Capstone: black 64-pixel-wide, 20-row box starting at screen row 27.
// K=27, K mod 4 = 3, so width = 16 * (3+1) = 64 pixels (4 words).
// The box begins at SCREEN + 32*27. A pressed key draws black; no key clears it.

(LOOP)
    @KBD
    D=M
    @FILL
    D;JGT
    @CLEAR
    0;JMP

(FILL)
    @R12
    M=-1
    @DRAW
    0;JMP

(CLEAR)
    @R12
    M=0

(DRAW)
    @SCREEN
    D=A
    @864
    D=D+A
    @R14
    M=D
    @20
    D=A
    @R13
    M=D

(ROW)
    @4
    D=A
    @R15
    M=D

(COL)
    @R12
    D=M
    @R14
    A=M
    M=D
    @R14
    M=M+1
    @R15
    MD=M-1
    @COL
    D;JGT

    // Skip the remaining 28 words in this screen row.
    @28
    D=A
    @R14
    M=D+M
    @R13
    MD=M-1
    @ROW
    D;JGT
    @LOOP
    0;JMP
