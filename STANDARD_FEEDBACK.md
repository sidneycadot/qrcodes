# Suggested improvements for standard ISO/IEC 18004:2024(en)

Sidney Cadot <sidney.cadot@gmail.com>, May 2025.

## Introduction

The ISO/IEC 18004:2024(en) standard describes QR codes. The author of this document recently implemented a QR code
encoder, using the standard for guidance. To this end, the standard was studied in detail with a 'fresh pair of eyes',
without a-priori knowledge of how QR codes work.

From this close reading it became clear that the standard contains a number of sections that can be improved in
terms of clarity, as well as a small number of clear and unambiguous mistakes that are easily fixable.
This document lists both.
 
The standards committee may want to read the list of given below, and consider them as suggested improvements on the
next  possible occasion, for example, when preparing the next edition of the ISO/IEC 18004 standard.

## Suggested improvements

### Introduction (page vii)

In the third clause of the enumeration, it is unclear what this means; the sentence appears to be non-grammatical.

*[...] the option for specifying alternative character is set to the default.*

Suggestion: reword for clarity.

### Introduction (page vii)

In the third clause of the enumeration, a word appears to be missing.

*[...] which enables small to moderate amount of data to be represented [...]*

Change this to:

*[...] which enables a small to moderate amount of data to be represented [...]*

### Section 5.1, clause b.3 (page 4)

The default character set for byte data in the absence of an explicit ECI designator is defined here as ISO/IEC 8859-1.

It would be useful to explicitly indicate that in the 2000 edition of the standard, the default encoding was JIS-8,
and that this was changed to ISO/IEC 8859-1 in the 2006 edition of the standard.

Furthermore, it may be useful to mention that, in contradiction to the standard, many QR code decoders (e.g. those
implemented on mobile phones) use UTF-8 as the default encoding instead.

### Section 5.1, clause f (page 5)

It is not made clear what these percentages mean, i.e., what the precise guarantee is for any of the four levels of
error correction in terms of error correction capabilities.

As stated, the most natural interpretation of the percentages would be that they indicate that if *any* x% of the
modules in the entire QR code are damaged (inverted), the QR code would still be readable. However, this is not the
case, as the percentage indicates the fraction of errors that can be dealt with *per block code word* rather than for
the entire QR code, and on the GF(8) symbol level rather than on the bit/module level.

An unlucky set of module-level errors can, in fact, make the QR code unreadable with *far less* than the stated
percentages of module-level errors.

In any case, the precise meaning of the numbers given should be made clear, as well as what they mean in practice.

See also Section 7.5.1.

### Section 5.2, Figure 1 (page 6)

The QR code symbol used here as an example uses Data Mask Pattern 6, whereas in earlier editions of the standard
(2000, 2006, 2015), this same example uses Data Mask Pattern 5.

It would be useful to explicitly acknowledge this change, and explain which one is the correct choice.

See also the comments later on about Section 7.8.3.1.

### Section 5.2, Figure 1, caption (page 6)

The caption claims the QR code example encodes the text "QR code Symbol".

In fact, the QR code example encodes the text "QR Code Symbol" (with the word "Code" capitalized).

In earlier editions of the standard (2006, 2015) the caption was correct. This change should be reverted.

### Section 7.3.1 (page 18)

It is unclear what this section is saying, precisely.

### Section 7.3.6 (page 18)

It is unclear what this section is saying, precisely.

### Section 7.4.3.2 (page 22)

The ECI designator example given is incorrect.

In ISO/IEC 8859-7, the five Greek letters Α, Β, Γ, Δ, Ε are encoded as C1 (hex) to C5 (hex).
The example given erroneously encodes them as A1 (hex) to A5 (hex).

This mistake was also present in the 2000, 2006, and 2015 editions of the standard.

It would also be useful if an example QR code symbol that contains the encoded data
is included in the standard.

### Section 7.4.6, Note 3, 4 (page 26)

These two notes indicate the differences between Table 6 and ISO 8859-1, especially in
regard to the interpretation of  the lower 32 byte values.

However, Section 5.1, clause b.3 indicates that the default encoding of bytes blocks
(in absence of a preceding ECI designator) is ISO/IEC 8859-1, which leaves those 32 bytes
undefined.

These statements are in contradiction. Either the default encoding is actually ISO/IEC 8859-1
(with the first 32 byte values undefined) or it is the similar-but=different encoding given
in Table 6, where an  interpretation is assigned to the first 32 byte values.

The standard should make an unequivocal choice.

### Section 7.4.11 (page 29)

This text can be improved for readability.

*[...] shall be connected in order [...]*

should be changed to:

*[...] shall be concatenated in order [...]*

For clarity, the following change could be considered.

*In certain versions of symbol [...]*

could be changed to:

*In certain QR code symbol versions [...]*

### Section 7.5.1 (page 33)

*Since QR code is a matrix symbology, a defect converting a module from dark to light or vice versa
will result in the affected symbol character misdecoding as an apparently valid but different codeword.*

This statement, in particular the part before the comma, does not make sense. The fact that module
inversion will read to a symbol character misdecoding is true, but it is not "because QR code is a
matrix symbology".

Deleting the part before the comma improves the clarity of the statement:

*A defect converting a module from dark to light or vice versa will result in the affected symbol character
misdecoding as an apparently valid but different codeword.*

### Section 7.5.1 (page 33, 34)

The explanation of the "p" value is overly complicated. Consider rewriting it for clarity.

### Section 7.5.1, Table 9 (pages 34 to 40)

The last two columns of the table are confusing, as each version's entry can
have more than the expected four rows specifying the code block parameters used
for each of the four error levels (L, Q, M, H).

Consider adding horizontal separator lines in the last two columns, to show
which code lines correspond to which of the four error correction levels.

Note: the table used to be formatted like that in the corresponding tables in the 2000
and 2006 editions of the standard. The presentation of the same information in those two
editions of the standard is much clearer because of that.

### Section 7.8.3.1 (pages 49, 50)

This section is quite unclear; it would be advisable to re-write it. it is very
hard to ascertain the intended score calculation from this description alone. 

One of the more confusing sentences in this section is this:

*[...] The variables N1 to N4 represent weighted penalty scores for the undesirable features [...]*

First off, N1 to N4 are not variables, but *constants*. And they don't represent weighted penalty
scores; rather, they are merely constants used in the calculation of the four terms that make up
the final penalty score for a given symbol.

More importantly, the score calculation described in this section does not lead to the data mask
pattern choices shown in the 7 QR code symbol examples given in the standard itself (Figure 1,
Figure 29 with five examples, and Figure I.4). The table below shows the scores calculated according
to the scoring method described, for eaach of the seven QR codes found in the standard, and for each
of the eight data mask pattern choices. Also listed is the optimal choice (lowest score) and the score
used in the QR code symbol shown in the standard. *The last two columns should match, but for four out
of seven cases, they do not.*

| QR code example       | Description                            | Pattern scores P0..P7, best (lowest) in **bold** | Optimal pattern | Pattern used in standard |
|-----------------------|----------------------------------------|--------------------------------------------------|-----------------|--------------------------|
| Figure 1              | "QR Code Symbol" in 1-M symbol         | 1219,1195,1189,1182,1142,**1107**,1116,1198      | Pattern 5       | Pattern 6 (**MISMATCH**) |
| Figure 29, top        | "A..Z 0..9 A..Z" in 4-M symbol         | 1672,1684,1568,**1402**,1416,1690,1598,1624      | Pattern 3       | Pattern 4 (**MISMATCH**) |
| Figure 29, second row | Structured append mode example, 1 of 4 | **1097**,1146,1208,1174,1136,1164,1184,1128      | Pattern 0       | Pattern 0                |
| Figure 29, second row | Structured append mode example, 2 of 4 | **1095**,1192,1203,1167,1133,1178,1171,1103      | Pattern 0       | Pattern 7 (**MISMATCH**) |
| Figure 29, second row | Structured append mode example, 3 of 4 | 1119,1125,1191,1134,1196,1137,1123,**1090**      | Pattern 7       | Pattern 7                |
| Figure 29, second row | Structured append mode example, 4 of 4 | 1245,1173,1207,**1128**,1148,1155,1172,1136      | Pattern 3       | Pattern 3                |
| Figure I.4            | "01234567" in 1-M symbol               | 1153,1250,1160,**1128**,1214,1243,1153,1133      | Pattern 3       | Pattern 2 (**MISMATCH**) |

The clarity of this section could be greatly improved if one or two worked-out examples were added that show the
score contributions and final scores for each of the 8 data mask patterns. For example, this could look like this
for the example QR code discussed in Annes I and shown in Figure I.4:

| Data Mask Pattern | First score term | Second score term | Third score term | Fourth score term | Total score |
|-------------------|------------------|-------------------|------------------|-------------------|-------------|
| Pattern 0         | 182              | 171               | 800              | 0                 | 1153        |
| Pattern 1         | 216              | 234               | 800              | 0                 | 1250        |
| Pattern 2         | 235              | 195               | 720              | 10                | 1160        |
| Pattern 3         | 216              | 192               | 720              | 0                 | 1128 (BEST) |
| Pattern 4         | 217              | 237               | 760              | 0                 | 1214        |
| Pattern 5         | 245              | 220               | 760              | 10                | 1243        |
| Pattern 6         | 207              | 186               | 760              | 0                 | 1153        |
| Pattern 7         | 203              | 210               | 720              | 0                 | 1133        |

Lastly, a tiebreaker should be defined in case two data mask patterns yield an identical score.
This would ensure that, for each QR code, there is a fully deterministic and unambiguous way of selecting the
correct data mask pattern.

It is suggested that a statement be added that decoders *should* accept QR codes with a suboptimal data mask pattern
choice.

Two further remarks on the score algorithm:

(1) According to the scoring procedure, the scores are determined with the version and format information areas
cleared (light modules). This is an unfortunate and suboptimal choice for which there seems to be no good reason.
It would be better if the standard mandated that both the version and format information were fully filled in when 
scoring the data mask patterns, taking into account that the format version information changes when assessing
the eight data masking patterns in turn.

(2) The fourth term in the scoring algorithm penalizes an imbalance between dark and light
squares in the QR code; but it does so by binning the percentual deviations in "classes" of
deviation away from the ideal 50% score:

score_contribution = 10 * floor(abs(dark_count / (dark_count + light_count) * 100 - 50) / 5)

The reason for applying this discretization is unclear. A more obvious scoring calculation for the
dark/light imbalance would omit the discretization but follow the same linear penalty relation,
at two penalty points per percent of deviation:

score_contribution = floor(2 * abs(dark_count / (dark_count + light_count) * 100 - 50))

### Annex A (page 69)

The definition of the generator polynomials is not correct:

*Each generator polynomial is the product of first degree polynomials: x − 2^0, x − 2^1, ..., x − 2^(n-1),
where n is the degree of the generator polynomial.*

This confuses the element of GF(8), α, with its byte representation, the byte value 2.

The correct statement is:

*Each generator polynomial is the product of first degree polynomials: x − α^0, x − α^1, ..., x − α^(n-1),
 where n is the degree of the generator polynomial.*

### Annex E, Table E.1 (pages 78, 79)

The description of the marker pattern position algorithm says:

*They are spaced as evenly as possible between the timing pattern and the opposite side of the symbol, any uneven
spacing being accommodated between the timing pattern and the first alignment pattern in the symbol interior.*

Unfortunately, this doesn't provide enough information on how this accommodation is implemented. A more precise
description of how this accommodation is implemented in cases where it is needed would be welcome.

### Annex I.2.6 (page 90)

This subsection contains an unambiguously incorrect statement:

*[...] the data masking pattern is 011.*

This should be changed to:

*[...] the data masking pattern is 010.*

This makes this subsection internally consistent.

It seems that this mistake stems from the 2000 edition of the standard, where the same example was
worked out; except back then, data mask pattern 3 was chosen instead of 2.
section 7.8.3.1.

When updating this section to reflect that change for the 2006 edition, it appears that this particular
reference to data masking pattern 011 was missed.
