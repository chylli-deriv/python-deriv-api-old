from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.errors import ConstructionError
from deriv_api.utils import dict_to_cache_key

class Cache(DerivAPICalls):
    """
    Cache - A class for implementing in-memory and persistent cache

    The real implementation of the underlying cache is delegated to the storage
    object (See the params).

    The storage object needs to implement the API.

    example
    # Read the latest active symbols
    symbols = await api.activeSymbols();

    # Read the data from cache if available
    cached_symbols = await api.cache.activeSymbols();

    param {DerivAPIBasic} api API instance to get data that is not cached
    param {Object} storage A storage instance to use for caching
    """
    pass