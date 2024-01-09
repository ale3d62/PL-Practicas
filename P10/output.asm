.text
.globl factorial
.type factorial, @function
factorial:


pushl %ebp   #factorial PROLOGUE
movl %esp, %ebp

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
cmpl $0,%eax
je false2
movl $(2), %eax
movl %eax, 8(%ebp)
jmp final2
false2:

final2:
subl $4, %esp
movl $(2), %eax
movl %eax, -4(%ebp)

movl 8(%ebp),%eax

pushl %eax
movl $(7), %eax

movl %eax, %ebx
popl %eax
addl %ebx,%eax
movl %eax, 8(%ebp)

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
Call factorial
addl $8,%esp
movl %eax, -8(%ebp)

#Save return value in %eax
movl $(0), %eax

movl %ebp %esp #main EPILOGUE
popl %ebp
ret

