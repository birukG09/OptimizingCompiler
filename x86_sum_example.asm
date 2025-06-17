section .data
    N       dd 10
    result  dd 0

section .text
    global _start

_start:
    mov eax, 0
    mov ecx, 1
    mov ebx, [N]

sum_loop:
    add eax, ecx
    inc ecx
    cmp ecx, ebx
    jle sum_loop

    mov [result], eax

    mov eax, 1
    xor ebx, ebx
    int 0x80
