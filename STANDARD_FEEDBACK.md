# Suggested improvements for standard ISO/IEC 18004:2024(en)

## Introduction

The ISO/IEC 18004:2024(en) standard text contains a number of sections that can be improved in terms of clarity,
as well as a small number of mistakes that are easily fixable. This section describes both.

Once this document is completed, we will reach out to the standards committee so they can consider these suggestions for a future edition of
ISO/IEC 18004.

## Suggested improvements


### Introduction (page vii)

In the third clause of the enumeration, it is unclear what this means:

"...the option for specifying alternative character is set to the default."

### Introduction (page vii)

In the third clause of the enumeration, a word appears to be missing.

"...which enables small to moderate amount of data to be represented ..."

should be:

"...which enables a small to moderate amount of data to be represented ..."

### Section 5.1, clause b.3 (page 4)

The default character set for byte data is defined as ISO-8859-1.

It would be useful to explicitly indicate that in the 2000 edition of
the standard,  the default encoding was JIS-8, and that this was
changed in the 2006 edition of the standard.

It would be useful to mention that, in contradiction to the standard,
many QR code decoders (e.g. those implemented on mobile phones) use
UTF-8 as the default encoding.

### Section 5.1, clause f (page 5)

It is not made clear what these percentages mean, i.e., what the precise
guarantee is for any of the four levels of error correction in terms
of error correction capabilities.
 
As stated, the most natural interpretation of the percentages would be that
they indicate that if *any* x% of the modules in the entire QR code are damaged
(inverted), the QR code  would still be readable. However, this is not the
case, as the percentage indicates the fraction of errors that can be dealt
with *per block code word* rather than for the entire QR code. This should
be made clear.

See also Section 7.5.1.

### Section 5.2, Figure 1 (page 6)

The QR code symbol used here as an example uses Data Mask Pattern 6, whereas in
earlier editions of the Standard (2000, 2006, 2015), this same example uses Data
Mask Pattern 5.

It would be useful to explicitly acknowledge this change, and explain which one
is the correct choice.

See also the comments later on about Section 7.8.3.1.

### Section 5.2, Figure 1, caption (page 6)

The caption claims the QR code example encodes the text "QR code Symbol."

In fact, the QR code example encodes the text "QR Code Symbol" (with the word
'Code' capitalized).

In the 2015 edition of the standard this was correct. This should be fixed.

### Section 7.3.1 (page 18)

It is unclear what this section is saying, precisely.

### Section 7.3.6 (page 18)

It is unclear what this section is saying, precisely.

### Section 7.4.3.2 (page 22)

The ECI designator example given is incorrect.

In ISO/IEC 8859-7, the five Greek letters Α, Β, Γ, Δ, Ε are encoded as C1 (hex) to C5 (hex).
The example given erroneously encodes them as A1 (hex) to A5 (hex).

This mistake was also present in the 2000, 2006, and 2015 editions of the standard.

It is also recommended that the resulting QR code is included in the standard.

### Section 7.4.6, Note 3, 4 (page 26)

These Notes indicate the differences between Table 6 and ISO 8859-1, especially in
regard to the lower 32 byte values.

However, Section 5.1, clause b.3 indicates that the default encoding of bytes blocks
(in absence of a preceding ECI designator) is ISO 8859-1, which leaves those 32 bytes
empty.

These statements are in contradiction. Either the default encoding is actually ISO 8859-1
(with the first 32 byte values undefined) or it is the encoding given in Table 6, where
an interpretation is assigned to the first 32 byte values.

The standard should make an unequivocal choice.

### Section 7.4.11 (page 29)

This text can be improved for readability.

"... shall be connected in order ..." should be changed to:
"... shall be concatenated in order ...".

"In certain versions of symbol ..." could be changed to:
"In certain versions of QR code symbol"

### Section 7.5.1 (page 33)

"Since QR code is a matrix symbology, a defect converting a module from dark to light or vice versa
 will result in the affected symbol character misdecoding as an apparently valid but different codeword."

This statement, in particular the part before the comma, does not make sense. The fact that module
inversion will read to a symbol character miscoding is true, but it is not "because QR code is a matrix
symbology", in any sense.

Deleting the part before the comma improves the clarity of the statement:

"A defect converting a module from dark to light or vice versa will result in the affected symbol character
 misdecoding as an apparently valid but different codeword."

### Section 7.5.1 (page 33, 34)

The explanation of the "p" value is overly complicated. Consider rewriting it for clarity.

### Section 7.5.1, Table 9 (pages 34 to 40)

The last two columns of the table are confusing, as each version's entry can
have more than the expected rows specifying the code block parameters used
for each of the four error levels (L, Q, M, H).

Consider adding horizontal separator lines in the last two columns, to show
which code lines correspond to which of the four error correction levels.

Note: the table used to be formatted like that in the 2000 and 2006 editions
of the standard. The presentation of the same information in those two editions
of the standard is much clearer because of that.

### Section 7.8.3.1 (pages 49, 50)

This section is quite unclear; it would be advisable to re-write it. it is very
hard to ascertain the intended score calculation from this description alone. 

To illustrate this, it seems that the score calculation described here does not 
explain the data mask pattern choice made in the 7 QR code symbol examples
given in the standard itself (Figure 1, Figure 29 with five examples, and Figure I.4).

This section would be much more understandable if one or two worked-out examples were
added that show the score contributions and final scores for each of the 8 data mask 
patterns. For example, this could look like this for the example shown in Figure I.4:

| Score terms       | Description                         | Pattern 0 | Pattern 1 | Pattern 2 | Pattern 3 | Pattern 4 | Pattern 5 | Pattern 6 | Pattern 7 |
|-------------------|-------------------------------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| First score term  | Adjacent modules in same row/column |           |           |           |           |           |           |           |           |
| Second score term | 2x2 blocks in the same color        |           |           |           |           |           |           |           |           |
| Third score term  | 1:1:3:1:1 patterns in row/column    |           |           |           |           |           |           |           |           |
| Fourth score term | Proportion of dark modules          |           |           |           |           |           |           |           |           |
| **Total score**   | *Lower is better*                   |           |           |           |           |           |           |           |           |

Lastly, a tiebreaker should be defined in case two data mask patterns yield an identical
score. This would ensure that, for each QR code, there is a fully deterministic and
unambiguous way of selecting the correct data mask pattern, which is very desirable.

Add statements that encoders *must* implement the data mask choice score given here,
and that decoders *should* accept QR codes with a suboptimal data mask pattern choice.

Two remarks on the score algorithm:

(1) According to the scoring procedure, the scores are determined with the version and format
information areas cleared. This is an unfortunate and sub-optimal choice. It would be better
if the standard mandated that both the version and format information were filled in when 
scoring QR codes (where the format information area is correct with respect to the data
masking pattern being scored).

(2) The fourth term in the scoring algorithm penalizes an imbalance between dark and light
squares in the QR code; but it does so in a discretized manner (10 penalty points for each
5 percents of deviation). The discretization is wholly unnecessary; the penalty could
instead be calculated as ...

### Annex A (page 69)

The definition of the generator polynomials is not correct.

"Each generator polynomial is the product of first degree polynomials: x − 2^0, x − 2^1, ..., x − 2^(n-1),
 where n is the degree of the generator polynomial."

This confuses the element of GF(8), α, with its byte representation, the byte value 2.

The correct statement is:

"Each generator polynomial is the product of first degree polynomials: x − α^0, x − α^1, ..., x − α^(n-1),
 where n is the degree of the generator polynomial."

### Annex E, Table E.1 (pages 78, 79)

The description of the marker pattern position algorithm says:

"They are spaced as evenly as possible between the timing pattern and the opposite side of the symbol, any uneven
 spacing being accommodated between the timing pattern and the first alignment pattern in the symbol interior."

Unfortunately, this doesn't provide enough information how this accommodation is implemented. A more precise
description of how this accommodation is made in cases where it is needed would be welcome. 

### Annex I.2.6 (page 90)

Incorrect statement: "... the data masking pattern is 011".

This should be replaced by: "... the data masking pattern is 010."

This makes this subsection internally consistent.

It seems that this mistake stems from the 2000 edition of the standard, where the same example was
worked out, except back then, data mask pattern 3 was chosen instead of 2. See also the comments on
section 7.8.3.1.
