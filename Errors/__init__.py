class InputError(Exception):
    #Exception raised for errors in input
    #made to call Exception on a missing Supplemental Data Table
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class MergingError(Exception):
    def __init__(self, message):
        self.message = message