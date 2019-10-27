from util import *

def get_military_code(*args,**kwargs):
    client = args[0]
    base_url = "veterans/careers/"
    results = client.call(base_url,kwargs['code'],'in_the_military')
    results_keys = list(results.keys())
    if results_keys.count("error")>0:
        return '',''
    else:
        codes,branch = extract_mocs(results,key='match')
        return codes,branch
