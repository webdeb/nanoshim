def freq_to_str(freq):
    if (freq < 1000):
        return str(round(freq, 1)) + "Hz"
    if (freq < 1_000_000):
        return str(round(freq / 1_000, 2)) + "kHz"
    else:
        return str(round(freq / 1_000_000, 2)) + "MHz"
