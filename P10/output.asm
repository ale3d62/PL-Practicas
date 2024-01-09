.text
.globl main
.type main, @function
main:


pushl %ebp   #main PROLOGUE
movl %esp, %ebp

subl $8, %esp

movl $(2), %eax
movl %eax, -4(%ebp)
movl %eax, -8(%ebp)

movl -4(%ebp),%eax

pushl %eax
movl -4(%ebp),%eax

movl %eax,%ebx
popl %eax
immull %ebx,%eax

pushl %eax
movl -4(%ebp),%eax

pushl %eax
movl $(2), %eax

movl %eax,%ebx
popl %eax
cdq
divl %ebx

movl %eax, %ebx
popl %eax
addl %ebx,%eax

pushl %eax
movl $(4), %eax

movl %eax, %ebx
popl %eax
subl %ebx,%eax
movl %eax, -8(%ebp)
#Save return value in %eax
movl $(0), %eax

movl %ebp %esp #main EPILOGUE
popl %ebp
ret

