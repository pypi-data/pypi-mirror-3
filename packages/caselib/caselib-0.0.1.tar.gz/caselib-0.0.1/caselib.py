import re


class CaseVisitor(object):

    def __init__(self):
        self.functions = {}

    def __call__(self, text, *key):
        return self.functions[key](text)

    def case(self, *key):
        def deco(f):
            self.functions[key] = f
            return self
        return deco


class CaseConverter(CaseVisitor):

    def guess_route(self, src, dest, keys=None):
        if keys is None:
            keys = self.functions.keys()
        available_keys = keys[:]
        for key in keys:
            if key[0] == src:
                available_keys.remove(key)
                if key[1] == dest:
                    return [key]
                else:
                    try:
                        route = self.guess_route(key[1], dest, available_keys)
                        if route:
                            return [key] + route
                    except ValueError:
                        pass
        raise ValueError('cannot route %r to %r' % (src, dest))

    def __call__(self, text, src, dest):
        try:
            return super(CaseConverter, self).__call__(text, src, dest)
        except KeyError:
            for src, dest in self.guess_route(src, dest):
                text = self(text, src, dest)
            return text


class CaseSplitter(CaseVisitor):

    def __call__(self, text, case):
        try:
            return super(CaseSplitter, self).__call__(text, case)
        except KeyError:
            return convert(text, case, snake_case).split('_')


class Case(object):

    def __repr__(self):
        return '<%s>' % type(self).__name__


class CamelCase(Case):

    FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
    ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


class camelCase(CamelCase):

    FIRST_CAP_RE = re.compile('([a-z]+)([A-Z][a-z]+)')


class snake_case(Case): pass
class SNAKE_CASE(snake_case): pass


CamelCase = CamelCase()
camelCase = camelCase()
snake_case = snake_case()
SNAKE_CASE = SNAKE_CASE()


# synonyms of CamelCase
BumpyCaps = BumpyCase = CamelCaps = CapitalizedWords = CapWords = \
EmbededCaps = HumpBack = InterCaps = PascalCase = WikiWord = WikiCase = \
UpperCamalCase = CamelCase

# synonyms of camelCase
camelBack = compoundNames = mixedCase = nerdCaps = headlessCamelCase = \
lowerCamelCase = camelCase


convert = CaseConverter()
split = CaseSplitter()


@convert.case(CamelCase, snake_case)
def convert(text):
    s1 = CamelCase.FIRST_CAP_RE.sub(r'\1_\2', text)
    return CamelCase.ALL_CAP_RE.sub(r'\1_\2', s1).lower()


@convert.case(camelCase, snake_case)
def convert(text):
    s1 = camelCase.FIRST_CAP_RE.sub(r'\1_\2', text)
    return CamelCase.ALL_CAP_RE.sub(r'\1_\2', s1).lower()


@convert.case(CamelCase, camelCase)
def convert(text):
    return text[0].lower() + text[1:]


@convert.case(snake_case, SNAKE_CASE)
def convert(text):
    return text.upper()


@convert.case(SNAKE_CASE, snake_case)
def convert(text):
    return text.lower()


@convert.case(snake_case, CamelCase)
def convert(text):
    return ' '.join(text.split('_')).title().replace(' ', '')
