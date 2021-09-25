import pickle


def dict_to_cache_key(obj):
    cloned_obj = obj.copy()
    for key in ['req_id', 'passthrough', 'subscribe']:
        cloned_obj.pop(key, None)

    return pickle.dumps(cloned_obj)
