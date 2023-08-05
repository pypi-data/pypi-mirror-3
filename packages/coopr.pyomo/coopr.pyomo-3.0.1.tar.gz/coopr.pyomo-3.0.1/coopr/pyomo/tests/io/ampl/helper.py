class MockFixedValue:
    value = 42
    def __init__(self, v = 42):
        self.value = v
    def fixed_value(self):
        return True
