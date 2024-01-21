import machine


def freq_to_str(freq):
    if (freq < 1000):
        return "%.2fHz" % round(freq, 2)
    elif (freq < 1_000_000):
        return "%.2fk" % round(freq / 1_000, 2)
    else:
        return "%.2fM" % round(freq / 1_000_000, 2)


def ns_to_str(ns):
    if (ns < 1e3):
        return str(round(ns)) + "ns"
    elif (ns < 1e6):
        return str(round(ns / 1e3, 2)) + "us"
    elif (ns < 1e9):
        return str(round(ns / 1e6, 2)) + "ms"
    else:
        return str(round(ns / 1e9, 2)) + "s"


def percent_str(value):
    return "%.2f" % round(value * 100, 2) + "%"


def ticks_to(value, s=1e-9):
    return value * (1/machine.freq()) / s
