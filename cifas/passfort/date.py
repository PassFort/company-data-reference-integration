from enum import Enum
from datetime import datetime, date


class DatePrecision(Enum):
    YEAR = 'YEAR'
    YEAR_MONTH = 'YEAR_MONTH'
    YEAR_MONTH_DAY = 'YEAR_MONTH_DAY'

    @property
    def date_format(self):
        if self is self.YEAR_MONTH_DAY:
            return '%Y-%m-%d'
        elif self is self.YEAR_MONTH:
            return '%Y-%m'
        return '%Y'


class PartialDate:
    value: date
    precision: DatePrecision

    def __init__(self, value: str, precision: DatePrecision):
        assert type(value) is str
        self.value = datetime.strptime(value, precision.date_format).date()
        self.precision = precision
    
    @classmethod
    def decode(cls, value):
        if isinstance(value, PartialDate):
            return value
        
        if value is None:
            return value

        try:
            return cls(value, DatePrecision.YEAR_MONTH_DAY)
        except ValueError:
            try:
                return cls(value, DatePrecision.YEAR_MONTH)
            except ValueError:
                return cls(value, DatePrecision.YEAR)
