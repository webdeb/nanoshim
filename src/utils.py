def freq_to_str(freq):
    if (freq < 1000):
        return str(round(freq, 1)) + "Hz"
    elif (freq < 1_000_000):
        return str(round(freq / 1_000, 2)) + "k"
    else:
        return str(round(freq / 1_000_000, 2)) + "M"


def ns_to_str(ns):
    if (ns < 1e3):
        return str(round(ns)) + "ns"
    elif (ns < 1e6):
        return str(round(ns / 1e3, 2)) + "us"
    elif (ns < 1e9):
        return str(round(ns / 1e6, 2)) + "ms"
    else:
        return str(round(ns / 1e9, 2)) + "s"
