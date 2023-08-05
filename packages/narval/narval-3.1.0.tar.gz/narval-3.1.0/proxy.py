
from logilab.common.pyro_ext import ns_get_proxy

def bot_proxy(config, cache):
    if not 'botproxy' in cache:
        nshost = config['bot-pyro-ns'] or config['pyro-ns-host']
        cache['botproxy'] = ns_get_proxy(config['bot-pyro-id'], 'narval',
                                         nshost=nshost)
    return cache['botproxy']
