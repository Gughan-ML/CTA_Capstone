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

def extract_education(response,key='',identifier=''):
    return extract_content(response[key],key="name",identifier='')

def extract_mocs(response,key=''):
    codes = []
    moc_category = []
    for val in response[key]:
        codes.append(val['code'])
        moc_category.append(val['branch'])

    codes = list(set(codes))
    moc_category = list(set(moc_category))
    return "#".join(codes),"#".join(moc_category)
