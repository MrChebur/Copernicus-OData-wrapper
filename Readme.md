# Copernicus OData wrapper

This is a Python wrapper of
the [Copernicus Open Data Protocol API](https://documentation.dataspace.copernicus.eu/APIs/OData.html).

It is designed to make it easier to send requests.

> [!IMPORTANT]
> This wrapper is not intended to download data. It has no such functions.

For example, using this wrapper you can:

- Filter products by various attributes (coordinates, cloud coverage, date ranges, collection name, etc)
- Get a download url for a specific product (i.e. Sentinel-2 Level 1C product with the name
  of `S2A_MSIL1C_20230702T064631_N0509_R020_T42VWN_20230702T073123.SAFE`)

## Usage example

```
from datetime import datetime
from pprint import pprint

from query import Query
from filter import Filter
from attributes import ProcessingLevel

if __name__ == '__main__':
    start_date = datetime(2023, 7, 2)
    end_date = datetime(2023, 7, 2)
    wkt = f'POINT(69.0 61.0)'
    
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
    query.set_expand(attributes=True, assets=True)
    response = query.send()  # send query

    pprint(response)
```

<!-- This content will not appear in the rendered Markdown

**This is bold text**
_This text is italicized_
> Text that is a quote

![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://myoctocat.com/assets/images/base-octocat.svg)
 -->
