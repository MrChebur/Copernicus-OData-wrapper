import unittest
import requests
from datetime import datetime

import errors
import attributes as Atr

from query import Query
from filter import Filter
from errors import check_response_for_errors

my_country_is_banned = False
proxy_ip_port = '103.66.10.101:8080'

query_ = Query()
endpoint = query_.endpoint
session = requests.Session()

if my_country_is_banned:
    session.proxies = {'http': f'http://{proxy_ip_port}',
                       # 'https': f'https://{proxy_ip_port}'
                       }


class Testerrors(unittest.TestCase):
    maxDiff = None

    def test_errors(self):
        from requests.models import Response
        the_response = Response()

        with self.assertRaises(errors.Unknown):
            the_response._content = b'{"detail": "BlaBla_unknown"}'
            check_response_for_errors(the_response)

        with self.assertRaises(errors.Unauthorized):
            the_response._content =  b'{"detail": "Unauthorized"}'
            check_response_for_errors(the_response)

        with self.assertRaises(errors.InvalidODataPath):
            the_response._content = b'{"detail": "Invalid odata path"}'
            check_response_for_errors(the_response)

        the_response._content = b'{"NOT_detail_KEY": "some_value"}'
        self.assertEqual(check_response_for_errors(the_response), None)

        the_response._content = b'{"detail": "Unauthorized" , "another_key": "some_value2"}'
        self.assertEqual(check_response_for_errors(the_response), None)


class TestQuery(unittest.TestCase):
    maxDiff = None

    def test_Query__merge_options(self):
        # Merging occurs in the order of keywords in the dictionary:
        # self.options = {'filter': None,
        #                 'orderby': None,
        #                 'top': None,
        #                 'skip': None,
        #                 'count': None,
        #                 'expand': None,
        #                 }

        query = Query()

        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?')

        query.set_top(3)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$top=3')

        query.set_orderby('ModificationDate', False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ModificationDate desc&$top=3')

        query.set_skip(0)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ModificationDate desc&$top=3&$skip=0')

        query.set_skip(10)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ModificationDate desc&$top=3&$skip=10')

        query = Query()
        f = Filter()
        f.by_name('1')
        query.set_filter(f)
        self.assertEqual(query._Query__merge_options(), rf"{endpoint}?$filter=Name eq '1'")

        query = Query()
        f = Filter()
        f.by_name('1'), f.Or(), f.by_name('2'), f.Or(), f.by_name('3')
        query.set_filter(f)
        self.assertEqual(query._Query__merge_options(), f"{endpoint}?$filter=Name eq '1' or Name eq '2' or Name eq '3'")

    def test_orderby_option(self):
        query = Query()

        query.set_orderby('ContentDate/Start', True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ContentDate/Start asc')

        query.set_orderby('ContentDate/Start', False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ContentDate/Start desc')

        query.set_orderby('ContentDate/End', True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ContentDate/End asc')

        query.set_orderby('ContentDate/End', False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ContentDate/End desc')

        query.set_orderby('PublicationDate', True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=PublicationDate asc')

        query.set_orderby('PublicationDate', False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=PublicationDate desc')

        query.set_orderby('ModificationDate', True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ModificationDate asc')

        query.set_orderby('ModificationDate', False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$orderby=ModificationDate desc')

    def test_set_top(self):
        query = Query()
        query.set_top(3)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$top=3')

    def test_set_skip(self):
        query = Query()
        query.set_skip(10)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$skip=10')

    def test_set_count(self):
        query = Query()
        query.set_count(False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?')

        query = Query()
        query.set_count(True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$count=True')

    def test_set_expand(self):
        query = Query()

        query.set_expand(attributes=False, assets=False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?')

        query.set_expand(attributes=None, assets=None)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?')

        query.set_expand(attributes=False, assets=True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$expand=Assets')

        query.set_expand(attributes=None, assets=True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$expand=Assets')

        query.set_expand(attributes=True, assets=False)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$expand=Attributes')

        query.set_expand(attributes=True, assets=None)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$expand=Attributes')

        query.set_expand(True, True)
        self.assertEqual(query._Query__merge_options(), rf'{endpoint}?$expand=Assets&$expand=Attributes')

    def test_clear(self):
        not_clear_query = Query()
        not_clear_query.set_top(3)
        new_query = Query()
        self.assertNotEqual(new_query._Query__options, not_clear_query._Query__options)

        not_clear_query = Query()
        not_clear_query.set_top(3)
        not_clear_query.clear()
        new_query = Query()
        self.assertEqual(new_query._Query__options, not_clear_query._Query__options)

        not_clear_query = Query()
        not_clear_query.set_orderby('PublicationDate', False)
        not_clear_query.clear()
        new_query = Query()
        self.assertEqual(new_query._Query__options, not_clear_query._Query__options)

    def test_by_names(self):
        import warnings

        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        query = Query()
        names = ["S1A_IW_GRDH_1SDV_20141031T161924_20141031T161949_003076_003856_634E.SAFE",
                 "S3B_SL_1_RBT____20190116T050535_20190116T050835_20190117T125958_0179_021_048_0000_LN2_O_NT_003.SEN3",
                 ]
        response = {'@odata.context': '$metadata#Products', 'value': [
            {'@odata.mediaContentType': 'application/octet-stream', 'Id': '3392fde3-b43c-51a0-9d1b-2d7d0419eeeb',
             'Name': 'S3B_SL_1_RBT____20190116T050535_20190116T050835_20190117T125958_0179_021_048_0000_LN2_O_NT_003.SEN3',
             'ContentType': 'application/octet-stream', 'ContentLength': 0, 'OriginDate': '2019-04-21T04:33:45.860Z',
             'PublicationDate': '2019-01-17T14:21:35.996Z', 'ModificationDate': '2019-01-17T14:21:35.996Z',
             'Online': True, 'EvictionDate': '',
             'S3Path': '/eodata/Sentinel-3/SLSTR/SL_1_RBT/2019/01/16/S3B_SL_1_RBT____20190116T050535_20190116T050835_20190117T125958_0179_021_048_0000_LN2_O_NT_003.SEN3',
             'Checksum': [], 'ContentDate': {'Start': '2019-01-16T05:05:35.224Z', 'End': '2019-01-16T05:08:35.224Z'},
             'Footprint': "geography'SRID=4326;POLYGON ((-99.8521 12.4751, -100.313 12.388, -100.777 12.3112, -101.233 12.2115, -101.697 12.1314, -102.16 12.032, -102.611 11.941, -103.072 11.8565, -103.528 11.7569, -103.99 11.668, -104.447 11.5765, -104.91 11.4803, -105.359 11.38, -105.825 11.2871, -106.275 11.1902, -106.732 11.0942, -107.19 10.9981, -107.648 10.8923, -108.101 10.7952, -108.56 10.6964, -109.009 10.5992, -109.465 10.4903, -109.916 10.3915, -110.374 10.2898, -110.828 10.1887, -111.281 10.0786, -111.737 9.97639, -112.185 9.8699, -112.635 9.7633, -113.087 9.6563, -113.264 9.61438, -112.643 7.00159, -112.027 4.34324, -111.424 1.68379, -110.832 -0.976423, -110.656 -0.937215, -110.209 -0.837193, -109.759 -0.739971, -109.324 -0.633757, -108.874 -0.535691, -108.427 -0.429214, -107.978 -0.331123, -107.529 -0.23249, -107.083 -0.135197, -106.634 -0.027269, -106.192 0.069413, -105.741 0.168034, -105.295 0.265912, -104.846 0.373029, -104.397 0.471169, -103.956 0.570229, -103.505 0.669202, -103.062 0.770737, -102.614 0.872318, -102.167 0.968041, -101.715 1.07247, -101.264 1.16585, -100.827 1.27236, -100.377 1.36475, -99.9321 1.4729, -99.4775 1.56814, -99.027 1.66407, -98.5855 1.77306, -98.1318 1.86269, -97.6841 1.96183, -98.2521 4.59956, -98.8034 7.23854, -99.3392 9.87844, -99.8521 12.4751))'",
             'GeoFootprint': {'type': 'Polygon', 'coordinates': [
                 [[-99.8521, 12.4751], [-100.313, 12.388], [-100.777, 12.3112], [-101.233, 12.2115],
                  [-101.697, 12.1314], [-102.16, 12.032], [-102.611, 11.941], [-103.072, 11.8565], [-103.528, 11.7569],
                  [-103.99, 11.668], [-104.447, 11.5765], [-104.91, 11.4803], [-105.359, 11.38], [-105.825, 11.2871],
                  [-106.275, 11.1902], [-106.732, 11.0942], [-107.19, 10.9981], [-107.648, 10.8923],
                  [-108.101, 10.7952], [-108.56, 10.6964], [-109.009, 10.5992], [-109.465, 10.4903],
                  [-109.916, 10.3915], [-110.374, 10.2898], [-110.828, 10.1887], [-111.281, 10.0786],
                  [-111.737, 9.97639], [-112.185, 9.8699], [-112.635, 9.7633], [-113.087, 9.6563], [-113.264, 9.61438],
                  [-112.643, 7.00159], [-112.027, 4.34324], [-111.424, 1.68379], [-110.832, -0.976423],
                  [-110.656, -0.937215], [-110.209, -0.837193], [-109.759, -0.739971], [-109.324, -0.633757],
                  [-108.874, -0.535691], [-108.427, -0.429214], [-107.978, -0.331123], [-107.529, -0.23249],
                  [-107.083, -0.135197], [-106.634, -0.027269], [-106.192, 0.069413], [-105.741, 0.168034],
                  [-105.295, 0.265912], [-104.846, 0.373029], [-104.397, 0.471169], [-103.956, 0.570229],
                  [-103.505, 0.669202], [-103.062, 0.770737], [-102.614, 0.872318], [-102.167, 0.968041],
                  [-101.715, 1.07247], [-101.264, 1.16585], [-100.827, 1.27236], [-100.377, 1.36475],
                  [-99.9321, 1.4729], [-99.4775, 1.56814], [-99.027, 1.66407], [-98.5855, 1.77306], [-98.1318, 1.86269],
                  [-97.6841, 1.96183], [-98.2521, 4.59956], [-98.8034, 7.23854], [-99.3392, 9.87844],
                  [-99.8521, 12.4751]]]}},
            {'@odata.mediaContentType': 'application/octet-stream', 'Id': 'c23d5ffd-bc2a-54c1-a2cf-e2dc18bc945f',
             'Name': 'S1A_IW_GRDH_1SDV_20141031T161924_20141031T161949_003076_003856_634E.SAFE',
             'ContentType': 'application/octet-stream', 'ContentLength': 0, 'OriginDate': '2014-12-27T02:54:17.244Z',
             'PublicationDate': '2016-08-21T07:27:38.212Z', 'ModificationDate': '2016-08-21T07:27:38.212Z',
             'Online': True, 'EvictionDate': '',
             'S3Path': '/eodata/Sentinel-1/SAR/GRD/2014/10/31/S1A_IW_GRDH_1SDV_20141031T161924_20141031T161949_003076_003856_634E.SAFE',
             'Checksum': [], 'ContentDate': {'Start': '2014-10-31T16:19:24.221Z', 'End': '2014-10-31T16:19:49.219Z'},
             'Footprint': "geography'SRID=4326;POLYGON ((19.165325 54.983635, 23.194235 55.39806, 23.592987 53.904648, 19.706837 53.49408, 19.165325 54.983635))'",
             'GeoFootprint': {'type': 'Polygon', 'coordinates': [
                 [[19.165325, 54.983635], [23.194235, 55.39806], [23.592987, 53.904648], [19.706837, 53.49408],
                  [19.165325, 54.983635]]]}}]}
        self.assertEqual(query.by_names(names), response)

        query = Query()
        names = []
        result = query.by_names(names)
        response = {'@odata.context': '$metadata#Products', 'value': []}

        self.assertEqual(result, response)

    def test_product_nodes(self):
        query = Query()
        query.session = session

        result = {"result":
            [
                {"Id": "S2A_MSIL1C_20180927T051221_N0206_R033_T42FXL_20180927T073143.SAFE",
                 "Name": "S2A_MSIL1C_20180927T051221_N0206_R033_T42FXL_20180927T073143.SAFE",
                 "ContentLength": 0,
                 "ChildrenNumber": 9,
                 "Nodes": {
                     "uri": "https://zipper.dataspace.copernicus.eu/odata/v1/Products(db0c8ef3-8ec0-5185-a537-812dad3c58f8)/Nodes(S2A_MSIL1C_20180927T051221_N0206_R033_T42FXL_20180927T073143.SAFE)/Nodes"}
                 }
            ]
        }

        uiid = 'db0c8ef3-8ec0-5185-a537-812dad3c58f8'
        self.assertEqual(query.product_nodes(uiid), result)

        url = 'https://catalogue.dataspace.copernicus.eu/odata/v1/Products(db0c8ef3-8ec0-5185-a537-812dad3c58f8)'
        self.assertEqual(query.product_nodes(url), result)


class TestFilter(unittest.TestCase):
    maxDiff = None

    def test_clear(self):
        f = Filter()
        f.body = 'VALUE'
        f.clear()
        self.assertEqual(f.body, None)

    def test_And(self):
        f = Filter()
        f.And()
        self.assertEqual(f.body, f'and')

    def test_Or(self):
        f = Filter()
        f.Or()
        self.assertEqual(f.body, f'or')

    def test_Not(self):
        f = Filter()
        f.Not()
        self.assertEqual(f.body, f'not')

    def test_contains(self):
        f = Filter()
        VALUE = 'VALUE'
        f.contains(VALUE)
        self.assertEqual(f.body, f"contains(Name,'{VALUE}')")

    def test_endswith(self):
        f = Filter()
        VALUE = 'VALUE'
        f.endswith(VALUE)
        self.assertEqual(f.body, f"endswith(Name,'{VALUE}')")

    def test_startswith(self):
        f = Filter()
        VALUE = 'VALUE'
        f.startswith(VALUE)
        self.assertEqual(f.body, f"startswith(Name,'{VALUE}')")

    def test_by_name(self):
        f = Filter()
        VALUE = 'VALUE'
        f.by_name(VALUE)
        self.assertEqual(f.body, f"Name eq '{VALUE}'")

    def test_collection(self):
        f = Filter()
        VALUE = 'VALUE'
        f.collection(VALUE)
        self.assertEqual(f.body, f"Collection/Name eq '{VALUE}'")

    def test_by_publication_date(self):
        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = True
        full_day = True
        f.by_publication_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'PublicationDate ge 2020-01-01T00:00:00.000Z and PublicationDate le 2020-01-02T23:59:59.999Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = True
        full_day = False
        f.by_publication_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'PublicationDate ge 2020-01-01T00:00:00.000Z and PublicationDate le 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = True
        f.by_publication_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'PublicationDate gt 2020-01-01T00:00:00.000Z and PublicationDate lt 2020-01-02T23:59:59.999Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        f.by_publication_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'PublicationDate gt 2020-01-01T00:00:00.000Z and PublicationDate lt 2020-01-02T00:00:00.000Z')

    def test_by_sensing_date(self):
        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = True
        full_day = True

        f.by_sensing_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         f'ContentDate/Start ge 2020-01-01T00:00:00.000Z and ContentDate/Start le 2020-01-02T23:59:59.999Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = True
        full_day = False
        f.by_sensing_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'ContentDate/Start ge 2020-01-01T00:00:00.000Z and ContentDate/Start le 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = True
        f.by_sensing_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'ContentDate/Start gt 2020-01-01T00:00:00.000Z and ContentDate/Start lt 2020-01-02T23:59:59.999Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        f.by_sensing_date(start, end, inclusive, full_day)
        self.assertEqual(f.body,
                         'ContentDate/Start gt 2020-01-01T00:00:00.000Z and ContentDate/Start lt 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        content_date_start = 'End'
        content_date_end = 'End'
        f.by_sensing_date(start, end, inclusive, full_day, content_date_start, content_date_end)
        self.assertEqual(f.body,
                         'ContentDate/End gt 2020-01-01T00:00:00.000Z and ContentDate/End lt 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        content_date_start = 'End'
        content_date_end = 'Start'
        f.by_sensing_date(start, end, inclusive, full_day, content_date_start, content_date_end)
        self.assertEqual(f.body,
                         'ContentDate/End gt 2020-01-01T00:00:00.000Z and ContentDate/Start lt 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        content_date_start = 'Start'
        content_date_end = 'End'
        f.by_sensing_date(start, end, inclusive, full_day, content_date_start, content_date_end)
        self.assertEqual(f.body,
                         'ContentDate/Start gt 2020-01-01T00:00:00.000Z and ContentDate/End lt 2020-01-02T00:00:00.000Z')

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        content_date_start = 'VALUE'
        with self.assertRaises(ValueError):
            f.by_sensing_date(start, end, inclusive, full_day, content_date_start)

        f = Filter()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 2)
        inclusive = False
        full_day = False
        content_date_end = 'VALUE'
        with self.assertRaises(ValueError):
            f.by_sensing_date(start, end, inclusive, full_day, content_date_end=content_date_end)

    def test_by_geographic_criteria(self):
        f = Filter()
        wkt_geometry = 'VALUE'
        f.by_geographic_criteria(wkt_geometry)
        self.assertEqual(f.body, f"OData.CSC.Intersects(area=geography'SRID=4326;{wkt_geometry}')")

        f = Filter()
        wkt_geometry = 'MULTIPOLYGON'
        with self.assertRaises(ValueError):
            f.by_geographic_criteria(wkt_geometry)

    def test_by_attribute(self):
        f = Filter()
        f.by_attribute('')
        self.assertEqual(f.body, '')

        f = Filter()
        queries = [Atr.BeginningDateTime() >= datetime(2019, 8, 1)
                   ]
        f.by_attribute(queries)
        self.assertEqual(f.body,
                         "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-08-01T00:00:00.000Z)")

        f = Filter()
        queries = [Atr.BeginningDateTime() >= datetime(2019, 8, 1),
                   Atr.BeginningDateTime() <= datetime(2019, 8, 2),
                   ]
        f.by_attribute(queries)
        self.assertEqual(f.body,
                         "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-08-01T00:00:00.000Z) and "
                         "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value le 2019-08-02T00:00:00.000Z)")

        f = Filter()
        queries = [Atr.BeginningDateTime() >= datetime(2019, 8, 1),
                   Atr.BeginningDateTime() <= datetime(2019, 8, 2),
                   Atr.CloudCover() < 10.0,
                   Atr.ProductType() == 'S2MSI2A',
                   Atr.OrbitDirection() == 'ASCENDING',
                   ]
        f.by_attribute(queries)
        self.assertEqual(f.body,
                         "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-08-01T00:00:00.000Z) and "
                         "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value le 2019-08-02T00:00:00.000Z) and "
                         "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.0) and "
                         "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and "
                         "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'ASCENDING')")


class TestAttributes(unittest.TestCase):

    def test_attributes(self):
        self.assertEqual(
            Atr.Authority() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'authority' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.Timeliness() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'timeliness' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.Coordinates() == '61, 69',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'coordinates' and att/OData.CSC.StringAttribute/Value eq '61, 69')")
        self.assertEqual(
            Atr.OrbitNumber() == 1,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value eq 1)")
        self.assertEqual(
            Atr.OrbitNumber() >= 1,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value ge 1)")
        self.assertEqual(
            Atr.OrbitNumber() <= 1,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value le 1)")
        self.assertEqual(
            Atr.OrbitNumber() > 1,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value gt 1)")
        self.assertEqual(
            Atr.OrbitNumber() < 1,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value lt 1)")
        self.assertEqual(
            Atr.ProductType() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.EndingDateTime() == datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'endingDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value eq 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.EndingDateTime() >= datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'endingDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.EndingDateTime() <= datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'endingDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value le 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.EndingDateTime() > datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'endingDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value gt 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.EndingDateTime() < datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'endingDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value lt 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.OrbitDirection() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.OperationalMode() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'operationalMode' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.ProcessingLevel() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.BeginningDateTime() == datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value eq 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.BeginningDateTime() >= datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value ge 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.BeginningDateTime() <= datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value le 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.BeginningDateTime() > datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value gt 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.BeginningDateTime() < datetime(2019, 1, 1, 1),
            "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'beginningDateTime' and att/OData.CSC.DateTimeOffsetAttribute/Value lt 2019-01-01T01:00:00.000Z)")
        self.assertEqual(
            Atr.PlatformShortName() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'platformShortName' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.BaselineCollection() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'baselineCollection' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.InstrumentShortName() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'instrumentShortName' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.RelativeOrbitNumber() == 999,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' and att/OData.CSC.IntegerAttribute/Value eq 999)")
        self.assertEqual(
            Atr.RelativeOrbitNumber() >= 999,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' and att/OData.CSC.IntegerAttribute/Value ge 999)")
        self.assertEqual(
            Atr.RelativeOrbitNumber() <= 999,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' and att/OData.CSC.IntegerAttribute/Value le 999)")
        self.assertEqual(
            Atr.RelativeOrbitNumber() > 999,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' and att/OData.CSC.IntegerAttribute/Value gt 999)")
        self.assertEqual(
            Atr.RelativeOrbitNumber() < 999,
            "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' and att/OData.CSC.IntegerAttribute/Value lt 999)")
        self.assertEqual(
            Atr.PlatformSerialIdentifier() == 'text',
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'platformSerialIdentifier' and att/OData.CSC.StringAttribute/Value eq 'text')")
        self.assertEqual(
            Atr.CloudCover() == 10.0,
            "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value eq 10.0)")
        self.assertEqual(
            Atr.CloudCover() >= 10.0,
            "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value ge 10.0)")
        self.assertEqual(
            Atr.CloudCover() <= 10.0,
            "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 10.0)")
        self.assertEqual(
            Atr.CloudCover() > 10.0,
            "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value gt 10.0)")
        self.assertEqual(
            Atr.CloudCover() < 10.0,
            "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.0)")


if __name__ == '__main__':
    unittest.main()
