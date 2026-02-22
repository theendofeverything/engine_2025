See https://peps.python.org/pep-0636/

Matching multiple cases: see https://peps.python.org/pep-0636/#or-patterns

# Silly example

```python
a = 1
b = 2
c = 3

number = 2

# Get "a", "b", or "c"
match number:
    case 1:
        print("a")
    case 2:
        print("b")
    case 3:
        print("c")

# Get "c" or "not c"
match number:
    case 1 | 2:
        print("not c")
    case 3:
        print("c")
```
