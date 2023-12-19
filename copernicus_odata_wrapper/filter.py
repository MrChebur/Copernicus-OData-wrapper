from datetime import datetime
from .attributes import Attribute as Atr
from .config import config


# noinspection PyMethodMayBeStatic
class Filter:

    def __init__(self, session=None, timeout=None):
        self.endpoint = config['endpoint']
        self.body = None
        self.post_request_body = None
        self.session = session
        self.timeout = timeout

    def __append(self, filter_part: str) -> None:
        """
        Adds a part of the filter to its body.
        :param filter_part: Any string
        :return: None
        """
        SPACE = ' '
        if self.body is None:
            self.body = f'{filter_part}'
        else:
            if self.body.endswith(SPACE):
                self.body += f'{filter_part}'
            else:
                self.body += f'{SPACE}{filter_part}'

    def clear(self) -> None:
        """
        Clears the filter body by setting it to None.
        :return: None
        """
        self.body = None

    def And(self) -> None:
        """
        Adds ` and ` to the end of the filter body.
        :return: None
        """
        self.__append('and')

    def Or(self) -> None:
        """
        Adds ` or ` to the end of the filter body.
        :return:
        """
        self.__append('or')

    def Not(self) -> None:
        """
        Adds ` not ` to the end of the filter body.
        :return:
        """
        self.__append('not')

    def __contains(self, name: str, flag: str) -> None:
        """
        Abstract method that is used to implement substring search by product name [contains, endswith, startswith].
        :param name: Any string that will be searched for.
        :param flag: Any of the values: [contains, endswith, startswith]
        :return:
        """
        self.__append(f"{flag}(Name,'{name}')")

    def contains(self, name) -> None:
        """
        Search for products names that CONTAIN substring. Only generates the filter body without sending it.
        :param name: substring
        :return:
        """
        self.__contains(name, flag='contains')

    def endswith(self, name) -> None:
        """
        Search for products names that ENDSWITH substring. Only generates the filter body without sending it.
        :param name: substring
        :return:
        """
        self.__contains(name, flag='endswith')

    def startswith(self, name) -> None:
        """
        Search for products names that STARTSWITH substring. Only generates the filter body without sending it.
        :param name: substring
        :return:
        """
        self.__contains(name, flag='startswith')

    def by_name(self, name: str) -> None:
        """
        To search for a specific product by its exact name. Only generates the filter body without sending it.

        :param name: A single name to be searched by.
        :return: str: A filter option.
        """
        if not isinstance(name, str):
            raise ValueError(f'The `name` parameter must be a `str`.')
        self.__append(f"Name eq '{name}'")

    def collection(self, collection: str) -> None:
        """
        Search for products within a specific collection.  Only generates the filter body without sending it.
        The following collections are currently available:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-collection-of-products
        :return: None
        """
        self.__append(f"Collection/Name eq '{collection}'")

    def by_publication_date(self, start: datetime, end: datetime, inclusive=True, full_day=False) -> None:
        """
        Search for products PUBLISHED between two dates (this is not a date of sensing). Only generates the filter body
        without sending it.
        :param start: Start date.
        :param end: End date.
        :param inclusive: If True - includes date intervals in the search query. True by default.
        :param full_day: If True - replaces the start time to 00-00-00 of the specified `start` day, and the end time
        to 23-59-59 of the specified `end` day.
        :return: None
        """
        if full_day:
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)

        datetime_format = '%Y-%m-%dT%H:%M:%S.%f'
        start_formatted = start.strftime(datetime_format)[:-3]  # microseconds are truncated to fit the format
        end_formatted = end.strftime(datetime_format)[:-3]

        if inclusive:
            operator1, operator2 = 'ge', 'le'
        else:
            operator1, operator2 = 'gt', 'lt'

        query = f"PublicationDate {operator1} {start_formatted}Z and PublicationDate {operator2} {end_formatted}Z"
        self.__append(query)

    def by_sensing_date(self, start: datetime, end: datetime, inclusive=True, full_day=False,
                        content_date_start: str = 'Start', content_date_end: str = 'Start') -> None:
        """
        Search for products ACQUIRED between two dates (this is a date of sensing).
        Only generates the filter body without sending it.

        The scene is not shotted instantly. So there are two dates ('Start', 'End') in the metadata attribute `ContentDate`.
        The `content_date_start` and `content_date_end` parameters are responsible for searching the corresponding
        attributes.

        :param start: Start date.
        :param end: End date.
        :param inclusive: If True - includes date intervals in the search query. True by default.
        :param full_day: If True - replaces the start time to 00-00-00 of the specified `start` day, and the end
        time to 23-59-59 of the specified `end` day.
        :param content_date_start: `ContentDate` metadata attributes: 'Start', 'End'
        :param content_date_end: `ContentDate` metadata attributes: 'Start', 'End'
        :return: None
        """
        CONTENT_DATE_POSSIBLE_VALUES = ['Start', 'End']

        if content_date_start not in CONTENT_DATE_POSSIBLE_VALUES:
            raise ValueError(f'The `content_date_start` permissible values are: {CONTENT_DATE_POSSIBLE_VALUES}')

        if content_date_end not in CONTENT_DATE_POSSIBLE_VALUES:
            raise ValueError(f'The `content_date_end` permissible values are: {CONTENT_DATE_POSSIBLE_VALUES}')

        if full_day:
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)

        datetime_format = '%Y-%m-%dT%H:%M:%S.%f'
        start_formatted = start.strftime(datetime_format)[:-3]  # microseconds are truncated to fit the format
        end_formatted = end.strftime(datetime_format)[:-3]

        if inclusive:
            operator1, operator2 = 'ge', 'le'
        else:
            operator1, operator2 = 'gt', 'lt'

        query = f"ContentDate/{content_date_start} {operator1} {start_formatted}Z and " \
                f"ContentDate/{content_date_end} {operator2} {end_formatted}Z"
        self.__append(query)

    def by_geographic_criteria(self, wkt_geometry: str) -> None:
        """
        To search for products intersecting the specified point or polygon.
        Disclaimers:
            MULTIPOLYGON is currently not supported.
            Polygon must start and end with the same point.
            Coordinates must be given in EPSG 4326

        :param wkt_geometry: Geometry in WKT format.
        :return: None
        """
        if 'MULTIPOLYGON' in wkt_geometry:
            raise ValueError(f'MULTIPOLYGON is currently not supported: \n{wkt_geometry}')

        query = f"OData.CSC.Intersects(area=geography'SRID=4326;{wkt_geometry}')"
        self.__append(query)

    def by_attribute(self, queries: [str] or [Atr.Attribute], join_all_with: str = ' and ') -> None:
        """
        Uses strings or `Attributes` classes to perform search for products by attributes. By default, all queries are
        joinded with `and`. If you use strings instead of [Atr.Attribute] the query setup will be completely manual
        (exept for joining with `and`).

        Example usage:
            from datetime import datetime
            import Attributes as Atr

            filter = Filter()
            queries = [
                Atr.BeginningDateTime() >= datetime(2019, 8, 1),
                Atr.BeginningDateTime() <= datetime(2019, 8, 2),
                Atr.CloudCover() < 10.0,
                Atr.ProductType() == 'S2MSI2A',
                Atr.OrbitDirection() == 'ASCENDING',
            ]
            filter.by_attribute(queries)
            print(filter.body)

        An equivalent of:
            $filter=
            Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-08-01T00:00:00.000Z) and
            Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value le 2019-08-02T00:00:00.000Z) and
            Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.0) and
            Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and
            Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'ASCENDING')

        :param queries: queries to be joined
        :param join_all_with: a string to join queries with (by default ' and ')
        :return:
        """
        self.__append(join_all_with.join(queries))
