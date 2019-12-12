from configparser import ConfigParser
import os

'''
Config utility function which uses the config.ini to get the configurations needed for various connections
Current version uses the credentials for the onet which needs to be configured at a later time to future ones
Any possible further connections can reuse this function by editing the config.ini file
'''
def config(filename=os.path.dirname(os.path.realpath(__file__))+'/config.ini', section='credentials'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    credentials = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            credentials[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return credentials
