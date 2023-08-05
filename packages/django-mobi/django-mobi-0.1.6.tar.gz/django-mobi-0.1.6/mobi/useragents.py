import os.path

from django.core.cache import cache

def load_from_search_strings_file():
    CACHE_KEY = 'MOBI_USER_AGENT'
    CACHE_TIMEOUT = 86400
    agents = cache.get(CACHE_KEY)
    
    if agents:
        # we got something, we are done, send it back.
        return agents
    
    # it wasn't in the cache, get it from the file, then store in the cache
    f = None
    try:
        f = open(os.path.join(os.path.dirname(__file__), 'search_strings.txt'))
        ss = f.readlines()
    finally:
        if f:
            f.close()
    agents = [s.strip() for s in ss if not s.startswith('#')]
    # store to the cache
    cache.set(CACHE_KEY, agents, CACHE_TIMEOUT)
    return agents

search_strings = load_from_search_strings_file()