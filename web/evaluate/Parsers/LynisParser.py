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

class lynis(AuditModule):

    @staticmethod
    def read(file):
        warning_dict = dict()
        suggestion_dict = dict()
        
        next_line = file.readline()
        
        while next_line:

            if "Warning:" in next_line:
                start_index = next_line.find("W")
                end_index = next_line.find("[")
                warning = next_line[start_index:end_index-1].replace("Warning: ", "")
                
                start_index = next_line.find("[test:")
                end_index = next_line.find("]")
                test = next_line[start_index + len("[test:"):end_index]

                next_line = next_line[end_index+2:]
                start_index = next_line.find("[details:")
                end_index = next_line.find("]")
                details = next_line[start_index + len("[details:"):end_index]
                
                next_line = next_line[end_index+2:]
                start_index = next_line.find("[solution:")
                end_index = next_line.find("]")
                solution = next_line[start_index + len("[solution:"):end_index]

                inner_dict = dict()
                inner_dict["warning"] = warning
                inner_dict["details"] = details
                inner_dict["solution"] = solution
                
                warning_dict[test] = inner_dict
            
            elif "Suggestion:" in next_line:
                start_index = next_line.find("S")
                end_index = next_line.find("[")
                suggestion = next_line[start_index:end_index-1].replace("Suggestion: ", "")
                
                start_index = next_line.find("[test:")
                end_index = next_line.find("]")
                test = next_line[start_index + len("[test:"):end_index]

                next_line = next_line[end_index+2:]
                start_index = next_line.find("[details:")
                end_index = next_line.find("]")
                details = next_line[start_index + len("[details:"):end_index]
                
                next_line = next_line[end_index+2:]
                start_index = next_line.find("[solution:")
                end_index = next_line.find("]")
                solution = next_line[start_index + len("[solution:"):end_index]

                inner_dict = dict()
                inner_dict["suggestion"] = suggestion
                inner_dict["details"] = details
                inner_dict["solution"] = solution
                
                suggestion_dict[test] = inner_dict
                    
            next_line = file.readline() 
       
        info_dict = dict()
        info_dict["warnings"] = warning_dict
        info_dict["suggestions"] = suggestion_dict
        return info_dict

    @staticmethod
    def evaluate(info_dict, yaml_path):
        
        return_string = ""
        
        if info_dict.has_key("warnings"):
            return_string += "The Lynis audit has found the following warnings: \n\n"
            for test in info_dict["warnings"]:
                inner_dict = info_dict["warnings"][test]
                warning = inner_dict["warning"]
                details = inner_dict["details"]
                solution = inner_dict["solution"]

                return_string +=  "The test " + test + " has found the following warning:\n" + warning + "\n" + "details: " + details + "\n" + "solution: " + solution + "\n\n"
        
        return_string += "\n##########################\n\n\n"
        
        if info_dict.has_key("suggestions"):
            return_string += "The Lynis audit has found the following suggestions: \n\n"
            for test in info_dict["suggestions"]:
                inner_dict = info_dict["suggestions"][test]
                suggestion = inner_dict["suggestion"]
                details = inner_dict["details"]
                solution = inner_dict["solution"]

                return_string +=  "The test " + test + " has found the following suggestion:\n" + suggestion + "\n" + "details: " + details + "\n" + "solution: " + solution + "\n\n"
       
        return return_string