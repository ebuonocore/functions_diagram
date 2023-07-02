class Memory:
    def __init__(self, size=10, basic_state=""):
        if size < 5:
            size = 5
        self.size = size
        self.pointer = 0
        self.bottom = size - 1
        self.top = 1
        self.states = [None] * size
        self.states[0] = basic_state

    def after(self, index):
        return (index + 1) % self.size

    def before(self, index):
        return (index - 1) % self.size

    def add(self, state):
        self.pointer = self.after(self.pointer)
        self.states[self.pointer] = state
        if self.pointer == self.top:
            self.top = self.after(self.top)
            if self.top == self.bottom:
                self.bottom = self.after(self.bottom)

    def undo(self):
        state = self.states[self.pointer]
        self.pointer = self.before(self.pointer)
        if self.pointer == self.bottom:
            self.pointer = self.after(self.pointer)
            return state
        state = self.states[self.pointer]
        return state

    def redo(self):
        state = self.states[self.pointer]
        self.pointer = self.after(self.pointer)
        if self.pointer == self.top:
            self.pointer = self.before(self.pointer)
            return state
        state = self.states[self.pointer]
        return state

    def __repr__(self):
        message = ""
        for state in self.states:
            if state is None:
                message += "_"
            else:
                message += "X"
        message += "\n"
        message += " " * self.pointer
        message += "|\n"
        message += "b:" + str(self.bottom)
        message += " p:" + str(self.pointer)
        message += " t:" + str(self.top)
        return message
