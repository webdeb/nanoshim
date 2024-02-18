import machine


def freq_to_str(freq):
    if (freq < 1000):
        return f"{round(freq, 2)}Hz"
    elif (freq < 1_000_000):
        return f"{round(freq / 1_000, 2)}k"
    else:
        return f"{round(freq / 1_000_000, 2)}M"


def ns_to_str(ns):
    if (ns < 1e3):
        return f"{round(ns, 1)}ns"
    elif (ns < 1e6):
        return f"{round(ns / 1e3, 2)}us"
    elif (ns < 1e9):
        return f"{round(ns / 1e6, 2)}ms"
    else:
        return f"{round(ns / 1e9, 2)}s"


def percent_str(value):
    return f"{round(value * 100, 2)}%"


def ticks_to(value, s=1e-9):
    return value * (1/machine.freq()) / s


def ticks_to_time_str(value):
    return ns_to_str(ticks_to(value))


def ticks_to_freq_str(value):
    return freq_to_str(machine.freq()/value)


def noop_0(): pass
def noop_1(a): pass
def noop_2(a, b): pass
