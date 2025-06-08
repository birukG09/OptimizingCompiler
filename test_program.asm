; Generated x86-64 assembly code
; Compile with: nasm -f elf64 output.asm && gcc -o program output.o

extern printf
extern exit

section .data
    print_fmt db '%d', 10, 0    ; Format string for printing integers

section .text
global _start

print_int:
    ; Print integer in rdi
    push rbp
    mov rbp, rsp
    
    ; Set up printf call
    mov rsi, rdi          ; Move integer to second argument
    mov rdi, print_fmt    ; Move format string to first argument
    xor rax, rax          ; Clear rax (no floating point args)
    call printf
    
    pop rbp
    ret

_start:
    ; Main program
    ; Print: print 8.0
    mov rdi, 8
    call print_int
    ; Print: print 16.0
    mov rdi, 16
    call print_int
    ; Print: print 12.0
    mov rdi, 12
    call print_int
    ; Print: print 36.0
    mov rdi, 36
    call print_int
    ; Print: print -5.0
    mov rdi, -5
    call print_int
    ; Print: print 10.0
    mov rdi, 10
    call print_int
    ; Print: print 15.0
    mov rdi, 15
    call print_int

    ; Exit program
    mov rdi, 0    ; Exit status
    call exit