## Feedback on standard ISO/IEC 18004:2024(en)

https://go.iso.org/customer-feedback?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdGQiOiJJU08vSUVDIDE4MDA0OjIwMjQiLCJpc3MiOiJJU08ifQ.4cn-n2MBPD_i_oNu1dZxQbD5j-rZNKq2DTTOqnPaqCY

* Introduction, page vii:

  Unclear wording:

  "...the option for specifying alternative character is set to the default."

* Introduction, page vii:

  Missing word:

  "...which enables small to moderate amount of data to be represented ..."

  should be:

  "...which enables a small to moderate amount of data to be represented ..."

* Section 5.1 (b.3):

  The default character set for byte data is defined as "ISO-8859-1".

  It would be useful to indicate that in the 2000 edition of the standard,
  the default encoding was JIS-8.

  It would be useful to mention that, in contradiction to the standard,
  many QR code decoders use UTF-8 as the default encoding (and perhaps
  exhort QR code reader implementers to conform to the standard.)

* Section 5.1 (f), page 5:

  It is not clear what these percentages mean, i.e., what the precise
  guarantee is for any of the four levels of error correction in terms
  of error correction capabilities.

  See also Section 7.5.1.

* Section 5.2, Figure 1:

  The QR code symbol used here as an example uses Data Mask Pattern 6,
  whereas in earlier editions of the Standard, this same example uses Data
  Mask Pattern 5.

  Please be explicit in acknowledging this change, and explain which one is correct.

* Section 5.2, Figure 1, caption:

  The caption claims the QR code example encodes the text "QR code Symbol."

  In fact, the QR code example encodes the text "QR Code Symbol" (with the word 'Code'
  capitalized).

  In the 2015 edition of the Standard this was correct. This should be fixed.

* Section 7.3.1. is unclear.

* Study 7.3.6. It is hard to read.

* Section 7.4.3.2:

  The example is incorrect. In ISO/IEC 8859-7, the capital Greek letters
  Alpha, Beta, Gamma, Delta, end Epsilon are incoded as C1..C5 (hex).
    The example given erroneously encodes them as A1..A5 (hex).

* Study Section 7.4.6, Note 3.

* Section 7.4.11:

  "connected" --> "concatenated", "joined"

  "versions of symbol" --> "versions of QR code symbol"

* Section 7.5.1:

  "Since QR code is a matrix symbology" -- this does not make sense.

* Section 7.5.1:

  The explanation of the "p" value is complicated and does not make a lot of sense.

* Section 7.5.1, Table 9:

  The last two columns of the table are confusing, as each version's entry can
  have more than 4 rows specifying the code block parameters used.

  Consider adding horizontal seperator lines in the last two columns, to show
  which code lines correspond to which of the four error correction levels.

  Note: it used to be like that in the 2000 and 2006 editions of the standard.
    The presentation of the same information, in Tables 13--22, is much clearer.


* Section 7.8.3.

  This section is not clear at all. As evidence for this: it seems that the
  algorithm described here does not explain the choices made in the 7 QR code
  symbol examples given in the standard.

  This section really needs one or two worked-out examples that show the scores
  for  each of the 8 data patterns for a given QR code.

  Also, there is no tiebreaker defined in case two data mask patterns yield
  the same score.

* Annex A

  The definition of the generator polynomials is not correct.

* Annex E

  Document how these choices were made.

* Annex I

  Incorrect statement: "the data masking pattern is 011".

  This stems from

* 
