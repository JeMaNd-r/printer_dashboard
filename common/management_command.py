from abc import ABC
from typing import Callable, Union

from django.core.management.base import BaseCommand as DjangoCommand
from django.core.management.base import CommandParser


class BaseCommand(DjangoCommand, ABC):
    """BaseCommand that can be inherited and customized."""

    quiet: bool = False
    """If True, the print statements are quiet."""

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False, quiet=False):
        self.quiet = quiet
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--quiet",
            action="store_true",
            default=False,
            help="Print no information.",
        )

    def _print_s(
        self,
        txt,
        ending=None,
    ):
        """
        Print given `txt` in SUCCESS style to `self.stdout` (generally green).
        """
        self._print(txt=txt, style=self.style.SUCCESS, ending=ending)

    def _print_w(
        self,
        txt,
        ending=None,
    ):
        """
        Print given `txt` in WARNING style to `self.stdout` (generally yellow).
        """
        self._print(txt=txt, style=self.style.WARNING, ending=ending)

    def _print_e(
        self,
        txt,
        ending=None,
    ):
        """
        Print given `txt` in ERROR style to `self.stdout` (generally red).
        """
        self._print(txt=txt, style=self.style.ERROR, ending=ending)

    def _print_n(
        self,
        txt,
        ending=None,
    ):
        """
        Print given `txt` in NOTICE style to `self.stdout` (generally red, but lighter).
        """
        self._print(txt=txt, style=self.style.NOTICE, ending=ending)

    def _print(
        self,
        txt,
        style: Union[None, Callable] = None,
        ending=None,
    ):
        if self.quiet:
            return
        if style is not None:
            self.stdout.write(style(txt), ending=ending)
        else:
            self.stdout.write(txt, ending=ending)

    def confirm_action(self, message: str) -> bool:
        response = input(f"{message} (y/n): ").strip().lower()
        return response == "y"

    def handle(self, *args, **options):
        """
        Override this function to implement the command. Call
        `super().handle(*args, **options)` first in order to add parsing for
        `BaseCommand` arguments.
        """

        if options["quiet"]:
            self.quiet = True
