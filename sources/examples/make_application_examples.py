#! /usr/bin/env -S python3 -B

"""Write application example QR codes as PNG image files.

Application examples contain strings that have are recognized by programs
that decode QR codes and can trigger specific actions.

Which types of strings are recognized and handled by different programs
is not really standardized.
"""

import glob
import os
import textwrap
from typing import NamedTuple

from qrcode_generator.utilities import write_optimal_qrcode


def remove_stale_files() -> None:
    """Remove stale QR code files."""
    for filename in glob.glob("qrcode_application_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)


class ApplicationExample(NamedTuple):
    description: str
    payload: str

    def filename(self) -> str:
        return f"qrcode_application_{self.description}.png"


def render(include_quiet_zone: bool, colormap: str, post_optimize: bool) -> list[str]:
    """Render application examples."""

    examples = [
        # Simple HTTP and HTTPS URLs are usually handled by phone camera software by
        # opening the URL in the phone's web browser.
        ApplicationExample(
            description="http_url",
            payload="http://www.example.com/"
        ),
        ApplicationExample(
            description="https_url",
            payload="https://www.example.com/"
        ),
        # A mailto URL as defined in RFC 6068.
        # These can open an email programs.
        ApplicationExample(
            description="mailto",
            payload="mailto:john.doe@example.com?subject=This%20is%20the%20subject.&body=Hi%20there."
        ),
        # A geolocation URL (RFC 5870). The location given points to the Big Ben clock tower in London, UK.
        # These can open a map / route planner application.
        ApplicationExample(
            description="geolocation",
            payload="geo:51.5007,-0.1245"
        ),
        # A Wi-Fi network specification.
        # These can propose that the network specified is used for internet access.
        ApplicationExample(
            description="wifi",
            payload="WIFI:S:MyNetworkName;T:WPA;P:MyPassword"
        ),
        # A telephone number.
        # These can be handled by calling the number.
        ApplicationExample(
            description="telephone",
            payload="tel:+123456789"
        ),
        # QR codes with an SMS address and (optionally) a body.
        # Both "sms:" and "smsto:" prefixes appear to work.
        # The iPhone app, at least, ignores the body part.
        ApplicationExample(
            description="sms_1",
            payload="sms:+123456789"
        ),
        ApplicationExample(
            description="sms_2",
            payload="sms:+123456789:Example Body"
        ),
        ApplicationExample(
            description="sms_3",
            payload="sms:+123456789?body=Example%20Body"
        ),
        ApplicationExample(
            description="smsto_1",
            payload="smsto:+123456789"
        ),
        ApplicationExample(
            description="smsto_2",
            payload="smsto:+123456789:Example Body"
        ),
        ApplicationExample(
            description="smsto_3",
            payload="smsto:+123456789?body=Example%20Body"
        ),
        # An event (for calendar applications).
        # This can open a calendar management application.
        ApplicationExample(
            description="vevent",
            payload=textwrap.dedent("""
            BEGIN:VEVENT
            SUMMARY:Fifth Solvay Conference on Physics
            DTSTART:19271024T120000
            DTEND:19271029T120000
            END:VEVENT 
            """).strip()
        ),
        # A vcard (for contact applications).
        # These can open a contact management applications.
        ApplicationExample(
            description="vcard",
            payload=textwrap.dedent("""
            BEGIN:VCARD
            VERSION:4.0
            FN:Albert Einstein
            N:Einstein;Albert;;;Dr.
            BDAY:18790314
            GENDER:M
            END:VCARD
            """).strip()
        )
        # Some more examples may be added:
        # - embedded HTML (even though it's not supported by standard QR code reader apps).
        # - embedded PNG (even though it's not supported by standard QR code reader apps).
    ]

    for example in examples:
        write_optimal_qrcode(
            payload=example.payload,
            filename=example.filename(),
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            post_optimize=post_optimize
        )

    return [example.filename() for example in examples]


def main():

    include_quiet_zone=True
    colormap = 'default'
    post_optimize = True

    remove_stale_files()
    render(include_quiet_zone, colormap, post_optimize)


if __name__ == "__main__":
    main()
