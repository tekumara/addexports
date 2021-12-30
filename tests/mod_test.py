import textwrap
import unittest

from libcst.codemod import CodemodTest

from addexports.mod import ExportInitImportAliasViaAllCommand


class ExportInitImportAliasViaAllCommandTests(CodemodTest):
    TRANSFORM = ExportInitImportAliasViaAllCommand

    def test_substitution(self) -> None:
        before = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2 as Task2
            """
        )
        after = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2 as Task2

            __all__ = ['Task1', 'Task2']
            """
        )

        self.assertCodemod(before, after)
