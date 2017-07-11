#!/usr/bin/python
'''
Created on May 3, 2017

@author: jesper
'''
import os

from Parsers.RJParser import *
from Parsers import RJParser as rjParser
from Parsers import LynisParser as lynisParser
from Parsers import UnixParser as unixParser


def audit_module_evaluate(parser, module_name, file, yaml_path):
    information = "### " + module_name + " ###\n\n"
    audit_module = getattr(parser, module_name)
    data = audit_module.read(file)
    information += str(audit_module.evaluate(data, yaml_path))
    information += "\n##################\n\n\n\n\n"
    return information    

def read_test_config(yaml_config_folder_path):
    tests_config_yaml = yaml_config_folder_path + '/tests_config.yaml'
    config_yaml = None
    with open(tests_config_yaml, "r") as stream:
        config_yaml = yaml.load(stream)
    return config_yaml

def write_to(file_path, evaluation):
    output = open(file_path, "w")
    output.write(evaluation)
    output.close()
def evaluate(parser):
    """Evaluate modules

    Args:
        - test_names: the file name which contains the name in the upload log folder
        - log_folder_path: the corresponds folder where the log files lies in
        - parser: the parser to read and evalute the log files

    Returns:
        - evaluation by the input parser

    """
    web_folder = os.getcwd()
    log_folder_path = web_folder + '/logs'
    yaml_config_folder_path = web_folder + '/config'
    parser_type = parser.__name__.split('.')[-1]
    evaluation = "The " + parser_type + " found the following issues:\n\n"
    #unzip_structures = [i[:-1] for i in open(test_structure)]
    config_yaml = read_test_config(yaml_config_folder_path)
    for module_name in config_yaml[parser_type]:
        path = config_yaml[parser_type][module_name]["path"]
        yaml_path =  yaml_config_folder_path + "/rules/" + module_name + ".yaml"
        log_path = log_folder_path + path
        for file_path in os.listdir(log_path):
            log_file_path = log_path + file_path
            file = open(log_file_path, "r")
            evaluation += audit_module_evaluate(parser, module_name, file, yaml_path)
    return evaluation


def main():
    #from Parsers import RJParser as parser
    from Parsers import RJParser as parser
    
    web_folder = os.getcwd()
    web_folder = web_folder.replace("/evaluate", "")
    log_folder_path = web_folder + '/jespertesting'
    
    lynis_log = log_folder_path + "/lynis.log"
    unix_log = log_folder_path + "/outputdetailed.txt"
    
    yaml_config_folder_path = web_folder + '/config'
    parser_type = parser.__name__.split('.')[-1]

    evaluation = "The " + parser_type + " found the following issues:\n\n"
    #unzip_structures = [i[:-1] for i in open(test_structure)]
    config_yaml = read_test_config(yaml_config_folder_path)
    for module_name in config_yaml[parser_type]:
        path = config_yaml[parser_type][module_name]["path"]
        yaml_path =  yaml_config_folder_path + "/rules/" + module_name + ".yaml"
        log_path = log_folder_path + path
        for file_path in os.listdir(log_path):
            log_file_path = log_path + file_path
            file = open(log_file_path, "r") #log_file_path
            evaluation += audit_module_evaluate(parser, module_name, file, yaml_path)
    output_file = open(log_folder_path + "/output.txt", "w")
    
    output_file.write(evaluation)
    
    return evaluation    

if __name__ == "__main__": main()
