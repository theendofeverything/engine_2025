# Typing references

- See https://docs.python.org/3/library/typing.html
- See https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
- See https://mypy.readthedocs.io/en/stable/type_inference_and_annotations.html#type-inference-and-annotations

# Stub file references

A "stub" file is a `.pyi` (`i` is for interface), which is like a C header
file. It just lists the types and does not do include variable assignments or
function bodies.

- See https://typing.python.org/en/latest/spec/distributing.html#stub-files
- See https://typing.python.org/en/latest/spec/distributing.html#packaging-typed-libraries

# Typing with mypy

Typing does not affect the runtime.

Typing does not affect the runtime.

Mypy only gives us static type checking. This is what makes it a useful tool
for catching bugs and this is why my `lint` recipe includes `mypy`.

Mypy will only flag missing type hints when it cannot infer the type. I've only
added type hints when flagged by mypy. But you can go as crazy with type
hinting as you want. You can pretend this is a typed language and type hint
every variable.

A `tuple` is a type, but you also need to specify what types go in this tuple:

```python
    position: tuple[float, float]
```

The same goes for `list` and `dict`.

To specify multiple allowed types, OR them like this:

```python
    position: tuple[int | float, int | float]
```

To specify a callback (a function name), import `Callable` from `typing` and
use `Callable[[type_arg1, type_arg2, etc.], type_returned]`. For example, here
the callback takes an `Event` and an `int` (for the `kmod`) and returns
nothing:

```python
def subscribe(self, callback: Callable[[pygame.event.Event, int], None]) -> None:
```

