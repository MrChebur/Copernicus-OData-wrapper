from datetime import datetime
from pprint import pprint

from copernicus_odata_wrapper.query import Query
from copernicus_odata_wrapper.filter import Filter
from copernicus_odata_wrapper.attributes import ProcessingLevel

if __name__ == '__main__':
    start_date = datetime(2023, 7, 2)
    end_date = datetime(2023, 7, 2)

    wkt = f'POINT(69.0 61.0)'
    # wkt = "POLYGON((69.0 61.0, 70.0 61.0, 70.0 60.0, 69.0 60.0, 69.0 61.0))"

    # setting up a filter
    f = Filter()  # create Filter instance
    f.by_sensing_date(start_date, end_date, full_day=True)  # filter by sensing dates
    f.And()  # add `and` to the end of the filter
    f.by_geographic_criteria(wkt)  # filter by coordinates
    f.And()
    f.collection('SENTINEL-2')  # filter by collection name
    f.And()

    attributes = [ProcessingLevel() == 'S2MSI1C']  # setting up attributes filter
    f.by_attribute(attributes)  # apply method `filter by attributes`

    query = Query()  # create Query instance
    query.set_filter(f)  # apply filter
    query.set_orderby('ContentDate/Start', ascending=True)  # sort results by sensing date in ascending order
    query.set_expand(attributes=True, assets=True) # show all available information
    response = query.send()  # send query

    pprint(response)
