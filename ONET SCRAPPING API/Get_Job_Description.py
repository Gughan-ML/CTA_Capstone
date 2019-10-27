from util import *

def get_job_description(*args,**kwargs):
    base_url = 'online/occupation/'
    client = args[0]
    sections = args[1]
    row = dict.fromkeys(kwargs['cols'],'')
    json_response = []

    row['Code'] = kwargs['code']
    results = client.call(base_url,kwargs['code'])
    if list(results.keys()).count('error')==0:
        row['Title'] = results['title']
        options = list(results.keys())
        if options.count("notice") == 0:
            details_url = results['details_resources']['resource']
            keys_present_response = [x['title'] for x in details_url]
            for i in range(0,len(sections)):
                section = sections[i]
                if keys_present_response.count(section[0])>0:
                    response = client.call(base_url,kwargs['code'],"details","_".join(section[0].split(" ")).lower())
                    if len(section)==4:
                            description = extract_content(response[section[1]],key=section[2],identifier=section[3])
                    elif len(section)==3:
                        description = extract_education(response[section[1]],key='category',identifier='')
                    else:
                        description = response['title']

                    row[section[0]] = description
                    json_response.append(response)
                else:
                    row[section[0]] = ''
                    json_response.append("{}")

    return json_response,row
