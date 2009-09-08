class ValidationException(Exception): pass


class ValidationDict(object):
    def __init__(self, directives):
        self.directives = directives
        self._dict = {}

        for key in directives:
            # TODO: Remove isinstance
            if isinstance(directives[key], dict):
                self._dict[key] = ValidationDict(directives[key])
            else:
                self._dict[key] = directives[key].default

    def __setitem__(self, key, value):
        self._dict[key] = self.directives[key].validate(value)

    def __getitem__(self, key):
        return self._dict[key]


class Float(object):
    def __init__(self, default, min=None, max=None):
        self.default = default
        self.min = min
        self.max = max

    def validate(self, value):
        try:
            value = float(value)
        except ValueError:
            raise ValidationException(value)

        if self.min is not None and value < self.min:
            raise ValidationException(value)
        elif self.max is not None and value > self.max:
            raise ValidationException(value)

        return value


class Bool(object):
    def __init__(self, default):
        self.default = default

    def validate(self, value):
        if not isinstance(value, bool):
            raise ValidationException(value)
        return value
