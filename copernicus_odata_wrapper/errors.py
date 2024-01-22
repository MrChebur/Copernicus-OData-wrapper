import requests


def check_response_for_errors(response: requests.Response) -> None:
    """
    Checks for errors in the response. If they are found, an `Exception` is raised.
    :param response: requests.Response
    :return: None - if there are no errors.
    """
    dictionary = response.json()

    # todo: Could there be an error with more than one key in the answer?
    # if only one exact 'detail' key in the response
    if len(dictionary) == 1:

        if 'detail' in dictionary:

            if dictionary == {'detail': 'Unauthorized'}:
                raise Unauthorized

            elif dictionary == {'detail': 'Invalid odata path'}:
                raise InvalidODataPath

            elif dictionary == {'detail': 'Not Found'}:
                raise NotFound

            elif dictionary == {"detail": "Expired signature!"}:
                raise ExpiredSignature

            elif dictionary == {"detail": "Product not found in catalogue"}:
                raise ProductNotFoundInCatalogue

            else:
                raise Unknown(f"An unknown error occurred, while sending:\n"
                              f"{response.url}"
                              f"\nYou may want to add this error to `errors.py`: "
                              f"{dictionary['detail']}")


class Unauthorized(Exception):
    pass


class InvalidODataPath(Exception):
    pass


class NotFound(Exception):
    pass


class ExpiredSignature(Exception):
    pass


class ProductNotFoundInCatalogue(Exception):
    pass


class Unknown(Exception):
    pass
