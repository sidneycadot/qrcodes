"""Generate all examples."""

import base64
from typing import NamedTuple

import make_iso18004_examples
import make_application_examples
import make_eci_examples
import make_miscellaneous_examples

from qrcode_generator.xml_writer import XmlWriter


class ExampleCollection(NamedTuple):
    description: str
    examples: list[make_iso18004_examples.RenderedExample]


def main():

    colormap='color'
    post_optimize=True
    include_quiet_zone=False

    example_collections = [
        ExampleCollection(
            description="QR codes from the ISO/IEC 18004 Standard",
            examples=make_iso18004_examples.render(include_quiet_zone, colormap, post_optimize)
        ),
        ExampleCollection(
            description="QR codes with explicit ECI designators",
            examples=make_eci_examples.render(include_quiet_zone, colormap, post_optimize)
        ),
        ExampleCollection(
            description = "QR codes for specific applications",
            examples=make_application_examples.render(include_quiet_zone, colormap, post_optimize)
        ),
        ExampleCollection(
            description="Miscellaneous QR code examples",
            examples=make_miscellaneous_examples.render(include_quiet_zone, colormap, post_optimize)
        )
    ]

    # Generate HTML file.

    with XmlWriter("examples.html") as html:
        with html.write_container_tag("html"):
            with html.write_container_tag("head"):
                html.write_leaf_tag("title", content="Example QR codes")
                html.write_leaf_tag("meta", arguments = {"charset": "UTF-8"})
                with html.write_container_tag("style"):
                    html.write_indented_line('.qr-code img { display: block; width: 40mm; margin-left: auto; margin-right: auto; margin-top: 8mm; margin-bottom: 8mm; image-rendering: pixelated; }')
                    html.write_indented_line('.qr-code p { text-align: center; font-weight: bold; color: blue; }')
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
                                                filename = example.descriptor.png_filename
                                                canvas = example.descriptor.canvas
                                                with open(filename, "rb") as fi:
                                                    imagedata = fi.read()
                                                source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                                html.write_leaf_tag("img", arguments={"src": source})
                                                html.write_leaf_tag("p", content=f"{example.description}\n{canvas.version}-{canvas.level.name}, pattern {canvas.pattern.name[-1]}".replace("\n", "<br/>"))
                                            index += 1


if __name__ == "__main__":
    main()
