
class TimeFactor:

    def __init__(self, value=0):
        self.value = value

    def incr(self, value):
        self.value += value

    def decr(self, value):
        self.value -= value

    def set(self, value):
        self.value = value

    def __bool__(self):
        return self.value > 0

    def __add__(self, other):
        self.value += other
        return self

    def __sub__(self, other):
        self.value -= other
        return self
