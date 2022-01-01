from typing import List, Optional, Sequence, Set

import libcst
import libcst.matchers as m
from libcst.codemod import CodemodContext, SkipFile, VisitorBasedCodemodCommand


class AddExportsToDunderAllCommand(VisitorBasedCodemodCommand):

    DESCRIPTION: str = "Export imports from __init__.py in __all__"

    def __init__(self, context: CodemodContext = CodemodContext(), ignore: List[str] = []):
        super().__init__(context)
        self.ignore = ignore

    def visit_Module(self, node: libcst.Module) -> None:
        # parallel_exec_transform_with_prettyprint reuses a single command instance across multiple files
        # so we reset names etc. from any previous modules
        self.names: Set[str] = set()
        self.existing_dunderall: Optional[libcst.Assign] = None

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        nodenames = node.names
        if isinstance(nodenames, libcst.ImportStar):
            self.warn("from x import * not supported")
        elif isinstance(nodenames, Sequence):
            for nn in nodenames:
                # use alias if present
                name = nn.evaluated_alias or nn.evaluated_name
                if not name.startswith("_") and name not in self.ignore:
                    self.names.add(name)
        return

    def leave_Assign(self, original_node: libcst.Assign, updated_node: libcst.Assign) -> libcst.Assign:
        # if an __all__ assign statement
        node = updated_node
        if (
            m.matches(
                node,
                m.Assign(targets=[m.AssignTarget(target=m.Name("__all__"))]),
            )
            and isinstance(node.value, libcst.List)
        ):
            self.existing_dunderall = node
            existing_values = {
                e.value.value.strip("'").strip('"')
                for e in node.value.elements
                if isinstance(e.value, libcst.SimpleString)
            }

            # NB: assume we have seen all names by now
            if not self.names.symmetric_difference(existing_values):
                raise SkipFile("Already exported")

            # update assignment
            return node.with_changes(
                value=libcst.List(
                    elements=[libcst.Element(value=libcst.SimpleString(value=f"'{n}'")) for n in sorted(self.names)]
                )
            )

        # some other assignment
        return updated_node

    def leave_Module(self, original_node: libcst.Module, updated_node: libcst.Module) -> libcst.Module:
        if not self.names:
            raise SkipFile("No imports")

        if self.existing_dunderall:
            # already updated in leave_Assign
            return updated_node

        # construct and add new __all__ line
        exports = "__all__ = ['" + "', '".join(sorted(self.names)) + "']"
        dunder_all = libcst.parse_statement(f"\n{exports}")
        new_body = [*updated_node.body, dunder_all]

        return updated_node.with_changes(body=new_body)
