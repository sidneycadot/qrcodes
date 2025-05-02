"""Define the RenderedExample type."""

from typing import NamedTuple

from qrcode_generator.utilities import QRCodePngFileDescriptor


class RenderedExample(NamedTuple):
    description: str
    descriptor: QRCodePngFileDescriptor
