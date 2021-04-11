# Comments
```
# Hello I'm a comment
```

# Function declaration
declares input variables(s) and return variable(s)

inline
```
def funcname(in: int16, in2: float32) -> out: int64:
    #Body of the function
```

breaking lines and parentheses for multiple output variables
```
def funcname(
    in1: int16,
    in2: float32
) -> (
    out1: float32, 
    out2: int8
):
    #Body of the function
```

# Expressions
## Sum
`1 + 2`
## Difference
`1 - 2`
## Product
`1 * 2`
## Division
`1 / 2`
## Power
`1 ** 2`
## Modulus
`1 % 2`
## bitwiseOr
`1 | 2`
## bitwiseAnd
`1 & 2`
## bitShiftLeft
`a << 2`
## bitShiftRight
`a >> 2`
## arc tangent
`atan(6)`



# Commands
## Declaration and Assignment
Empty Declaration
```
var1: float32
```
Declaration with assignment
```
var1: float32 = 3 + 2
```
Reassignment without declaration
```
var1 = 3 + 2
```
## cmdWrite
Write variable to register
```
register registerA <- var1
```
## rawRead
Read register to variable
```
var1 <- register registerA
```
## delay
```
delay for 500:
    #more Idented commands
```