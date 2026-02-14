"""Options analysis tools."""

import logging
from polygon import RESTClient
from config import POLYGON_API_KEY

if not POLYGON_API_KEY:
    logging.getLogger(__name__).warning(
        "POLYGON_API_KEY not set. Market data API calls will fail."
    )

polygon_client = RESTClient(api_key=POLYGON_API_KEY)
