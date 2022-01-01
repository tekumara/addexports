import os
import sys
from pathlib import Path
from typing import List

import libcst
import libcst.tool as tool
import typer

from addexports.mods import AddExportsToDunderAllCommand

app = typer.Typer(help="Discover imports in __init__.py and add them to the __all__ attribute to make them public.")


def find_init_py(paths: List[Path]) -> List[Path]:
    if not paths:
        return []

    files = []

    # recurse ignoring hidden dirs (which rglob doesn't do)
    for p in paths:
        basename = os.path.basename(p)
        if p.is_file() and basename == "__init__.py":
            files.append(p)
        if p.is_dir() and (basename == "." or not basename.startswith(".")):
            files.extend(find_init_py(list(p.iterdir())))

    return files


@app.command(
    help="""
        Modify __init__.py files in path(s).

        Recurses into subdirs.
        """
)
def mod(
    paths: List[Path] = typer.Argument(default=None, help="Paths containing __init__.py file(s)"),
    ignore: List[str] = typer.Option(default=[], help="Imports to ignore (can be repeated)"),
) -> int:

    command_instance = AddExportsToDunderAllCommand(ignore=ignore)

    files = find_init_py(paths)

    # adapted from https://github.com/Instagram/LibCST/blob/c44ff0500b52dd78716c36c7d1efd3016e20005f/libcst/tool.py#L572
    try:
        result = tool.parallel_exec_transform_with_prettyprint(  # type: ignore
            command_instance, files, show_successes=True  # type: ignore
        )
    except KeyboardInterrupt:
        print("Interrupted!", file=sys.stderr)
        return 2

    # Print a fancy summary at the end.
    print(
        f"Finished codemodding {result.successes + result.skips + result.failures} files!",
        file=sys.stderr,
    )
    print(f" - Transformed {result.successes} files successfully.", file=sys.stderr)
    print(f" - Skipped {result.skips} files.", file=sys.stderr)
    print(f" - Failed to codemod {result.failures} files.", file=sys.stderr)
    print(f" - {result.warnings} warnings were generated.", file=sys.stderr)
    return 1 if result.failures > 0 else 0


@app.command(help="Print ast for a file")
def ast(file: Path) -> None:
    with open(file, "rb") as fp:
        code = fp.read()

    tree = libcst.parse_module(
        code,
        config=(libcst.PartialParserConfig()),
    )
    print(tool.dump(tree))


def main(args: List[str] = sys.argv[1:]) -> None:
    app(args)


if __name__ == "__main__":
    main()
