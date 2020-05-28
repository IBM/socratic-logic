class Theory(object):
    def __init__(self, *args):
        pass

    def entails(self, query):
        pass


class Sentence(object):
    pass


class SimpleSentence(Sentence):
    def __init__(self, formula, ranges):
        pass


class RealRange(object):
    pass


class ClosedRange(RealRange):
    def __init__(self, lower, upper):
        pass
