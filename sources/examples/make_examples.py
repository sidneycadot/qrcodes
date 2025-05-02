"""Generate all examples, then render a big HTML page containing them all."""

import make_iso18004_examples
import make_application_examples
import make_eci_examples
import make_miscellaneous_examples

from render_html_examples import render_html_examples, RenderableExampleCollection


def main():

    colormap='color'
    optimize_png=True
    include_quiet_zone=False

    example_collections = [
        RenderableExampleCollection(
            description="QR codes from the ISO/IEC 18004 Standard",
            examples=make_iso18004_examples.render(include_quiet_zone, colormap, optimize_png)
        ),
        RenderableExampleCollection(
            description="QR codes with explicit ECI designators",
            examples=make_eci_examples.render(include_quiet_zone, colormap, optimize_png)
        ),
        RenderableExampleCollection(
            description = "QR codes for specific applications",
            examples=make_application_examples.render(include_quiet_zone, colormap, optimize_png)
        ),
        RenderableExampleCollection(
            description="Miscellaneous QR code examples",
            examples=make_miscellaneous_examples.render(include_quiet_zone, colormap, optimize_png)
        )
    ]

    render_html_examples("examples.html", example_collections)


if __name__ == "__main__":
    main()
