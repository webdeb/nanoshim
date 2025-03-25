import machine


def is_int(n):
    return isinstance(n, int)


def freq_to_str(freq):
    if (freq < 1000):
        return "{:.3f}Hz".format(freq, 3)
    elif (freq < 1_000_000):
        return "{:.3f}k".format(freq / 1_000, 3)
    else:
        return "{:.3f}M".format(freq / 1_000_000, 3)


def ns_to_str(ns):
    if (ns < 1e3):
        return "{:.1f}ns".format(ns)
    elif (ns < 1e6):
        return "{:.3f}us".format(ns / 1e3)
    elif (ns < 1e9):
        return "{:.3f}ms".format(ns / 1e6)
    else:
        return "{:.3f}s".format(ns / 1e9)


def percent_str(value):
    return "{:.2f}%".format(value * 100)


def ticks_to(value, s=1e-9):
    return value * (1/machine.freq()) / s


def ticks_to_time_str(value):
    return ns_to_str(ticks_to(value))


def ticks_to_freq_str(value, mf=None):
    mf = machine.freq() if mf is None else mf
    return freq_to_str(mf/value)


def noop_0(): pass
def noop_1(a): pass
def noop_2(a, b): pass
