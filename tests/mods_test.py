import textwrap

from libcst.codemod import CodemodTest

from addexports.mods import AddExportsToDunderAllCommand


class AddExportsToDunderAllTest(CodemodTest):
    TRANSFORM = AddExportsToDunderAllCommand

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
