# PL-Practicas #

A C to x86 translator using Python and [SLY](https://pypi.org/project/sly/) for the Languaje processors subject.

## Features ##

The translator supports the following statements:

- Declaration of Global variables
- Declaration and assignment of Local Variables (basic and
- pointer types of int,char and float)
- Declaration of arrays for the previous primitive types.
- Logical, comparison and arithmetic operators
- IF-ELSE and WHILE nested sentences
- Declaration and use of functions (printf and scanf included)
- References to variables in functions

### Extras ###
- C code exceptions are managed by the translator and displayed through the console.
- The translator adds comments to make it easier to follow the resulting code.

  ```
  pushl %ebp  ;main PROLOGUE
  movl %esp, %ebp
  
  subl $4, %esp
  movl %(2), %eax
  movl %eax, -4(%ebp)
  
  ;Save return value in %eax
  movl $(0), %eax
  
  movl %ebp %esp ;main EPILOGUE
  popl %ebp
  ret
  ```

## Constrains ##

- Functions: Main has to be the last function.
- IF-ELSE and WHILE: They must have {}.
- Return: Statements of the form: return a=2; (which are accepted by C) are not considered.
- Functions without a return statement are not considered.
- There are no type-conversions
- Scanf only works with ”%d”.
- Even though float and char declarations are accepted, the x86 code for their declarations is incomplete.

## How to run ##

Enter your C file in the `Examples` folder
Run `gramatica.py`. Your file should appear in the list of files; type its name without the .c extension and enter.
If the translation was succesfully completed, your translated file should be in the `ASM` folder.
