import os
import sys
from typing import List
from addexports.mods import AddExportsToDunderAllCommand
import libcst.tool as tool
import typer
from pathlib import Path

app = typer.Typer(help="addexports code mod")


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

@app.command()
def mod(paths: List[Path]):

    command_instance = AddExportsToDunderAllCommand()

    files = find_init_py(paths)

    # adapted from https://github.com/Instagram/LibCST/blob/c44ff0500b52dd78716c36c7d1efd3016e20005f/libcst/tool.py#L572
    try:
        result = tool.parallel_exec_transform_with_prettyprint(
            command_instance,
            files,                  # type: ignore
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

def main(args: List[str] = sys.argv[1:]) -> None:
    app(args)


if __name__ == "__main__":
    main()
