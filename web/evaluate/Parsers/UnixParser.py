'''
Created on May 16, 2017

@author: jesper
'''

class AuditModule():
    @staticmethod
    def read(file):
        pass
    @staticmethod
    def evaluate(info_dict, yaml_path):
        pass

class unix(AuditModule):
    
    @staticmethod
    def read(file):
        info_dict = dict()
        
        next_line = file.readline()
        
        while next_line:
            if "WARNING:" in next_line:
                warning = next_line.replace("WARNING: ", "")[:-1]
                if info_dict.has_key("warnings"):
                    info_dict["warnings"].append(warning)
                else:
                    info_dict["warnings"] = [warning]
        
            next_line = file.readline()
        return info_dict


    @staticmethod
    def evaluate(info_dict, yaml_path):
        
        return_string = ""
        
        
        if info_dict.has_key("warnings"):
            return_string += "The unix audit has found the following warnings:\n\n"
            
            for warning in info_dict["warnings"]:
                
                return_string += warning + "\n"
        
        
        return return_string