import textwrap

from libcst.codemod import CodemodTest

from addexports.mods import AddExportsToDunderAllCommand


class AddExportsToDunderAllTest(CodemodTest):
    TRANSFORM = AddExportsToDunderAllCommand

    def test_substitution(self) -> None:
        before = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2
            from .tasks import Task3 as Task3
            """
        )
        after = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2
            from .tasks import Task3 as Task3

            __all__ = ['Task1', 'Task2', 'Task3']
            """
        )

        self.assertCodemod(before, after)

    def test_ignore_existing_exports(self) -> None:
        before = textwrap.dedent(
            """
            from .tasks import Task1

            __all__ = ['Task1']
            """
        )
        after = textwrap.dedent(
            """
            from .tasks import Task1

            __all__ = ['Task1']
            """
        )

        self.assertCodemod(before, after)

    def test_append_to_existing_exports(self) -> None:
        before = textwrap.dedent(
            """
            from .tasks import Task1, Task2

            __all__ = ['Task2']
            """
        )
        after = textwrap.dedent(
            """
            from .tasks import Task1, Task2

            __all__ = ['Task1', 'Task2']
            """
        )

        self.assertCodemod(before, after)
