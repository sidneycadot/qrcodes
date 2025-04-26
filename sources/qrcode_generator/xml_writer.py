"""This module defines the XmlWriter class."""

from __future__ import annotations

import io
from typing import Optional


class XmlOpenCloseTagManager:
    """Helper class to support nested XML tags."""
    def __init__(self, svg_writer: XmlWriter, tag: str, arguments: Optional[dict[str, str]]):
        self.svg_writer = svg_writer
        self.tag = tag
        self.arguments = arguments

    def __enter__(self):
        self.svg_writer.write_open_tag(self.tag, self.arguments)

    def __exit__(self, exc_type, exc_value, traceback):
        self.svg_writer.write_close_tag(self.tag)


class XmlWriter:
    """A class to support writing of XML data."""
    def __init__(self, indent_spec: str|int = 4):
        self.buf = io.StringIO()
        self.indent_level = 0
        self.indent_string = indent_spec * " " if isinstance(indent_spec, int) else indent_spec

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _write_indented_line(self, line: str):
        """Write an indented line to the output buffer."""
        self.buf.write(self.indent_level * self.indent_string + line + "\n")

    def write_comment(self, comment: str):
        """Write a single-line comment at the current indentation level."""
        line = f"<!-- {comment} -->"
        self._write_indented_line(line)

    def write_open_tag(self, tag: str, arguments: Optional[dict[str, str]]) -> None:
        """Write a single-line open tag."""
        arguments_string = "" if arguments is None else "".join(" {}=\"{}\"".format(key, value) for (key, value) in arguments.items())
        line = f"<{tag}{arguments_string}>"
        self._write_indented_line(line)
        self.indent_level += 1

    def write_close_tag(self, tag: str) -> None:
        """Decrement the indentation level and write a single-line close tag."""
        self.indent_level -= 1
        line = f"</{tag}>"
        self._write_indented_line(line)

    def write_leaf_tag(self, tag: str, arguments: Optional[dict[str, str]], content: Optional[str]=None) -> None:
        """Write a single-line leaf tag with optional literal content."""
        arguments_string = "" if arguments is None else "".join(" {}=\"{}\"".format(key, value) for (key, value) in arguments.items())
        if content is None:
            line = f"<{tag}{arguments_string}/>"
        else:
            line = f"<{tag}{arguments_string}>{content}</{tag}>"
        self._write_indented_line(line)

    def write_container_tag(self, tag: str, arguments: Optional[dict[str, str]]=None) -> XmlOpenCloseTagManager:
        """Return a context manager that writes an open tag on entry and a close tag on exit."""
        return XmlOpenCloseTagManager(self, tag, arguments)

    def get_content(self) -> str:
        return self.buf.getvalue()
