'''
Created on May 3, 2017

@author: jesper
'''

import itertools
import yaml
from symbol import comparison
from multiprocessing.forking import duplicate
from sqlalchemy.sql.functions import next_value

class AuditModule():
    @staticmethod
    def read(file):
        pass
    @staticmethod
    def evaluate(info, yaml_path):
        pass

class cron_at(AuditModule):   
    @staticmethod
    def read(file):
        info_dict = dict()
      
        next_line = file.readline()
        
        while next_line:
            
            inner_values = next_line.split()
            
            if "No such file or directory" in next_line:
                info_dict[inner_values[3][1:-2]] = ["No such file or directory"]  # [1:-2] is to trim the filename from from quotation marks
            
            else: 
                # [permissions][?][owner][group][size][month][day][hour:min][filename]
                    info_dict[inner_values[8]] = inner_values[0]
                
            next_line = file.readline()
                
        return info_dict

    @staticmethod
    def evaluate(info_dict, yaml_path):
        return_string = ""
        
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
    
        for file_name in yaml_dict:
            if info_dict.has_key(file_name):
                info_value = info_dict[file_name]

                for comparison in yaml_dict[file_name]:
                    yaml_values = yaml_dict[file_name][comparison]         
                    message = compare(info_value, yaml_values, comparison)
                    if message is not None: return_string += message + "\n"

        return return_string

class crontab(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        notSetupString = "No crontab has been set up for the following: \n"
        
        
        next_line = file.readline()[:-1]
        while (next_line): 
            crontab = next_line.replace("no crontab for ", "")
            values[crontab] = "no"
            next_line = file.readline()[:-1]    
        return values

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""

        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
        
        
        blacklist = yaml_dict.pop("blacklist")
        expected = yaml_dict.pop("expected")
        
        for cronjob in blacklist:
            if info.has_key(cronjob):
                message = blacklist[cronjob]["msg"]
                return_string += message + "\n"
                
        for cronjob in expected:
            if not info.has_key(cronjob):
                message = expected[cronjob]["msg"]
                return_string += message + "\n"
                
#         for key in yaml_dict:
#             if info.has_key(key):
#                 customer_value = info[key]
#                 
#                 for comparison in yaml_dict[key]:
#                     values = yaml_dict[key][comparison]
#                     print customer_value
#                     print values
#                     print comparison
#                     message = compare(customer_value, values, comparison)
#                     if message is not None: return_string += message + "\n"

        
        return return_string

class diskvolume(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        file.readline()  # Skip first line
        next_line = file.readline()
        column = ["filesystem", "size", "used", "avail", "use%", "mount"]
        while next_line:
            inner_dict = dict()
            # [Filesystem][Size][Used][Avail][Use%][Mounted on]
            inner_values = next_line.split()
            for index in range(0, 6):
                inner_dict[column[index]] = inner_values[index]

            inner_dict["use%"] = inner_dict["use%"][:-1]  # Removes the % sign
            values[inner_values[5]] = inner_dict
            next_line = file.readline()

        return values

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        info_copy = dict(info)


        with open(yaml_path, "r") as stream:
            loaded_data = yaml.load(stream)
        for key in loaded_data:
            if info.has_key(key):
                customer_map = info[key]
                for column in customer_map:
                    customer_value = customer_map[column]
                    if not loaded_data[key].has_key(column): continue
                    for comparison in loaded_data[key][column]:
                        values = loaded_data[key][column][comparison]
                        message = compare(customer_value, values, comparison)
                        if message is not None: return_string += message + "\n"
                        
                info_copy.pop(key)
                
        for key in info_copy:
            customer_map = info[key]
            for column in customer_map:
                customer_value = customer_map[column]
                if not loaded_data["default"].has_key(column): continue
                for comparison in loaded_data["default"][column]:
                    values = loaded_data["default"][column][comparison]
                    message = compare(customer_value, values, comparison)
                    if message is not None: 
                        message = message.replace("/fs/", key)
                        return_string += message + "\n"

        
        return return_string

class encrypted_disk(AuditModule):
    @staticmethod
    def read(file):
        values = dict()

        next_line = file.readline()
        while next_line:
            inner_values = dict()
            

            n_line_split = next_line.split()
            
            for i in range(1, len(n_line_split)):
                n_line_ssplit = n_line_split[i].split("=")

                inner_values[n_line_ssplit[0]] = n_line_ssplit[1]
                
            values[n_line_split[0]] = inner_values
            next_line = file.readline()

        
        return values

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        uuid_dict = {}
        
        for key in info:
            for key_key in info[key]:
                if ("UUID" in key_key):
                    if uuid_dict.has_key(info[key][key_key]):
                        uuid_dict[info[key][key_key]].append(key)
                    else:
                        uuid_dict[info[key][key_key]] = [key]
                    
        
        
        
        for uuid in uuid_dict:
            duplicate_warning_msg = open("duplicate_uuid_warning_msg.txt", "r").read()
            
            if len(uuid_dict[uuid]) > 1:
                duplicate_warning_msg = duplicate_warning_msg.replace("/uuid/", uuid)
                duplicate_warning_msg = duplicate_warning_msg.replace("/key_set/", str(set(uuid_dict[uuid])))

                return_string += duplicate_warning_msg + "\n"
                
        return return_string

class environment(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        while True:
            nextLine = file.readline()
            if (nextLine == ""):
                break
            
            innerValues = nextLine.split("=")
            if (innerValues[0] == "LS_COLORS"):  # Hard to parse and don't think it has anythign to do with security risks
                continue
            
            values[innerValues[0]] = innerValues[1][:-1]
        return values

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""

        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)

        for key in yaml_dict:
            # check if key exists in customer file
            if info.has_key(key):
                customer_value = info[key]
                values = yaml_dict[key]
                for comparison in values:
                    message = compare(customer_value, values[comparison], comparison)
                    if message is not None: return_string += message + "\n"
                
                
                

        return return_string

class firewall(AuditModule):
    
    @staticmethod
    def read(file):
        values = dict()
        
        next_line = file.readline()
        
        while next_line:
            
            inner_values = next_line.split()
            if (inner_values and inner_values[0] == "Chain"):
                chain = inner_values[1]
                policy = inner_values[3].split(")")[0]
                values[chain] = policy
                
                
            next_line = file.readline()
                
        return values


    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
        
        
        for trafic in yaml_dict:
            columns = yaml_dict[trafic]
            if yaml_dict[trafic].has_key("policy"):
                for comparison in yaml_dict[trafic]["policy"]:
                    customer_value = info[trafic]
                    values = yaml_dict[trafic]["policy"][comparison]
                    
                    
                    message = compare(customer_value, values, comparison)
                    if message is not None: return_string += message + "\n"

        return return_string

class groups(AuditModule):
    @staticmethod        
    def read(file):
        info_dict = dict()
        
        next_line = file.readline()[:-1]
        
        while next_line:
            inner_dict = dict()
            inner_values = next_line.split(":")
            inner_dict["group"] = inner_values[0]
            inner_dict["password"] = inner_values[1]
            inner_dict["id"] = inner_values[2]
            inner_dict["users"] = inner_values[3]

            info_dict[inner_dict["group"]] = inner_dict
            next_line = file.readline()[:-1]

            
        return info_dict
            
    @staticmethod        
    def evaluate(info_dict, yaml_path):
        return_string = ""
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
        default_dict = yaml_dict.pop("default")
        
        for key in yaml_dict:
            if info_dict.has_key(key):
                for column in yaml_dict[key]:
                    info_value = info_dict[key][column]
                    for comparison in yaml_dict[key][column]:
                        yaml_values = yaml_dict[key][column][comparison]
                        message = compare(info_value, yaml_values, comparison)
                        if message is not None: 
                            message = message.replace("/users/", info_dict[key]["users"])
                            message = message.replace("/group/", info_dict[key]["group"])
                            return_string += message + "\n"
                            
        for key in info_dict:
            for column in default_dict:
                info_value = info_dict[key][column]
                for comparison in default_dict[column]:
                    yaml_values = default_dict[column][comparison]
                    message = compare(info_value, yaml_values, comparison)
                    if message is not None:
                        message = message.replace("/users/", info_dict[key]["users"])
                        message = message.replace("/group/", info_dict[key]["group"])
                        return_string += message + "\n"            
        
        return return_string

class lastlog(AuditModule):
    
    # Unsure how to parse...
    @staticmethod
    def read(file):
        value = dict()
        last_dict = dict()
        lastlog_dict = dict()
        
        next_line = file.readline()
        
        
        while next_line and not "wtmp begins " in next_line:
            next_values = next_line.split()
            if len(next_values) > 1: 
                last_dict[next_values[0]] = "yes"
            next_line = file.readline()
            
        next_line = file.readline()  # Skip line    
        while next_line:
            next_values = next_line[:-1].split(None, 1)
            
            if len(next_values) > 1: 
                lastlog_dict[next_values[0]] = next_values[1]
        
            next_line = file.readline()
            
        
        value["last"] = last_dict
        value["lastlog"] = lastlog_dict
            
            
            
        return value
    @staticmethod
    def evaluate(info, yaml_path):
        # Not sure how to evaluate...
        return_string = ""
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
        last = yaml_dict.pop("last")
        lastlog = yaml_dict.pop("lastlog")
        info_last = info.pop("last")
        info_lastlog = info.pop("lastlog")
        
        for key in lastlog:
            if info_lastlog.has_key(key):
                for comparison in lastlog[key]:
                    customer_value = info_lastlog[key]
                    values = lastlog[key][comparison]
                    message = compare(customer_value, values, comparison)
                    
                    if message is not None:
                        return_string += message + "\n"
                
        for key in last:
            if info_last.has_key(key):
                message = last[key]["msg"]
                
                if message is not None:
                    return_string += message + "\n"        
                        
        return return_string

class modprobe(AuditModule):    
    @staticmethod
    def read(file):
        values = dict()
        modprobes = []
        
        while True:
            nextLine = file.readline()    
            if ("Module" in nextLine): break
            modprobes.append(nextLine[:-1])
        
        values["modprobe.d"] = modprobes
        
        while True:
            nextLine = file.readline()
            if (nextLine == ""): break
            innerValues = nextLine.split()

            values[innerValues[0]] = innerValues
            
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        
        return_string = ""
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
        
        
        
        # Important configs
        
        for config in yaml_dict["important_configs"]:
            if config == "default":
                important_configs = yaml_dict["important_configs"]["default"]["config"]
                for i_config in important_configs:
                    if i_config not in dict["modprobe.d"]:
                        message = yaml_dict["important_configs"]["default"]["message"]
                        message = message.replace("/conf/", i_config)
                        return_string += message + "\n"
            elif config not in dict["modprobe.d"]:
                message = yaml_dict["important_configs"][config]["message"]
                return_string += message + "\n"


        # Important modules
        
        for module in yaml_dict["important_modules"]:
            if module == "default":
                important_modules = yaml_dict["important_modules"]["default"]["module"]
                for i_module in important_modules:
                    if i_module not in dict.keys():
                        message = yaml_dict["important_modules"]["default"]["message"]
                        message = message.replace("/module/", i_module)
                        return_string += message + "\n"
                        
            elif module not in dict.keys():
                message = yaml_dict["important_modules"][module]["message"]
                return_string += message + "\n"
                
        
        # Blacklisted configs
        
        for config in yaml_dict["blacklisted_configs"]:
            if config == "default":
                important_configs = yaml_dict["blacklisted_configs"]["default"]["config"]
                for i_config in important_configs:
                    if i_config in dict["modprobe.d"]:
                        message = yaml_dict["blacklisted_configs"]["default"]["message"]
                        message = message.replace("/conf/", i_config)
                        return_string += message + "\n"
            elif config in dict["modprobe.d"]:
                message = yaml_dict["blacklisted_configs"][config]["message"]
                return_string += message + "\n" 
                
                
        # Blacklisted modules
        
        for module in yaml_dict["blacklisted_modules"]:
            if module == "default":
                important_modules = yaml_dict["blacklisted_modules"]["default"]["module"]
                for i_module in important_modules:
                    if i_module in dict.keys():
                        message = yaml_dict["blacklisted_modules"]["default"]["message"]
                        message = message.replace("/module/", i_module)
                        return_string += message + "\n"
                        
            elif module in dict.keys():
                message = yaml_dict["blacklisted_modules"][module]["message"]
                return_string += message + "\n"
                
#         modprobe_file = open("modprobe_folders", "r")
#         
#         config_list = []
#         blacklist = []
#         important_list = []
#         
#         customer_modules = []
#         
#         
#         next_line = modprobe_file.readline() #Skip line
#         next_line = modprobe_file.readline()
#         
#         while next_line and not next_line.startswith("#"):
#             config_list.append(next_line[:-1])
#             next_line = modprobe_file.readline()
#             
#         next_line = modprobe_file.readline() # Skip line
#         
#         while next_line and not next_line.startswith("#"):
#             blacklist.append(next_line[:-1])
#             next_line = modprobe_file.readline()        
# 
#         next_line = modprobe_file.readline() # Skip line
#         
#         while next_line and not next_line.startswith("#"):
#             important_list.append(next_line[:-1])
#             next_line = modprobe_file.readline()   
#             
#         customer_config_list = dict["modprobe.d"].split("%")
# 
#         dict.pop("modprobe.d", None)
#         dict.pop("", None)
#         
#         for key in dict:
#             customer_modules.append(key)
# 
#         for config in config_list:
#             if config not in customer_config_list:
#                 return_string += "The expected file " + config + " is not in your system.\n"
#                 
#         for module in customer_modules:
#             if module in blacklist:
#                 return_string += "The system contains the blacklisted module " + module + "\n"
#         
#         for module in important_list:
#             if module not in customer_modules:
#                 return_string += "The system does not contain the important module " + module + "\n"


        return return_string 
    
class networkvolume(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        mount_dict = dict()
        fstab_dict = dict()
        
        next_line = file.readline()
        
        while next_line and "#" not in next_line and not next_line.isspace():
            innerValues = next_line.split()
            mount_dict[innerValues[2]] = innerValues
            next_line = file.readline()

        while next_line and "#" not in next_line and not next_line.isspace():
            inner_dict = dict()
            if ("#" in next_line): 
                next_line = file.readline()
                continue
            inner_values = next_line.split()
            
            
            inner_dict["file_system"] = inner_values[0]
            inner_dict["mount_point"] = inner_values[1]
            inner_dict["type"] = inner_values[2]
            options = inner_values[3].split(",")
            inner_dict["options"] = options
            inner_dict["dump"] = inner_values[4]
            inner_dict["pass"] = inner_values[5]
            
            fstab_dict[inner_dict["mount_point"]] = inner_dict

            next_line = file.readline()

        
        values["mount"] = mount_dict
        values["fstab"] = fstab_dict
        
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
    
        uuid_dict = dict()
        
        info_mount = info["mount"]
        info_fstab = info["fstab"]
     
        with open(yaml_path, "r") as stream:
                warnings = yaml.load(stream)
        # check duplicates
        for key in info_fstab:
            uuid = info_fstab[key]["file_system"].split("=")[1]
            if uuid_dict.has_key(uuid):
                uuid_dict[uuid].append(info_fstab[key]["mount_point"])
            else: 
                uuid_dict[uuid] = [info_fstab[key]["mount_point"]]
        
        for key in uuid_dict:
            if len(uuid_dict[key]) > 1:
                message = warnings["duplicates"]
                message = message.replace("/uuid/", key).replace("/key_set/", str(uuid_dict[key]))
                return_string += message + "\n"
                
        # #
        
        # check for username/password and backup, pass 
        for key in info_fstab:
            # check for username/password
            options = info_fstab[key]["options"]            
            for option in options:
                if "password" in option or "username" in option:
                    message = warnings["username_password"]
                    return_string += message + "\n"
        
            # checks for backup
            backup = info_fstab[key]["dump"]
            if backup != 1:
                message = warnings["backup"]
                return_string += message + "\n"
                
            # checks for pass
            pass_flag = info_fstab[key]["pass"]
            if key != "/" and pass_flag == "1":
                message = warnings["pass_non_root"]
                return_string += message + "\n"
                
            elif key == "/" and pass_flag != "1":
                message = warnings["pass_root"]
                return_string += message + "\n"
                
        
            
        return return_string

class open_connections(AuditModule):

    @staticmethod
    def read(file):
        values = dict()
        
        file.readline()  # Skip first line
        next_line = file.readline()
        while (next_line and not "COMMAND" in next_line):
            innerValues = next_line.split()
            values[innerValues[4]] = innerValues
            next_line = file.readline()
            
        while (next_line):
            innerValues = next_line.split()
            # Unsure what should be the key..
            values[innerValues[0] + "#" + innerValues[3]] = innerValues
            next_line = file.readline()

        return values

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        """Lists of listen ports, estab ports etc
        
        make sure that the ports are not bad according to open_connections file
        
        """
        return return_string

class passwdpolicy(AuditModule):

    @staticmethod
    def read(file):
        values = dict()
        
        next_line = file.readline()
        
        while(next_line):

            if "#" not in next_line and not next_line.isspace():

                key_value = next_line.split()
                values[key_value[0]] = key_value[1]
                
            next_line = file.readline()
            
        return values

    @staticmethod
    def evaluate(info, yaml_path):
        
        return_string = ""

        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
            
        for key in yaml_dict:
            if info.has_key(key):
                for comparison in yaml_dict[key]:
                    customer_value = info[key]
                    values = yaml_dict[key][comparison]
                    message = compare(customer_value, values, comparison)
                    if message is not None: 
                        return_string += message + "\n"
        
#         passwd_file = open("passwdpolicy", "r")
#         
#         next_line = passwd_file.readline()
#         
#         important_keys = []
#         passwd_dict = dict()
#         
#         while next_line:
#             
#             if (next_line.isspace() or next_line.startswith("%")):
#                 next_line = passwd_file.readline()
#                 continue
#             
#             passwd_key = next_line.split("=")[0]
#             
#             passwd_values = next_line.split("=")[1][:-1]
#             
#             passwd_dict[passwd_key] = passwd_values
#             next_line = passwd_file.readline()
#         
#         print passwd_dict
#         print info
#         
#         for key in passwd_dict:
#             #If key is in customer
#             if info.has_key(key[1:]):
#                 #If key is dangerous
#                 if (key.startswith("^")):
#                     return_string += "The key " + key + " is considered dangerous.\n"
#                 
#                 else:
#                     customer_value = info[key[1:]]
#                     values = passwd_dict[key]
#                     print key
#                     print "customer: " + customer_value
#                     print "values:   " + str(values)
#                     #If value is dangerous
#                     if "^" + customer_value in values:
#                         return_string += "The value " + customer_value + " is considered dangerous. Consider switching to " + str([x for x in values if not x.startswith("^")] + ". prefeably one of " + str([x for x in values if x.startswith("*")])) + "\n"
#                     
#                     #If value is not prefered
#                     if "<" + customer_value in values:
#                         return_string += "The value " + customer_value + " is not considered preferable. Consider switching to one of " + str([x for x in values if x.startswith("*")]) + "\n"
#                         
#             #If not found in customer
#             else:
#                 #If key is important
#                 if (key.startswith("#")):
#                     important_keys.append(key[1:])
#                     #Add recomended value?
#         
#         if len(important_keys) > 0:  
#                 return_string += "The following important keys were not found: " + str(important_keys) + "\n"
#         
        

        """if info["ENCRYPT_METHOD"] == "MD5":
            return_string = (return_string + "Your currently password encrypting method is MD5. " + 
                            "\nYou should consider changing the encrypting method to SHA256 or SHA516.")
            
            
        if info["PASS_MIN_DAYS"] > '0': 
            return_string = (return_string + "Warning: You have to wait " + dict["PASS_MIN_DAYS"] + 
                            " days to change password, this can be a security risk in case of accidental password change.")

        """
        
        return return_string

class processes(AuditModule):
    @staticmethod    
    def read(file):
        
        values = dict()
        
        next_line = file.readline()
        next_line = file.readline()  # Skip first line
        
        while (next_line):
            inner_dict = dict()
            next_line = next_line[:-1]
            inner_values = next_line.split(None, 10)
            
            
            inner_dict["USER"] = inner_values[0]
            inner_dict["PID"] = inner_values[1]
            inner_dict["%CPU"] = inner_values[2]
            inner_dict["%MEM"] = inner_values[3]
            inner_dict["VSZ"] = inner_values[4]
            inner_dict["RSS"] = inner_values[5]
            inner_dict["TTY"] = inner_values[6]
            inner_dict["STAT"] = inner_values[7]
            inner_dict["START"] = inner_values[8]
            inner_dict["TIME"] = inner_values[9]
            inner_dict["COMMAND"] = inner_values[10]
            
            values[inner_dict["COMMAND"]] = inner_dict
            
            next_line = file.readline()
            
        
#         next_line = file.readline()
#         
#         while (next_line):
#             splitted_line = next_line.split()
#             innerValues = ["" for i in range(11)] # Init the list with empty strings
#             for i in range (0, 10):
#                 innerValues[i] = splitted_line[i]
#             for i in range (10, len(splitted_line)):
#                 innerValues[10] = str(innerValues[10]) + splitted_line[i] + " "
#             
#             innerValues[10] = innerValues[:-1]
#             next_line = file.readline()
#             
#             
#             values[innerValues[1]] = innerValues
        
        return values

    @staticmethod
    def evaluate(info, yaml_path):  # change to dict if using commented code?
        return_string = ""   
        
        info_copy = dict(info)
        
        with open(yaml_path, 'r') as stream:
            yaml_dict = yaml.load(stream)
            
        default = yaml_dict.pop("default")
        important_processes = yaml_dict.pop("important_processes")
        blacklisted_processes = yaml_dict.pop("blacklisted_processes")
        
        # important processes
        for key in important_processes:
            if key == "default":
                for process in important_processes["default"]["process"]:
                    if not info.has_key(process):
                        message = important_processes["default"]["message"]
                        message = message.replace("/process/", process)
                        return_string += message + "\n"
            elif not info_copy.has_key(key):
                return_string += important_processes[key]["message"] + "\n"
        
        # blacklisted processes
        for key in blacklisted_processes:
            if key == "default":
                for process in blacklisted_processes["default"]["process"]:
                    if info.has_key(process):
                        message = blacklisted_processes["default"]["message"]
                        message = message.replace("/process/", process)
                        return_string += message + "\n"
            elif info_copy.has_key(key):
                return_string += blacklisted_processes[key]["message"] + "\n"
        
        
        # default value check (CPU & MEM usage)
        # print info_copy
        for key in info_copy:
            for column in default:
                customer_value = info_copy[key][column]
                for comparison in default[column]:
                    values = default[column][comparison]
                    message = compare(customer_value, values, comparison)
                    if message is not None:
                        message = message.replace("/process/", key)
                        return_string += message + "\n"
        
        
        # other keys
        
        for key in yaml_dict:
            if info_copy.has_key(key):
                for column in yaml_dict[key]:
                    for comparison in yaml_dict[key][column]:
                        if info_copy[key].has_key(column):
                            customer_value = info_copy[key][column]
                            values = yaml_dict[key][column][comparison]
                            message = compare(customer_value, values, comparison)
                            
                            if message is not None:
                                return_string += message
#        processes_file = open("processes", "r")
#   
#         next_line = processes_file.readline() #Skip first line
#         next_line = processes_file.readline()
#                 
#         expected_processes = []
#         non_root_blacklist = []
#         blacklist = []
#         
#  
#         while next_line and "#" not in next_line and not next_line.isspace():
#             expected_processes.append(next_line[:-1])
#             next_line = processes_file.readline()
#         
#         next_line = processes_file.readline()
#         
#         while next_line and "#" not in next_line and not next_line.isspace():
#             non_root_blacklist.append(next_line[:-1])
#             next_line = processes_file.readline()
#     
#         next_line = processes_file.readline()
# 
# 
#         while next_line and "#" not in next_line and not next_line.isspace():
#             blacklist.append(next_line[:-1])
#             next_line = processes_file.readline()
#             
#         
#         
#         for key in dict.iterkeys():
#             customer_process = dict[key][10][:-1]
#             
#             #if process is blacklist
#             if customer_process in blacklist:
#                 return_string += "The process " + customer_process + " currently running on your service is in our blacklist\n"
#             
#             #if process is non root
#             elif customer_process in non_root_blacklist and dict[key][0 != "root"]:
#                 return_string += "The process " + customer_process + " currently running on your service as a non-root. This is considered a security risk\n"
# 
#             #if expected process is found, it removes it from the exepcted processes list
#             if customer_process in expected_processes:
#                 expected_processes = [x for x in expected_processes if x != customer_process]
#                 
#         #if expected_processes is NOT empty
#         if expected_processes:
#             return_string += "The following processes were expected but could not be found on your system: " + str(expected_processes) + "\n"
            
        return return_string

class samba(AuditModule):
    @staticmethod
    def read(file):
        
        values = dict()
        
        
        next_line = file.readline()
        
        while (next_line):
            if "No such file or directory" in next_line:
                
                values["/etc/samba/smb.conf"] = "No such file or directory"
                return values
            
            if "#" in next_line or next_line.isspace():
                next_line = file.readline()
                continue
            
            if "[" in next_line:
                level = next_line
                next_line = file.readline()
                continue
            
            next_values = next_line.split(" = ")
            
            values[next_values[0].lstrip()] = [next_values[1][:-1], level[:-1]]
            
            next_line = file.readline()
        
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        
        samba_file = open(yaml_path, "r")
        
        
        samba_dict = dict()
        
        samba_lists = [[]]
        
        
        samba_important_keys = []
        
        samba_lists[0] = ([1, 2, 3])
        samba_lists.append([17, 6, 5])
        
        next_line = samba_file.readline()
        
        while next_line:
            if next_line.startswith("%") or next_line.isspace():
                next_line = samba_file.readline()
                continue
            samba_k_v_l = next_line[:-1].split("=")
            samba_key = samba_k_v_l[0]
            samba_v_l = samba_k_v_l[1].split(",")
            
            
            next_line = samba_file.readline()
            samba_values = samba_v_l[0].split("|")
            samba_levels = samba_v_l[1].split("|")
            
            if samba_key.startswith("#"): samba_important_keys.append(samba_key[1:])
                
            samba_dict[samba_key] = [samba_values, samba_levels]
            
            
        for key in samba_dict:
            if key[1:] in info.keys():
                
                # if Dangerous key
                if key.startswith("^"):
                    return_string += "The key " + key + " is considered dangerous.\n"
                    
                else:
                    customer_value = info[key[1:]][0]
                    customer_level = info[key[1:]][1]
                    samba_values = samba_dict[key][0]
                    samba_levels = samba_dict[key][1]
                    # if Dangerous level
                    if "^" + customer_level in samba_levels:
                        return_string += "The level for the key " + key[1:] + " is considered dangerous. Consider changing to one of " + str([x[1:] for x in samba_levels if not x.startswith("^")]) + " preferably one of " + str([x[1:] for x in samba_levels if x.startswith("*")]) + "\n"
                        
                    # if not preferable level
                    elif "<" + customer_level in samba_levels:
                        if len([x for x in samba_levels if x.startswith("*")]) > 0:
                            return_string += "The level for the environment key " + key[1:] + " is not considered preferable. Consider changing to one of " + str([x[1:] for x in samba_levels if x.startswith("*")]) + "\n" 
                      
                    # cant find level in samba txt    
                    elif "*" + customer_level not in samba_levels:
                        return_string += "The level " + customer_value + " for the key " + key[1:] + " was not found in our list of \"predetermined\" levels. \n\tRecommended levels: " + str([x[1:] for x in samba_levels if x.startswith("*")]) + "\n\tOkay levels: " + str([x[1:] for x in samba_levels if x.startswith("<")]) + "\n"

                    
                    # if Dangerous value
                    if "^" + customer_value in samba_values:
                        return_string += "The value for the key " + key[1:] + " is considered dangerous. Consider changing to one of " + str([x[1:] for x in samba_values if not x.startswith("^")]) + " preferably one of " + str([x[1:] for x in samba_values if x.startswith("*")]) + "\n"

                    # if not preferable value
                    elif "<" + customer_value in samba_values:
                        if len([x for x in samba_levels if x.startswith("*")]) > 0:
                            return_string += "The value for the environment key " + key[1:] + " is not considered preferable. Consider changing to one of " + str([x[1:] for x in samba_values if x.startswith("*")]) + "\n" 
                         
                    # cant find value in samba txt
                    elif "*" + customer_level not in samba_values:
                        return_string += "The value " + customer_value + " for the key " + key[1:] + " was not found in our list of \"predetermined\" values. \n\tRecommended values: " + str([x[1:] for x in samba_values if x.startswith("*")]) + "\n\tOkay levels: " + str([x[1:] for x in samba_values if x.startswith("<")]) + "\n"
                  
                samba_important_keys = [x for x in samba_important_keys if x != key[1:]]
            # cant find key in samba  
            
        if len(samba_important_keys) > 0:
            return_string += "The following keys were not found in your system: " + str(samba_important_keys) + ". They are considered important."
                
                    
                    
            
        
        return return_string

class sshd(AuditModule):
    @staticmethod
    def read(file):
        info_dict = dict()
        
        next_line = file.readline()
        
        while (next_line):

            if "No such file or directory" in next_line:
                info_dict["/etc/ssh/sshd_config"] = "No such file or directory"
            
            if "#" in next_line or next_line.isspace(): 
                next_line = file.readline()
                continue

            next_values = next_line.split()

            info_dict[next_values[0]] = next_values[1]
            
            next_line = file.readline()
        
        return info_dict
    @staticmethod
    def evaluate(info_dict, yaml_path):
        return_string = ""
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)        
            
        for key in yaml_dict:
            if info_dict.has_key(key):
                info_value = info_dict[key]
                yaml_values = yaml_dict[key]
                
                for comparison in yaml_values:  
                    yaml_value = yaml_values[comparison]
                    message = compare(info_value, yaml_value, comparison)
                    if message is not None: 
                        return_string += message + "\n"

        return return_string

class startup(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        
        file.readline()  # Skip first line (/etc/init.d)
        file.readline()  # Skip second line (total 216) //maybe use?
        
        next_line = file.readline()
        
        while (next_line):
            next_values = next_line.split()
            values[next_values[8]] = next_values
            next_line = file.readline()
            
        return values
        

    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        
        blacklist = []
        expected = []
        
        with open(yaml_path, "r") as stream:
            yaml_dict = yaml.load(stream)
            
        expected = yaml_dict.pop("expected")
        blacklist = yaml_dict.pop("blacklisted")
        permission = yaml_dict.pop("permission")
        
        # expected scripts
        for script in expected["scripts"]:
            if script not in info:
                message = expected["msg"]
                message = message.replace("/script/", script)
                return_string += message + "\n"
                
        # blacklisted scripts
        for script in blacklist["scripts"]:
            if script in info:
                message = blacklist["msg"]
                message = message.replace("/script/", script)
                return_string += message + "\n"

        # check permissions
        for key, value in info.iteritems():
            permissions = value[0]
            permissions = list(permissions)
            
            if permissions[5] == "w" or permissions[8] == "w":
                message = permission["msg"]
                message = message.replace("/script/", key)
                return_string += message + "\n"

            
            
        return return_string
    
class sudoers(AuditModule):
    @staticmethod
    def read(file):
        
        values = dict()
        username = ""
        hosts = ""
        run_as_users = ""
        run_as_groups = ""
        command = ""
        
        
        next_line = file.readline()
        
        while (next_line):
            group = False

            if "#" in next_line or next_line.isspace(): 
                next_line = file.readline()
                continue
            
            if "Defaults" in next_line:
                inner_values = next_line.split()
                tmp = inner_values[1].split("=")
                username = tmp[0]
                values[username] = ['', '', '', command]
                next_line = file.readline()
                continue

            inner_values = next_line.split()


            username = inner_values[0]

            command = inner_values[2]

            inner_values = inner_values[1].split("=")

            hosts = inner_values[0]

            inner_values = inner_values[1].split(":")

            
            
            if (len(inner_values) > 1):
                run_as_users = inner_values[0][1:]
                run_as_groups = inner_values[1][:-1]
            else:
                run_as_users = inner_values[0][-1:-1]


            values[username] = [hosts, run_as_users, run_as_groups, command]
            
            next_line = file.readline()

        return values

    @staticmethod
    def evaluate(info, yaml_path):

        return_string = ""

        if info.has_key("env_reset") == True:
            return_string += "env_reset is available. The system will make sure the terminal environment remove any user variables and clear potentially harmful environmental variables from the sudo sessions \n \n"
        else:
            return_string += "env_reset variable has not been set. You should add it the variable in /etc/sudoers"    

        for key, value in info.iteritems():
            if key == "secure_path":

                if value[3] != "[\'\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin\"\']":
                 continue

            if (value[0] and value[1] and value[2] and value[3]) == "ALL" and ("root" not in key) and ("%" not in key):
                 return_string += "User: " + "\"" + key + "\"" + " has super user rights.\n\n"
                 continue

            if (value[0] and value[2] and value[3] == "ALL") and (value[1] == '') and ("root" not in key) and ("%admin" not in key) and ("%sudo" not in key):
                 return_string += "Members of group: " + "\"" + key + "\"" + " may gain root privileges.\n\n"
                 continue

            if (value[0] and value[1] and value[2] and value[3] == "ALL") and ("root" not in key) and ("%admin" not in key) and ("%sudo" not in key):
                 return_string += "Members of sudo group: " + "\"" + key + "\"" + " can execute any command\n\n"
                 continue

        return return_string

class suid_files(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        
        next_line = file.readline()
        
        while (next_line):
            values[next_line] = next_line
            next_line = file.readline()
             
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        return return_string

class system(AuditModule):
    @staticmethod
    def read(file):
        
        values = dict()
        
        next_line = file.readline()
        
        while (next_line):
            values[next_line] = next_line
            next_line = file.readline()
            
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        return return_string

class users(AuditModule):
    @staticmethod
    def read(file):
        values = dict()
        
        next_line = file.readline()
        
        while (next_line):    
            inner_dict = dict()
            inner_values = next_line[:-1].split(":", 6)
            
            inner_dict["username"] = inner_values[0]
            inner_dict["password"] = inner_values[1]
            inner_dict["user_id"] = inner_values[2]
            inner_dict["group_id"] = inner_values[3]
            inner_dict["user_info"] = inner_values[4]
            inner_dict["home_dir"] = inner_values[5]
            inner_dict["shell"] = inner_values[6]
            
            values[inner_dict["username"]] = inner_dict
            
            next_line = file.readline()
        
        
        return values
    @staticmethod
    def evaluate(info, yaml_path):
        return_string = ""
        
        with open(yaml_path, 'r') as stream:
            yaml_dict = yaml.load(stream)
                        
        for key in yaml_dict:
            if info.has_key(key):
                for column in yaml_dict[key]:
                    for comparison in yaml_dict[key][column]:
                        values = yaml_dict[key][column][comparison]
                        customer_value = info[key][column]
                        message = compare(customer_value, values, comparison)
                        if message is not None: 
                            return_string += message
                    
#         for key in dict:
#             
#             risks = [False, False, False]
# 
#             value = dict[key]
#             if value[2] == "0" and not key == "root":
#                 return_string = return_string + "User " + "'" + key + "'" + " has super user rights\n"
#                 risks[0] = True
#                 
#             if value[1] == "!":
#                 return_string = return_string = "User " + "'" + key + "'" + " is stored in /etc/security/passwd and is not encrypted\n"
#                 risks[1] = True
#                 
#             elif value[1] == "*":
#                 return_string = return_string + "User " + "'" + key + "'" + " has an invalid password\n"
#                 risks[2] = True
#                 
#             
#             if risks[0]:
#                 return_string += "\nYou should change the users' priviliges"
#             
#             if risks[1]:
#                 return_string += "\nYou should encrypt the users' password"
#             
#             if risks[2]:
#                 return_string += "\nYou should change users' password to a valid one"
#                       
        return return_string

def compare(customer_value, values, comparison):
    
    # Equal
    
    if comparison == "eq":
        value = values.keys()[0]

        if customer_value != value:
            message = values[value]["msg"]
            severity = values[value]["severity"]
            return message    
    # Not equal 
    if comparison == "neq":
        values = values["values"]

        if customer_value in values.keys():
            message = values[customer_value]["msg"]
            severity = values[customer_value]["severity"]
            return message
            
    if comparison == "nlt":
        value = values["value"]
        
        if int(customer_value) < int(value):
            message = values["msg"]
            severity = values["severity"]
            return message
        
    if comparison == "ngr":
        value = values["value"]
        
        if float(customer_value) > float(value):
            message = values["msg"] 
            return message
            
    if comparison == "nbtwn":

        values = values["values"]
        for message in values:
            for ranges in values[message]["ranges"]:
                range_max = max(ranges)
                range_min = min(ranges)
                if int(customer_value) < range_max and int(customer_value) > range_min:
                    severity = values[message]["severity"]
                    return message
                
    if comparison == "in":
        if customer_value not in values["values"]:
            severity = values["severity"]
            message = values["msg"]
            return message
                
    if comparison == "permissions":
        for permission_group in values:
            if permission_group == "other":
                other_rwx = customer_value[7:]
                for permission in values[permission_group]:
                    if permission in other_rwx:
                        message = values[permission_group] [permission]["msg"]
                        return message
                    
            if permission_group == "user":
                user_rwx = customer_value[1:4]
                for permission in values[permission_group]:
                    if permission in user_rwx:
                        message = values[permission_group] [permission]["msg"]
                        return message
            
            if permission_group == "group":
                group_rwx = customer_value[4:7]
                for permission in values[permission_group]:
                    if permission in group_rwx:
                        message = values[permission_group] [permission]["msg"]
                        return message
        
            
    pass
