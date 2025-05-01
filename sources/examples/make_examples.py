"""Generate all examples."""
import base64
import glob
from typing import NamedTuple

import make_iso18004_examples
import make_eci_examples
import make_application_examples
import make_miscellaneous_examples

from qrcode_generator.xml_writer import XmlWriter


class ExampleCollection(NamedTuple):
    description: str
    filenames: list[str]


def main():

    colormap='color'
    post_optimize=True
    include_quiet_zone=False

    example_collections = [
        #make_iso18004_examples.main()
        #make_eci_examples.main()
        ExampleCollection(
            description = "Application Examples",
            filenames = make_application_examples.render(include_quiet_zone, colormap, post_optimize)
        ),
        ExampleCollection(
            description = "Miscellaneous Examples",
            filenames = make_miscellaneous_examples.render(include_quiet_zone, colormap, post_optimize)
        )
    ]

    with XmlWriter("examples.html") as html:
        with html.write_container_tag("html"):
            with html.write_container_tag("head"):
                html.write_leaf_tag("title", arguments={}, content="Example QR codes")
                with html.write_container_tag("style"):
                    html.write_indented_line('div.qr-code img { display: block; width: 40%; margin-left: auto; margin-right: auto; margin-top: 8mm; margin-bottom: 8mm; image-rendering: pixelated; }')
                    html.write_indented_line('div.qr-code p { text-align: center; font-weight: bold; color: blue; }')
            with html.write_container_tag("body"):
                html.write_leaf_tag("h1", content="Example QR codes")
                html.write_leaf_tag("hr")
                for example_collection in example_collections:
                    with html.write_container_tag("div", arguments={"class": "example-collection"}):
                        html.write_leaf_tag("h2", content=example_collection.description)
                        for filename in example_collection.filenames:
                            html.write_leaf_tag("hr")
                            with html.write_container_tag("div", arguments={"class": "qr-code"}):
                                with open(filename, "rb") as fi:
                                    imagedata = fi.read()
                                source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                html.write_leaf_tag("img", arguments={"src": source})
                                html.write_leaf_tag("p", content=filename)


if __name__ == "__main__":
    main()
