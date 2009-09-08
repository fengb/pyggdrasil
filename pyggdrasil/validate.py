class ValidationException(Exception): pass


class ValidationDict(object):
    def __init__(self, directives):
        self.directives = dict(directives)
        self._order = [key for (key, value) in directives]
        self._dict = {}

        for (key, value) in directives:
            # TODO: Remove isinstance
            if isinstance(value, list):
                self._dict[key] = ValidationDict(value)
            else:
                self._dict[key] = value.default

    def __setitem__(self, key, value):
        # TODO: Remove isinstance
        if isinstance(key, tuple):
            dict, key = self._target(key)
            dict[key] = value
        else:
            self._dict[key] = self.directives[key].validate(value)

    def __getitem__(self, key):
        # TODO: Remove isinstance
        if isinstance(key, tuple):
            dict, key = self._target(key)
            return _dict[key]
        else:
            return self._dict[key]

    def _target(self, key):
        if len(key) == 1:
            return self, key[0]
        else:
            return self[key[0]]._target(key[1:])

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._order)

    def __eq__(self, target):
        return self.dict == target.dict

    @property
    def dict(self):
        dict = {}
        for key in self:
            if isinstance(self[key], ValidationDict):
                dict[key] = self[key].dict
            else:
                dict[key] = self[key]
        return dict

    def load(self, dict):
        for key in dict:
            # TODO: Remove isinstance
            if isinstance(self[key], ValidationDict):
                self[key].load(dict[key])


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
