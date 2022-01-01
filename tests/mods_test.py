import textwrap

import pytest
from libcst import PartialParserConfig, parse_module
from libcst.codemod import CodemodContext, CodemodTest, SkipFile

from addexports.mods import AddExportsToDunderAllCommand


class AddExportsToDunderAllTest(CodemodTest):
    TRANSFORM = AddExportsToDunderAllCommand

    def test_substitution(self) -> None:
        before = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2

            # use alias name
            from .tasks import TASK3 as Task3

            # treat as private because of underscore
            from .tasks import Task4 as _Task4

            # ignore
            from .tasks import Task5 as Task5

            """
        )
        after = textwrap.dedent(
            """
            import features
            from .tasks import Task1, Task2

            # use alias name
            from .tasks import TASK3 as Task3

            # treat as private because of underscore
            from .tasks import Task4 as _Task4

            # ignore
            from .tasks import Task5 as Task5

            __all__ = ['Task1', 'Task2', 'Task3']
            """
        )

        self.assertCodemod(before, after, ignore=["Task5"])

    def test_ignore_existing_exports_single_quoted(self) -> None:
        before = textwrap.dedent(
            """
            from .tasks import Task1

            __all__ = ['Task1']
            """
        )

        with pytest.raises(SkipFile):
            self.assertCodemod(before, before)

    def test_ignore_existing_exports_double_quoted(self) -> None:
        before = textwrap.dedent(
            """
            from .tasks import Task1

            __all__ = ["Task1"]
            """
        )

        self.assertCodemod(before, before, expected_skip=True)

    def test_append_to_existing_exports(self) -> None:
        before = textwrap.dedent(
            """
            from .tasks import Task1, Task2

            __all__ = ["Task2"]
            """
        )
        after = textwrap.dedent(
            """
            from .tasks import Task1, Task2

            __all__ = ['Task1', 'Task2']
            """
        )

        self.assertCodemod(before, after)

    def test_command_reset_between_modules(self) -> None:
        # reuse single instance in the same manner as parallel_exec_transform_with_prettyprint
        transform_instance = AddExportsToDunderAllCommand(CodemodContext())

        before = textwrap.dedent(
            """
            from .tasks import Task1
            """
        )

        input_tree = parse_module(
            CodemodTest.make_fixture_data(before),
            config=(PartialParserConfig()),
        )

        transform_instance.transform_module(input_tree)

        before_skip = textwrap.dedent(
            """
            from .tasks import Task2

            __all__ = ['Task2']
            """
        )

        input_tree_skip = parse_module(
            CodemodTest.make_fixture_data(before_skip),
            config=(PartialParserConfig()),
        )

        # should skip unless it sees Task1 from first invocation
        with pytest.raises(SkipFile):
            transform_instance.transform_module(input_tree_skip)
