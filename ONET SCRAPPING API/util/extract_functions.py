#extract utility functions will used across varations for the extraction of various contents

'''
extract content is an utility function which takes sections like tasks, primary responsbilities
and splits it line by line and returnes multiple lines into single ";" separated line
'''
def extract_content(response,key='',identifier=''):
    output = []
    if len(response)>0:
        for val in response:
            if identifier=='':
                output.append(val[key])
            else:
                tech_category = val[identifier]['name']
                category_values_array = val[key]
                category_values = ";".join([x['name'] for x in category_values_array])
                output.append(tech_category+" - "+category_values)
        return "#".join(output)

'''
Format of education warranted the need of the separate extract function
'''
def extract_education(response,key='',identifier=''):
    return extract_content(response[key],key="name",identifier='')

'''
Each ONET job code has multiple military occupational codes (MOC) and there are duplicates in the matching
the following extract function get the MOCs removes all the duplicates and returns a # separated line 
'''
def extract_mocs(response,key=''):
    codes = []
    moc_category = []
    for val in response[key]:
        codes.append(val['code'])
        moc_category.append(val['branch'])

    codes = list(set(codes))
    moc_category = list(set(moc_category))
    return "#".join(codes),"#".join(moc_category)
