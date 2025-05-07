"""Define the RenderedExample type."""

import base64
import textwrap
from typing import NamedTuple

from qrcode_generator.utilities import QRCodePngFileDescriptor
from qrcode_generator.xml_writer import XmlWriter


class RenderHtmlExample(NamedTuple):
    description: dict[str, str]
    descriptor: QRCodePngFileDescriptor


class RenderHtmlExampleCollection(NamedTuple):
    # Possible fields:
    # - version/level/pattern
    # - ISO standard locations
    # - Short description
    # - Payload
    # - ECI designator
    # - Encoding (character set)
    #
    description: str
    examples: list[RenderHtmlExample]

def render_html_examples(filename_html: str, example_collections: list[RenderHtmlExampleCollection]) -> None:

    # Generate HTML file.

    css_style_definitions ="""
        .qr-code img { display: block; width: 40mm; margin-left: auto; margin-right: auto; margin-top: 8mm; margin-bottom: 8mm; image-rendering: pixelated; }
        .qr-code p { text-align: center; font-weight: bold; color: blue; }
    """

    with XmlWriter(filename_html) as html:
        with html.write_container_tag("html"):
            with html.write_container_tag("head"):
                html.write_leaf_tag("title", content="Example QR codes")
                html.write_leaf_tag("meta", arguments = {"charset": "UTF-8"})
                with html.write_container_tag("style"):
                    for line in textwrap.dedent(css_style_definitions).strip().splitlines():
                        html.write_indented_line(line)
            with html.write_container_tag("body"):
                html.write_leaf_tag("h1", content="Example QR codes")
                for example_collection in example_collections:
                    with html.write_container_tag("div", arguments={"class": "example-collection"}):
                        html.write_leaf_tag("h2", content=example_collection.description)
                        with html.write_container_tag("table"):
                            num_rows = (len(example_collection.examples) + 3) // 4
                            index = 0
                            for row in range(num_rows):
                                with html.write_container_tag("tr"):
                                    for col in range(4):
                                        if index < len(example_collection.examples):
                                            example = example_collection.examples[index]
                                            with html.write_container_tag("td",  arguments={"class": "qr-code"}):
                                                with open(example.descriptor.png_filename, "rb") as fi:
                                                    imagedata = fi.read()
                                                source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                                canvas = example.descriptor.canvas
                                                html.write_leaf_tag("img", arguments={"src": source})
                                                html.write_leaf_tag("p", content=f"{example.description}\n{canvas.version}-{canvas.level.name}, pattern {canvas.pattern.name[-1]}".replace("\n", "<br/>"))
                                            index += 1
