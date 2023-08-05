class MockDroopy(object):

    def __init__(self, text, attributes, operators):
        self.text = text
        self.attributes = attributes
        self.operators = operators

    def __getattr__(self, attr):
        if attr in self.attributes.keys():
            return self.attributes[attr]
        elif attr in self.operators.keys():
            def wrapper(*args):
                return self.operators[attr]
            return wrapper

def _(text, attributes, operators):
    return MockDroopy(text, attributes, operators)


