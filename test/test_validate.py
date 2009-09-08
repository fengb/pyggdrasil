import py.test
from pyggdrasil import validate


class TestFloat(object):
    def setup_method(self, method):
        self.validator = validate.Float(30, 12, 80)

    def test_reject_less_than_min(self):
        py.test.raises(validate.ValidationException,
                       'self.validator.validate(self.validator.min - 1)')

    def test_reject_greater_than_max(self):
        py.test.raises(validate.ValidationException,
                       'self.validator.validate(self.validator.max + 1)')


class TestBool(object):
    def setup_method(self, method):
        self.validator = validate.Bool(True)

    def test_reject_nonbool(self):
        py.test.raises(validate.ValidationException,
                       'self.validator.validate(0)')


class TestDict(object):
    def setup_method(self, method):
        self.dict = validate.ValidationDict({
            'float': validate.Float(10, 0, 19),
            'subdict': {
                'float': validate.Float(0, 0, 19),
            }
        })

    def test_dict_access(self):
        self.dict['float'] = 1
        assert self.dict['float'] == 1

    def test_subdict_access(self):
        self.dict['subdict']['float'] = 1
        assert self.dict['subdict']['float'] == 1
