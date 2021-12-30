import sys
from typing import Sequence, Set

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

class AddExportsToDunderAll(VisitorBasedCodemodCommand):

    DESCRIPTION: str = "Export imports from __init__.py in __all__"

    def __init__(self, context: CodemodContext = CodemodContext()):
        super().__init__(context)

        self.names: Set[str] = set()

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        nodenames = node.names
        if isinstance(nodenames, cst.ImportStar):
            print("WARN: from x import * not supported", file=sys.stderr)
        elif isinstance(nodenames, Sequence):
            self.names.update({ia.evaluated_name for ia in nodenames})
        return

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if not self.names:
            return original_node

        # construct __all__
        exports = "__all__ = ['" + "', '".join(sorted(self.names)) + "']"
        new_line = cst.parse_statement(f"\n{exports}")
        print(exports, file=sys.stderr)

        new_body = [*original_node.body, new_line]
        return original_node.with_changes(body=new_body)
