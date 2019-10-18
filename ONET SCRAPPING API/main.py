from util import *
from OnetWebService import OnetWebService
import os

def main():
    credentials = config()
    client = OnetWebService(credentials['username'],credentials['password'])
    input_path = os.path.dirname(os.path.realpath(__file__))+"/input/"
    input_file = os.listdir(input_path)[0]
    onet_codes = []
    with open(input_path + input_file) as f:
        read_data = f.read().strip()

    read_data = read_data.split("\n")

    for val in read_data[1:]:
        onet_codes.append(val.split(",")[0])

    code = onet_codes[0]
    results = client.call('online/occupation/',(code))
    print(results.keys())

if __name__ == '__main__':
    main()
