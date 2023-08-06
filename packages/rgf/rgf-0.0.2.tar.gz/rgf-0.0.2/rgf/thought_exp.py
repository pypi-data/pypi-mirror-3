spec_context_stack = []

class ExampleGroup(object):
    def __init__(self):
        self.examples = []
        self.nested_example_groups = []

    def before(self):
        pass

    def add_example(self, description, spec_func):
        self.examples.append(Example(description, spec_func))

    def __enter__(self):
        spec_context_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # spec_context_stack.pop(-1)
        return True

class Example(object):
    def __init__(self, description, spec_func):
        self.description = description
        self.spec_func = spec_func

def describe(description):
    eg = ExampleGroup()
    eg.description = description
    return eg

def it(description):
    def example_creator(spec_func):
        print "HELLO: %s" % spec_func
        print "STACKY: %s" % spec_context_stack[-1]
        spec_context_stack[-1].add_example(description, spec_func)
    return example_creator
