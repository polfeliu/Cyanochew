# Comments
```
# Hello I'm a comment
```

# Function declaration and return
declares function name and input variables(s)
```
def funcname(in1: int16,in2: float32):
    #Body of the function
```

at the end of the function there should be a return that specified which variables are returned.

```
return var1
```
the specs also supports to return list of variables
```
return [var1, var2, var3]
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