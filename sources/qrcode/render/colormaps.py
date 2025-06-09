"""Colormaps for rendering QR codes."""

from qrcode.qr_code import ModuleValue

colormap_default = {
    ModuleValue.QUIET_ZONE_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_1: '#000000',
    ModuleValue.SEPARATOR_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_1: '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffffff',
    ModuleValue.ALIGNMENT_PATTERN_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_0: '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_FIXED_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.VERSION_INFORMATION_0: '#ffffff',
    ModuleValue.VERSION_INFORMATION_1: '#000000',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.DATA_0: '#ffffff',
    ModuleValue.DATA_1: '#000000',
    ModuleValue.ERRC_0: '#ffffff',
    ModuleValue.ERRC_1: '#000000',
    ModuleValue.REMAINDER_BIT_0: '#ffffff',
    ModuleValue.REMAINDER_BIT_1: '#000000',
    ModuleValue.DATA_ERRC_INDETERMINATE: '#ffffff',
    ModuleValue.INDETERMINATE: '#ffffff'
}

colormap_color = {
    ModuleValue.QUIET_ZONE_0: '#fff0f0',
    ModuleValue.FINDER_PATTERN_0: '#ffcccc',
    ModuleValue.FINDER_PATTERN_1: '#ff0000',
    ModuleValue.SEPARATOR_0: '#ffcccc',
    ModuleValue.TIMING_PATTERN_0: '#ffcccc',
    ModuleValue.TIMING_PATTERN_1: '#ff0000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffcccc',
    ModuleValue.ALIGNMENT_PATTERN_1: '#ff0000',
    ModuleValue.FORMAT_INFORMATION_0: '#ccffcc',
    ModuleValue.FORMAT_INFORMATION_1: '#008800',
    ModuleValue.FORMAT_INFORMATION_FIXED_1: '#ff00ff',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ccffcc',
    ModuleValue.VERSION_INFORMATION_0: '#ddddff',
    ModuleValue.VERSION_INFORMATION_1: '#0000ff',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ddddff',
    ModuleValue.DATA_0: '#eeffee',
    ModuleValue.DATA_1: '#001100',
    ModuleValue.ERRC_0: '#ffeeff',
    ModuleValue.ERRC_1: '#110033',
    ModuleValue.REMAINDER_BIT_0: '#ffffdd',
    ModuleValue.REMAINDER_BIT_1: '#555500',
    ModuleValue.DATA_ERRC_INDETERMINATE: '#777777',
    ModuleValue.INDETERMINATE: '#ff0000'
}
