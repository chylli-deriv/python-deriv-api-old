import pickle
import re

def dict_to_cache_key(obj):
    cloned_obj = obj.copy()
    for key in ['req_id', 'passthrough', 'subscribe']:
        cloned_obj.pop(key, None)

    return pickle.dumps(cloned_obj)

def is_valid_url(url):
    regex = re.compile(
        r'^(?:ws)s?://'  # ws:// or wss://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None
