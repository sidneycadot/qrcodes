#! /usr/bin/env -S python3 -B

"""Write application example QR codes as PNG image files.

Application examples encode strings that have a format that can be recognized by QR code readers
and can trigger specific actions.
"""

import glob
import os
import textwrap
from typing import Optional

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render_pil import render_qrcode_as_pil_image
from qrcode_generator.utilities import write_optimal_qrcode, optimize_png


def main():

    # Remove stale application axample files.

    for filename in glob.glob("qrcode_application_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)

    colormap = 'default'
    post_optimize = True

    # Simple URLs to HTTP/HTTPS.
    write_optimal_qrcode(
        "http://www.example.com/",
        "qrcode_application_http_url.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "https://www.example.com/",
        "qrcode_application_https_url.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # A mailto URL (RFC 6068).
    write_optimal_qrcode(
        "mailto:john.doe@example.com?subject=This%20is%20the%20subject.&body=Hi%20there.",
        "qrcode_application_mailto.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # A geolocation URL (RFC 5870). The location given points to the Big Ben clock tower in London, UK.
    write_optimal_qrcode(
        "geo:51.5007,-0.1245",
        "qrcode_application_geolocation.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # A Wi-Fi network specification.
    write_optimal_qrcode(
        "WIFI:S:MyNetworkName;T:WPA;P:MyPassword",
        "qrcode_application_wifi.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # A telephone number.
    write_optimal_qrcode(
        "tel:+123456789",
        "qrcode_application_telephone.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # This produces QR codes with an SMS address and (optionally) a body.
    # Both "sms:" and "smsto:" prefixes appear to work.
    # The iPhone app, at least, ignores the body part.
    write_optimal_qrcode(
        "sms:+123456789",
        "qrcode_application_sms_1.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "sms:+123456789:Example Body",
        "qrcode_application_sms_2.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "sms:+123456789?body=Example%20Body",
        "qrcode_application_sms_3.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "smsto:+123456789",
        "qrcode_application_smsto_1.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "smsto:+123456789:Example Body",
        "qrcode_application_smsto_2.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "smsto:+123456789?body=Example%20Body",
        "qrcode_application_smsto_3.png",
        colormap=colormap,
        post_optimize=post_optimize
    )

    # An event (for calendar applications).

    vevent_descriptor = textwrap.dedent("""
    BEGIN:VEVENT
    SUMMARY:Fifth Solvay Conference on Physics
    DTSTART:19271024T120000
    DTEND:19271029T120000
    END:VEVENT 
    """).strip()

    write_optimal_qrcode(
        vevent_descriptor,
        "qrcode_application_vevent.png",
        colormap=colormap,
        post_optimize=True
    )

    # A vcard (for contact applications).

    vcard_descriptor = textwrap.dedent("""
    BEGIN:VCARD
    VERSION:4.0
    FN:Albert Einstein
    N:Einstein;Albert;;;Dr.
    BDAY:18790314
    GENDER:M
    END:VCARD
    """).strip()

    write_optimal_qrcode(
        vcard_descriptor,
        "qrcode_application_vcard.png",
        colormap=colormap,
        post_optimize=True
    )

    # Some more examples may be added:
    # - embedded HTML (even though it's not supported by standard QR code reader apps).
    # - embedded PNG (even though it's not supported by standard QR code reader apps).


if __name__ == "__main__":
    main()
