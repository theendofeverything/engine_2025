# Python string format specification

Say we have a number that prints 5-characters wide:

```python
>>> num=1.234
>>> print(f".....\n{num}")
.....
1.234
```

Use `:>N` to right-align `N` characters wide:

```python
>>> print(f"........\n{num:>8}")
........
   1.234
```

Make the width a variable:

```python
>>> w=8
>>> print(f"........\n{num:>{w}}")
........
   1.234
```
