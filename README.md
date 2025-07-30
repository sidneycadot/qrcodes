QR Codes
========

This repository contains my QR-code implementation. While the encoder functionality is pretty mature, the decoder is still merely a prototype.

In particular, the decoder currently takes a binary matrix as input. For a practical encoder, it will be necessary to add pre-processing to
get from a camera image to such a binary matrix, which involves detecting finder patterns and sampling the binary matrix.
Those steps are not trivial.  

References
----------

A pretty good web-based QR-code encoder/decoder:

https://qrscanner.net

Feedback on ISO/IEC 18004:2024(en), as found on the cover of the Standard:

https://go.iso.org/customer-feedback?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdGQiOiJJU08vSUVDIDE4MDA0OjIwMjQiLCJpc3MiOiJJU08ifQ.4cn-n2MBPD_i_oNu1dZxQbD5j-rZNKq2DTTOqnPaqCY

A useful explanation of QR codes:

https://downloads.bbc.co.uk/rd/pubs/whp/whp-pdf-files/WHP031.pdf
