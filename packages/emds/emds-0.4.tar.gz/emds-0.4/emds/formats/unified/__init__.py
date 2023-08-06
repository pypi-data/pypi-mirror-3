from emds.compat import json
from emds.data_structures import MarketHistoryList, MarketOrderList
from emds.formats.exceptions import ParseError
from emds.formats.unified import history, orders

def parse_from_json(json_str):
    """
    Given a Unified Uploader message, parse the contents and return a
    MarketOrderList or MarketHistoryList instance.

    :param str json_str: A Unified Uploader message as a JSON string.
    :rtype: MarketOrderList or MarketHistoryList
    :raises: MalformedUploadError when invalid JSON is passed in.
    """
    try:
        message_dict = json.loads(json_str)
    except ValueError:
        raise ParseError("Mal-formed JSON input.")

    upload_keys = message_dict.get('uploadKeys', False)
    if upload_keys is False:
        raise ParseError(
            "uploadKeys does not exist. At minimum, an empty array is required."
        )
    elif not isinstance(upload_keys, list):
        raise ParseError(
            "uploadKeys must be an array object."
        )

    upload_type = message_dict['resultType']

    try:
        if upload_type == 'orders':
            return orders.parse_from_dict(message_dict)
        elif upload_type == 'history':
            return history.parse_from_dict(message_dict)
        else:
            raise ParseError(
                'Unified message has unknown upload_type: %s' % upload_type)
    except TypeError as exc:
        # MarketOrder and HistoryEntry both raise TypeError exceptions if
        # invalid input is encountered.
        raise ParseError(exc.message)

def encode_to_json(order_or_history):
    """
    Given an order or history entry, encode it to JSON and return.

    :type order_or_history: MarketOrderList or MarketHistoryList
    :param order_or_history: A MarketOrderList or MarketHistoryList instance to
        encode to JSON.
    :rtype: str
    :return: The encoded JSON string.
    """
    if isinstance(order_or_history, MarketOrderList):
        return orders.encode_to_json(order_or_history)
    elif isinstance(order_or_history, MarketHistoryList):
        return history.encode_to_json(order_or_history)
    else:
        raise Exception("Must be one of MarketOrderList or MarketHistoryList.")