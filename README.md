# addexports

Discover imports in _\_\_init\_\_.py_ and add them to the `__all__` attribute to make them public.

## Why?

[PEP 008](https://www.python.org/dev/peps/pep-0008/#id50) states public interfaces can be declared using the `__all__` attribute in a module.

mypy in strict mode will detect usage of symbols that are not part of the public interface, eg:

```
error: Module "myapp" does not explicitly export attribute "Task"; implicit reexport disabled
```

Likewise pyright will give a similar error:

```
error: "Task" is not exported from module "myapp"
```

## Usage

```
Usage: addexports [OPTIONS] COMMAND [ARGS]...

  Discover imports in __init__.py and add them to the __all__ attribute to
  make them public.

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  debug  Print ast
  mod    Modify __init__.py files in path(s).
```

For example this _\_\_init\_\_.py_:

```python
from .tasks import Task1
```

will be modified to:

```python
from .tasks import Task1

__all__ = ['Task1']
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
