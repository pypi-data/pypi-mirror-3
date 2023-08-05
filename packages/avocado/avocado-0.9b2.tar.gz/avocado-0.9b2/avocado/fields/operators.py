"""
Simple set of classes that roughly map one-to-one to the operations that can
performed in the django ORM.

Each class must provide a `clean' method that checks a given `value' is of
the right length and in some cases, type.
"""
import re

from avocado.utils.iter import ins

__all__ = ('exact', 'iexact', 'contains', 'inlist', 'lt', 'gt', 'lte', 'gte',
    'between', 'null', 'notbetween', 'notexact', 'notiexact', 'doesnotcontain',
    'notinlist', 'notnull', 'MODEL_FIELD_MAP')

FIELD_LOOKUPS = re.compile(r'(i?(exact|contains|regex|startswidth|endswith)|'\
    '(gt|lt)e?|in|range|year|month|day|week_day|isnull|search)')

class Operator(object):
    short_name = ''
    verbose_name = ''
    operator = ''
    negated = False

    def __str__(self):
        if self.negated:
            return '%s (~%s)' % (self.short_name, self.operator)
        return '%s (%s)' % (self.short_name, self.operator)

    def __unicode__(self):
        return u'%s' % str(self)

    def __repr__(self):
        return str(self.__class__)

    def _get_uid(self):
        if self.negated:
            return '-%s' % self.operator
        return '%s' % self.operator
    uid = property(_get_uid)

    def stringify(self, value):
        s = '<b>%s</b>'
        if value is None:
            if self.negated:
                value = 'has any value'
            else:
                value = 'has no value'
        elif type(value) is bool:
            value = value and 'Yes' or 'No'
        else:
            value = str(value)

        return s % value

    def check(self, value):
        pass

    def text(self, value):
        pass


class PrimitiveOperator(Operator):
    def check(self, value):
        if not ins(value):
            return True
        return False

    def text(self, value):
        value = self.stringify(value)
        return '%s %s' % (self.verbose_name, value)


class SequenceOperator(Operator):
    def check(self, value):
        if ins(value):
            return True
        return False

    def text(self, value):
        value = map(self.stringify, value)
        if len(value) == 1:
            return '%s %s' % (Exact.verbose_name, value[0])
        return '%s %s' % (self.verbose_name,
            ' or '.join(value))


class Exact(PrimitiveOperator):
    "Only used with boolean fields. Use `iexact' otherwise."
    short_name = '='
    verbose_name = 'is equal to'
    operator = 'exact'
exact = Exact()


class iExact(PrimitiveOperator):
    short_name = '='
    verbose_name = 'is equal to'
    operator = 'iexact'
iexact = iExact()


class Contains(PrimitiveOperator):
    short_name = 'contains'
    verbose_name = 'contains the text'
    operator = 'icontains'
contains = Contains()


class LessThan(PrimitiveOperator):
    short_name = '<'
    verbose_name = 'is less than'
    operator = 'lt'
lt = LessThan()


class GreaterThan(PrimitiveOperator):
    short_name = '>'
    verbose_name = 'is greater than'
    operator = 'gt'
gt = GreaterThan()


class LessThanOrEqual(PrimitiveOperator):
    short_name = '<='
    verbose_name = 'is less than or equal to'
    operator = 'lte'
lte = LessThanOrEqual()


class GreaterThanOrEqual(PrimitiveOperator):
    short_name = '>='
    verbose_name = 'is greater than or equal to'
    operator = 'gte'
gte = GreaterThanOrEqual()


class Null(PrimitiveOperator):
    short_name = 'is null'
    verbose_name = 'is null'
    operator = 'isnull'

    def text(self, value):
        "Do not return operator"
        return self.stringify(None)
null = Null()


class InList(SequenceOperator):
    short_name = 'in list'
    verbose_name = 'is either'
    operator = 'in'

    def text(self, value):
        value = map(self.stringify, value)
        if len(value) == 1:
            return '%s %s' % (Exact.verbose_name, value[0])
        value = ', '.join(value[:-1]) + ' or %s' % value[-1]
        return '%s %s' % (self.verbose_name, value)


inlist = InList()


class Between(SequenceOperator):
    short_name = 'between'
    verbose_name = 'is between'
    operator = 'range'

    def check(self, value):
        if ins(value) and len(value) == 2:
            return True
        return False

    def text(self, value):
        value = map(self.stringify, value)
        return '%s %s' % (self.verbose_name,
            ' and '.join(value))
between = Between()


class NotBetween(Between):
    short_name = 'not between'
    verbose_name = 'is not between'
    negated = True
notbetween = NotBetween()


class NotExact(Exact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True
notexact = NotExact()


class NotiExact(iExact):
    short_name = '!='
    verbose_name = 'is not equal to'
    negated = True
notiexact = NotiExact()


class DoesNotContain(Contains):
    short_name = 'does not contain'
    verbose_name = 'does not contain'
    negated = True
doesnotcontain = DoesNotContain()


class NotInList(InList):
    short_name = 'not in list'
    verbose_name = 'is not'
    negated = True
notinlist = NotInList()


class NotNull(Null):
    short_name = 'not null'
    verbose_name = 'is not null'
    negated = True
notnull = NotNull()

NULL_OPERATORS = (null, notnull)
GENERAL_OPERATORS = (inlist, notinlist, exact, notexact)

CHAR_OPERATORS = GENERAL_OPERATORS + NULL_OPERATORS + (iexact, notiexact,
    contains, doesnotcontain)

NUMERIC_OPERATORS = GENERAL_OPERATORS + NULL_OPERATORS + (lt, lte, gt, gte,
    between, notbetween)

MODEL_FIELD_MAP = {
    'AutoField': GENERAL_OPERATORS,
    'CharField': CHAR_OPERATORS,
    'TextField': CHAR_OPERATORS,
    'IntegerField': NUMERIC_OPERATORS,
    'FloatField': NUMERIC_OPERATORS,
    'DecimalField': NUMERIC_OPERATORS,
    'DateField': NUMERIC_OPERATORS,
    'DateTimeField': NUMERIC_OPERATORS,
    'TimeField': NUMERIC_OPERATORS,
    'BooleanField': GENERAL_OPERATORS,
    'NullBooleanField': NULL_OPERATORS + GENERAL_OPERATORS
}
