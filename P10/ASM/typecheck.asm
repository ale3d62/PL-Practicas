.text
.globl main
.type main, @function
main:


pushl %ebp   ;main PROLOGUE
movl %esp, %ebp

subl $8, %esp
1.0movl %eax, -4(%ebp)

1.0movl %eax, -8(%ebp)

10.0movl %eax, -8(%ebp)
;Save return value in %eax
movl $(0), %eax

movl %ebp %esp ;main EPILOGUE
popl %ebp
ret

