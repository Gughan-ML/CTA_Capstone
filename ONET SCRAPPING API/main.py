from util import *
from OnetWebService import OnetWebService
import os
import pandas as pd
from Get_Job_Description import get_job_description
from Get_Military_Code import get_military_code

'''
Controller functions which is responsible for the whole crawling function to be run as intended.
Reads the onet job codes from the input folder and calls the api to get the data and stores everything
in a pandas dataframe and finally writes the output to the folder
'''
def main():
    credentials = config() #obtain credentials
    client = OnetWebService(credentials['username'],credentials['password']) #obtain connection 
    base_path = os.path.dirname(os.path.realpath(__file__))+"/"
    input_path = "input/"
    meta_path = "meta/"
    output_path = "output/"
    onet_codes = []

    # Reading the onet job codes from the input folder
    # Any changes for reading onet job codes has to be done in the inputs folder
    input_file = os.listdir(base_path+input_path)[0]
    onet_code_dump = read_file(base_path +input_path+input_file)

    # Read the meta data for the job description crawling
    meta_file = os.listdir(base_path+meta_path)[0]
    sections =  read_file(base_path+meta_path+meta_file)
    sections = [x.split(",") for x in sections]
    cols = ['Code','Title'] + [x[0] for x in sections] + ['MOCs','Military_Branch']

    #Initialize output list
    output_list = []

    #read onet codes from dump
    for val in onet_code_dump[1:]:
        onet_codes.append(val.split(",")[0])

    #Start Crawling from ONET
    for code in onet_codes:
        print("Crawling "+code+" ...")
        json_response,row = get_job_description(client,sections,code=code,cols=cols)
        MOC,branch = get_military_code(client,code=code)
        row['MOCs'] = MOC
        row['Military_Branch'] = branch
        output_list.append(row)
        write_file(output_path+"json/"+code,format=".json",data=json_response)

    #write output to the csv
    df = pd.DataFrame(output_list)
    df.to_csv(output_path+"csv/final.csv")


if __name__ == '__main__':
    main()
