class UnitRenderer():
    def __init__(self, units, default=None):
        self.units = units
        self.default_unit = default or units[-1]

    def render(self, value):
        for v, u, d in self.units:
            if (value >= v):
                return f"{round(value / v, d)}{u}"

        v, u, d = self.default_unit
        return f"{round(value / v, d)}{u}"


LRenderer = UnitRenderer([
    (1, "H", 3),
    (1/1_000, "mH", 2),
    (1/1_000_000, "uH", 2)
])

FRenderer = UnitRenderer([
    (1_000_000, "MHz", 3),
    (1_000, "kHz", 3),
    (1, "Hz", 0)
])

CRenderer = UnitRenderer([
    (1, "F", 3),
    (1/1_000, "mF", 3),
    (1/1_000_000, "uF", 2),
    (1/1_000_000_000, "nF", 2),
    (1/1_000_000_000_000, "pF", 0),
])
