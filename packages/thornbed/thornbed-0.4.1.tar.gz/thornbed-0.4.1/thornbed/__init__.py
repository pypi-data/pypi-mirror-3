from services import get_providers

__version__ = '0.4.1'
providers = get_providers()

def embed(url, **kwargs):
    res = None
    for service, lookup in providers:
        res = lookup(url, **kwargs)
        if res:
            break
    return res