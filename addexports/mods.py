import sys
from typing import Sequence, Set

import libcst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

class AddExportsToDunderAllCommand(VisitorBasedCodemodCommand):

    DESCRIPTION: str = "Export imports from __init__.py in __all__"

    def __init__(self, context: CodemodContext = CodemodContext()):
        super().__init__(context)

        self.names: Set[str] = set()

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        nodenames = node.names
        if isinstance(nodenames, libcst.ImportStar):
            print("WARN: from x import * not supported", file=sys.stderr)
        elif isinstance(nodenames, Sequence):
            self.names.update({ia.evaluated_name for ia in nodenames})
        return

    def visit_Module(self, node: libcst.Module) -> None:
        print(f"\n{self.context.filename}")

    def leave_Module(self, original_node: libcst.Module, updated_node: libcst.Module) -> libcst.Module:
        if not self.names:
            return original_node

        # construct __all__
        exports = "__all__ = ['" + "', '".join(sorted(self.names)) + "']"
        new_line = libcst.parse_statement(f"\n{exports}")
        print(exports, file=sys.stderr)

        new_body = [*original_node.body, new_line]
        return original_node.with_changes(body=new_body)
