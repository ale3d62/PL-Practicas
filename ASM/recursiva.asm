.text
.globl recursiva
.type recursiva, @function
recursiva:


pushl %ebp   ;recursiva PROLOGUE
movl %esp, %ebp

;IF CODE
;EQ OPERAND
movl 8(%ebp),%eax

pushl %eax
movl $(0), %eax

movl %eax,%ebx
popl %eax
cmpl %ebx,%eax
jne false1
movl $1,%eax
j final1
false1:
movl $0,%eax
final1:
;END EQ OPERAND
cmpl $0,%eax
je false2
;Save return value in %eax
movl $(0), %eax

movl %ebp %esp ;recursiva EPILOGUE
popl %ebp
ret
jmp final2
false2:
movl 8(%ebp),%eax

pushl %eax
movl $(1), %eax

movl %eax, %ebx
popl %eax
subl %ebx,%eax
movl %eax, 8(%ebp)
;Save return value in %eax
movl 8(%ebp),%eax

movl %ebp %esp ;recursiva EPILOGUE
popl %ebp
ret

final2:
;END IF CODE

.text
.globl main
.type main, @function
main:


pushl %ebp   ;main PROLOGUE
movl %esp, %ebp

subl $8, %esp
movl $(10), %eax
movl %eax, -4(%ebp)

movl -4(%ebp),%eax
pushl %eax
Call recursiva
addl $4,%esp
movl %eax, -8(%ebp)

movl -4(%ebp),%eax
 
 pushl %eax
pushl %d
Call printf
addl $8,%esp
;Save return value in %eax
movl $(0), %eax

movl %ebp %esp ;main EPILOGUE
popl %ebp
ret

