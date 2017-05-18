'''
Created on May 16, 2017

@author: jesper
'''

class AuditModule():
    @staticmethod
    def read(file):
        pass
    @staticmethod
    def evaluate(info, yaml_path):
        pass

class lynis(AuditModule):

    @staticmethod
    def read(file):
        print "lynis/read"
        values = dict()
        
        next_line = file.readline()
        
        while next_line:

            if "Warning:" in next_line:
                start_index = next_line.find("W")
                end_index = next_line.find("[")
                
                warning = next_line[start_index:end_index-1].replace("Warning: ", "")
                if not values.has_key("warnings"):
                    values["warnings"] = [warning]
                else: 
                    values["warnings"].append(warning)
            
            elif "Suggestion:" in next_line:
                start_index = next_line.find("S")
                end_index = next_line.find("[")
                
                suggestion = next_line[start_index:end_index-1].replace("Suggestion: ", "")
                if not values.has_key("suggestions"):
                    values["suggestions"] = [suggestion]
                else: 
                    values["suggestions"].append(suggestion)            
            next_line = file.readline() 
            
        return values

    @staticmethod
    def evaluate(info, yaml_path):
        print "lynis/Eval"
        
        returnString = ""
        
        if info.has_key("warnings"):
            returnString += "The Lynis audit has found the following warnings: \n\n"
            for warning in info["warnings"]:
                returnString += warning + "\n"
        
        if info.has_key("suggestions"):
            returnString += "\n\nThe Lynis audit has found the following suggestions: \n\n"
            for suggestion in info["suggestions"]:
                returnString += suggestion + "\n"
        
        return returnString