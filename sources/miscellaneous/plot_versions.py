#! /usr/bin/env -S python3 -B

import matplotlib.pyplot as plt

from qrcode_generator.enum_types import ErrorCorrectionLevel
from qrcode_generator.lookup_tables import version_specification_table

data = {}
for version_specification in version_specification_table.values():
    if version_specification.error_correction_level not in data:
        data[version_specification.error_correction_level] = []
    number_of_data_codewords = version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords
    data[version_specification.error_correction_level].append((version_specification.version, number_of_data_codewords))

plotspecs = [
    (311, None),
    (312, 10),
    (313, 4)
]

for (subplotspec, xlim) in plotspecs:

    plt.subplot(subplotspec)

    for error_correction_level in ErrorCorrectionLevel:
        xy = data[error_correction_level]
        if xlim is not None:
            xy = [(x, y) for (x, y) in xy if x <= xlim]
        x, y = zip(*xy)
        plt.plot(x, y, "-*", label=error_correction_level.name)

    plt.xlabel("version")
    plt.ylabel("data capacity [bytes]")
    plt.grid()
    plt.yscale('log')
    plt.legend()

plt.show()
