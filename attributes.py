from datetime import datetime


# Abstract classes:
class Attribute:
    """Abstract OData attribute"""

    def __init__(self):
        self.Name = None
        self.Value = None
        self.ValueType = None
        self.operator = None

    def prepare_odata_filter(self):
        if isinstance(self.Value, datetime):
            datetime_format = '%Y-%m-%dT%H:%M:%S.%f'
            value = self.Value.strftime(datetime_format)[:-3] + 'Z'  # microseconds are truncated to fit the format
        elif isinstance(self.Value, str):
            value = f"'{self.Value}'"
        else:
            value = self.Value

        filter_template = f"Attributes/OData.CSC.{self.ValueType}Attribute/any(" \
                          f"att:att/Name eq '{self.Name}'" \
                          f" and " \
                          f"att/OData.CSC.{self.ValueType}Attribute/Value {self.operator} {value})"
        return filter_template


class StringAttribute(Attribute):
    """Abstract OData string attribute"""

    def __init__(self):
        super().__init__()
        self.ValueType = 'String'

    def __eq__(self, other):
        if not isinstance(other, str):
            raise ValueError(f'{str} is requred, not {type(other)}')

        self.operator = 'eq'
        self.Value = other
        return self.prepare_odata_filter()


class DoubleAttribute(Attribute):
    """Abstract OData double attribute"""

    def __init__(self):
        super().__init__()
        self.ValueType = 'Double'

    def __eq__(self, other):
        if not isinstance(other, float):
            raise ValueError(f'{float} is requred, not {type(other)}')
        self.operator = 'eq'
        self.Value = other
        return self.prepare_odata_filter()

    def __lt__(self, other):
        if not isinstance(other, float):
            raise ValueError(f'{float} is requred, not {type(other)}')
        self.operator = 'lt'
        self.Value = other
        return self.prepare_odata_filter()

    def __le__(self, other):
        if not isinstance(other, float):
            raise ValueError(f'{float} is requred, not {type(other)}')
        self.operator = 'le'
        self.Value = other
        return self.prepare_odata_filter()

    def __ge__(self, other):
        if not isinstance(other, float):
            raise ValueError(f'{float} is requred, not {type(other)}')
        self.operator = 'ge'
        self.Value = other
        return self.prepare_odata_filter()

    def __gt__(self, other):
        if not isinstance(other, float):
            raise ValueError(f'{float} is requred, not {type(other)}')
        self.operator = 'gt'
        self.Value = other
        return self.prepare_odata_filter()


class IntegerAttribute(Attribute):
    """Abstract OData integer attribute"""

    def __init__(self):
        super().__init__()
        self.ValueType = 'Integer'

    def __eq__(self, other):
        if not isinstance(other, int):
            raise ValueError(f'{int} is requred, not {type(other)}')
        self.operator = 'eq'
        self.Value = other
        return self.prepare_odata_filter()

    def __lt__(self, other):
        if not isinstance(other, int):
            raise ValueError(f'{int} is requred, not {type(other)}')
        self.operator = 'lt'
        self.Value = other
        return self.prepare_odata_filter()

    def __le__(self, other):
        if not isinstance(other, int):
            raise ValueError(f'{int} is requred, not {type(other)}')
        self.operator = 'le'
        self.Value = other
        return self.prepare_odata_filter()

    def __ge__(self, other):
        if not isinstance(other, int):
            raise ValueError(f'{int} is requred, not {type(other)}')
        self.operator = 'ge'
        self.Value = other
        return self.prepare_odata_filter()

    def __gt__(self, other):
        if not isinstance(other, int):
            raise ValueError(f'{int} is requred, not {type(other)}')
        self.operator = 'gt'
        self.Value = other
        return self.prepare_odata_filter()


class DateTimeOffsetAttribute(Attribute):
    """Abstract OData datetime attribute"""

    def __init__(self):
        super().__init__()
        self.ValueType = 'DateTimeOffset'

    def __eq__(self, other):
        if not isinstance(other, datetime):
            raise ValueError(f'{datetime} is requred, not {type(other)}')
        self.operator = 'eq'
        self.Value = other
        return self.prepare_odata_filter()

    def __lt__(self, other):
        if not isinstance(other, datetime):
            raise ValueError(f'{datetime} is requred, not {type(other)}')
        self.operator = 'lt'
        self.Value = other
        return self.prepare_odata_filter()

    def __le__(self, other):
        if not isinstance(other, datetime):
            raise ValueError(f'{datetime} is requred, not {type(other)}')
        self.operator = 'le'
        self.Value = other
        return self.prepare_odata_filter()

    def __ge__(self, other):
        if not isinstance(other, datetime):
            raise ValueError(f'{datetime} is requred, not {type(other)}')
        self.operator = 'ge'
        self.Value = other
        return self.prepare_odata_filter()

    def __gt__(self, other):
        if not isinstance(other, datetime):
            raise ValueError(f'{datetime} is requred, not {type(other)}')
        self.operator = 'gt'
        self.Value = other
        return self.prepare_odata_filter()


# The actual OData classes are below:

#  todo: Not all of these classes can be requested! I took them from responses. See documentation, citation:
#   [Attribute.Name] is the attribute name which can take multiple values, depending on collection (Attachment 1 - Coming soon)
#   https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-attributes
class Authority(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'authority'


class Timeliness(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'timeliness'


class Coordinates(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'coordinates'


class OrbitNumber(IntegerAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'orbitNumber'


class ProductType(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'productType'


class EndingDateTime(DateTimeOffsetAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'endingDateTime'


class OrbitDirection(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'orbitDirection'


class OperationalMode(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'operationalMode'


class ProcessingLevel(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'processingLevel'


class BeginningDateTime(DateTimeOffsetAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'beginningDateTime'


class PlatformShortName(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'platformShortName'


class BaselineCollection(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'baselineCollection'


class InstrumentShortName(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'instrumentShortName'


class RelativeOrbitNumber(IntegerAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'relativeOrbitNumber'


class PlatformSerialIdentifier(StringAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'platformSerialIdentifier'


class CloudCover(DoubleAttribute):
    def __init__(self):
        super().__init__()
        self.Name = 'cloudCover'
