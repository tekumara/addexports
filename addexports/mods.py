import sys
from typing import Sequence, Set

import libcst
import libcst.codemod
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

class AddExportsToDunderAllCommand(VisitorBasedCodemodCommand):

    DESCRIPTION: str = "Export imports from __init__.py in __all__"

    def __init__(self, context: CodemodContext = CodemodContext()):
        super().__init__(context)

        self.names: Set[str] = set()

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        nodenames = node.names
        if isinstance(nodenames, libcst.ImportStar):
            self.warn("from x import * not supported")
        elif isinstance(nodenames, Sequence):
            self.names.update({ia.evaluated_name for ia in nodenames})
        return

    def leave_Module(self, original_node: libcst.Module, updated_node: libcst.Module) -> libcst.Module:
        if not self.names:
            raise libcst.codemod.SkipFile("Nothing to export")

        # construct __all__
        exports = "__all__ = ['" + "', '".join(sorted(self.names)) + "']"
        new_line = libcst.parse_statement(f"\n{exports}")

        new_body = [*original_node.body, new_line]

        # reset names so they don't get carried onto the next module
        self.names = set()

        return original_node.with_changes(body=new_body)
