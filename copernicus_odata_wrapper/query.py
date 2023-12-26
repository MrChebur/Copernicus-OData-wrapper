import inspect
import requests


from .filter import Filter
from .errors import check_response_for_errors
from .config import config

# noinspection PyMethodMayBeStatic
class Query:
    """
    Copernicus OData query wrapper as described in the documentation:
    https://documentation.dataspace.copernicus.eu/APIs/OData.html#odata-products-endpoint

    This class does not include `DeletedProducts` functionality.

    Class attrubutes:
        session - `requests.Session` i.e. to handle proxy
        timeout - a paramater of the `session.get()` or `session.post()`
    """

    def __init__(self):
        self.endpoint = config['endpoint']
        self.endpoint_zipper = config['endpoint_zipper']

        # general search options
        self.__options = {'filter': None,
                          'orderby': None,
                          'top': None,
                          'skip': None,
                          'count': None,
                          'expand': None,
                          }
        self.__options_defaults = self.__options.copy()

        # requests parameters
        self.session = None
        self.timeout = (30, 30)
        self.post_body = None

    def __merge_options(self) -> str:
        """Formats and merges options into a single line string with endpoint.
        :return: Request ready to be sent.
        """
        formatted_options = []
        for option, value in self.__options.items():
            if value is not None:

                if option == 'filter':
                    if value.body is None:
                        continue
                    formatted_option = f'${option}={value.body}'

                else:
                    formatted_option = f'${option}={value}'

                formatted_options.append(formatted_option)

        merged = f'{self.endpoint}?' + '&'.join(formatted_options)
        return merged

    def set_filter(self, fltr: Filter) -> None:
        """
        This method is used to set a `Filter` object that generates filter options.
        :param fltr: `Filter()` instance.
        :return:
        """
        if isinstance(fltr, Filter):
            self.__options['filter'] = fltr
        else:
            raise TypeError(f'Not supported type: {type(fltr)}')

    def set_orderby(self, argument: str, ascending: None or bool = None) -> None:
        """
        Orderby option can be used to order the products in an ascending (asc) or descending (desc) direction.
        If ascending is not specified, then the resources will be ordered in ascending order. By default, if orderby
        option is not used, the results are not ordered. If orderby option is used, additional orderby by id is also
        used, so that the results are fully ordered and no products are lost while paginating through the results.

        Example usage:
            query = Query()
            query.orderby_option('ContentDate/Start', ascending=False)

        An equivalent of:
            $orderby=ContentDate/Start desc

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#orderby-option

        :param argument: One of: 'ContentDate/Start', 'ContentDate/End', 'PublicationDate', 'ModificationDate'
        :param ascending: True/False/None
        """
        possible_arguments = ['ContentDate/Start', 'ContentDate/End', 'PublicationDate', 'ModificationDate']

        if ascending is None:
            direction = ''  # empty - by default means ascending
        elif ascending:
            direction = 'asc'
        else:
            direction = 'desc'

        if argument not in possible_arguments:
            raise ValueError(f'Invalid `argument`={argument}. Possible arguments: {possible_arguments}')
        self.__options['orderby'] = f'{argument} {direction}'

    def set_top(self, top: int or None = None) -> None:
        """
        Top option specifies the maximum number of items returned from a query. The default value is set to 20.
        The acceptable range is: 0 - 1000

        Example usage:
            query = Query()
            query.top_option(1)

        An equivalent of:
            $top=1

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#top-option
        """

        if top is not None:
            if top > 1000:
                raise ValueError(f'`top` maximum is 1000')
            elif top < 0:
                raise ValueError(f'`top` minimum is 0')
            else:
                self.__options['top'] = str(top)

    def set_skip(self, skip: int or None = None) -> None:
        """
        Skip option can be used to skip a specific number of results. Exemplary application of this option would be
        paginating through the results, however for performance reasons, we recommend limiting queries with small-time
        intervals as a substitute of using skip in a more generic query.

        The default value is set to 0.  Whenever a query results in more products than 20 (default top value),
        the API provides a nextLink at the bottom: "@OData.nextLink"

        The acceptable range is: 0 - 10 000

        Example usage:
            query = Query()
            query.skip_option(50)

        An equivalent of:
            $skip=50

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#skip-option
        """

        if skip is not None:
            if skip > 10000:
                raise ValueError(f'`skip` maximum is 10 000')
            elif skip < 0:
                raise ValueError(f'`skip` minimum is 0')
            else:
                self.__options['skip'] = str(skip)

    def set_count(self, enable: bool or None = None) -> None:
        """
        Count option enables users to get the exact number of products matching the query.
        This option is disabled (None) by default to accelerate the query performance.

        Example usage:
            query = Query()
            query.count_option(True)

        An equivalent of:
            $count=True

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#count-option
        """
        if enable is not None:
            if enable:
                self.__options['count'] = 'True'

    def set_expand(self, attributes: bool or None = None, assets: bool or None = None) -> None:
        """
        Expand attributes option enables users to see full metadata of each returned result.
        Expand assets allows to list additional assets of a products, including quicklooks.

        Example usage:
            query = Query()
            query.expand_option(attributes=True)

        An equivalent of:
            $expand=Attributes

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#expand-option
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#expand-assets

        :param attributes: If True - expands `Attributes`.
        :param assets: If True - expands `Assets`.
        :return: None
        """
        ATTRIBUTES = 'Attributes'
        ASSETS = 'Assets'
        BOTH = 'Assets&$expand=Attributes'  # '&$expand=Assets&$expand=Attributes' Yeah, it's awkward.

        if any(value is not None for value in [attributes, assets]):

            if attributes and assets:  # must be the first `if`
                self.__options['expand'] = BOTH

            elif attributes:
                self.__options['expand'] = ATTRIBUTES

            elif assets:
                self.__options['expand'] = ASSETS

            else:  # both False, or False/None
                pass

    def clear(self) -> None:
        self.__options = self.__options_defaults.copy()

    def send(self) -> dict:
        """
        Sends the query after it has been configured.
        :return: Response as a dictionary.
        """
        session = self.session
        if self.session is None:
            session = requests.Session()

        url = self.__merge_options()
        response = session.get(url, timeout=self.timeout)
        if check_response_for_errors(response) is None:
            dictionary = response.json()
            return dictionary

    def by_names(self, names: [str]) -> dict:
        # This method is different from the methods specified in `filter.py`, so it is derived from the `Filter` class.
        """
        Immediately sends a POST request to search for multiple product names.
        The name MUST ends with '.SAFE' or the scene will not be found.
        :param names: The list of product names to be searched by.
        :return:
        """
        session = self.session
        if self.session is None:
            session = requests.Session()

        url = f'{self.endpoint}/OData.CSC.FilterList'
        search_list = [{'Name': name} for name in names]
        response = session.post(url, timeout=self.timeout, json={"FilterProducts": search_list})
        if check_response_for_errors(response) is None:
            dictionary = response.json()
            return dictionary

    def quicklook(self):
        """
        Implementation of this method is not planned.

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#quicklook
        :return:
        """

        raise NotImplementedError(f'Implementation of this method is not planned: '
                                  f'`{inspect.currentframe().f_code.co_name}`')

    def product_nodes(self, uuid: str or None = None) -> dict:
        # todo: It's a strange method. I need to think about how to make it more convenient.
        """
        Lists product content. Only nodes that are folders can have their contents listed. Attempting to list Nodes
        for file results returning  an empty list. The listing Nodes feature is available for both authorized and
        unauthorized users. Every Listed Node has “uri” field, which lists its children.

        Example usage:
            query = Query()
            product = query.product_nodes('db0c8ef3-8ec0-5185-a537-812dad3c58f8')
            print('\nfirst node:')
            pprint(product)

            procucts_nodes = product['result'][0]['Nodes']['uri']
            aux_data = query.product_nodes(procucts_nodes)
            print(f'\naux_data node:')
            pprint(aux_data)

            aux_nodes_uri = aux_data['result'][0]['Nodes']['uri']
            print(f'\naux_nodes_uri={aux_nodes_uri}')

        An equivalent of:
            https://zipper.dataspace.copernicus.eu/odata/v1/Products(db0c8ef3-8ec0-5185-a537-812dad3c58f8)/Nodes
            https://zipper.dataspace.copernicus.eu/odata/v1/Products(db0c8ef3-8ec0-5185-a537-812dad3c58f8)/Nodes(S2A_MSIL1C_20180927T051221_N0206_R033_T42FXL_20180927T073143.SAFE)/Nodes
            https://zipper.dataspace.copernicus.eu/odata/v1/Products(db0c8ef3-8ec0-5185-a537-812dad3c58f8)/Nodes(S2A_MSIL1C_20180927T051221_N0206_R033_T42FXL_20180927T073143.SAFE)/Nodes(AUX_DATA)/Nodes

        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#listing-product-nodes

        :param uuid: uuid or url pointing exact product or url pointing product nodes.
        :return:
        """

        session = self.session
        if self.session is None:
            session = requests.Session()

        if self.endpoint in uuid or self.endpoint_zipper in uuid:
            if uuid.endswith(r'/Nodes'):
                url = f'{uuid}'
            else:
                url = f'{uuid}/Nodes'
        else:
            url = f'{self.endpoint}({uuid})/Nodes'

        response = session.get(url, timeout=self.timeout)
        if check_response_for_errors(response) is None:
            dictionary = response.json()
            return dictionary

    def product_download(self):
        """
        Reference to method:
        https://documentation.dataspace.copernicus.eu/APIs/OData.html#product-download
        :return:
        """
        raise NotImplementedError('Not planned to be implemented. It is not the job of this wrapper to handle data '
                                  'downloading tasks.')


class QueryDeleted:
    """
    Currently adding a wrapper for deleted products is not planned:
    https://documentation.dataspace.copernicus.eu/APIs/OData.html#odata-deletedproducts-endpoint
    """

    def __init__(self):
        raise NotImplementedError
