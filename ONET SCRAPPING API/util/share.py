import json
def read_file(path):
    with open(path) as f:
        read_data = f.read().strip()
    return read_data.split("\n")

def write_file(path,format,data):
    f = open(path+format,"w+")
    if format==".json":
        json.dump(data,f)
    f.close()
