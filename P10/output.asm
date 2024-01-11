.comm h 4 4
.comm g 4 4
.comm e 4 4
.text
.globl f
.type f, @function
f:


pushl %ebp   #f PROLOGUE
movl %esp, %ebp

subl $4, %esp
movl $(2), %eax
movl %eax, -4(%ebp)

;IF CODE
;NEQ OPERAND
movl 8(%ebp),%eax

pushl %eax
movl $(0), %eax

movl %eax,%ebx
popl %eax
cmpl %ebx,%eax
je false1
movl $1,%eax
j final1
false1:
movl $0,%eax
final1:
;END NEQ OPERAND
cmpl $0,%eax
je false2
movl $(2), %eax
movl %eax, 8(%ebp)
jmp final2
false2:

final2:
;END IF CODE
pushl Escriba un numero
Call printf
addl $4,%esp
leal 8(%ebp),%eax
 
 pushl %eax
pushl %d
Call scanf
addl $8,%esp
movl 8(%ebp),%eax
 
 pushl %eax
pushl Ha escrito: %d
Call printf
addl $8,%esp
#Save return value in %eax
movl 8(%ebp),%eax

movl %ebp %esp #f EPILOGUE
popl %ebp
ret

.text
.globl main
.type main, @function
main:


pushl %ebp   #main PROLOGUE
movl %esp, %ebp

subl $4, %esp
movl $(2), %eax
movl %eax, -4(%ebp)

subl $8, %esp
leal h, %eax
pushl %eax
movl $(1), %eax
pushl %eax
Call f
addl $8,%esp
movl %eax, -8(%ebp)

#Save return value in %eax
movl $(0), %eax

movl %ebp %esp #main EPILOGUE
popl %ebp
ret

