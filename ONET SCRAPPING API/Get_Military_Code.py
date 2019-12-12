from util import *

'''
This functions acccess a end point when presented the onet job code will give response
of all the military codes associated with it
'''
def get_military_code(*args,**kwargs):
    client = args[0]
    base_url = "veterans/careers/" #MOC end point that will provided to the onetwebservice class
    results = client.call(base_url,kwargs['code'],'in_the_military')
    results_keys = list(results.keys())
    if results_keys.count("error")>0:
        return '',''
    else:
        codes,branch = extract_mocs(results,key='match')
        return codes,branch
