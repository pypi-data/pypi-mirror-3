import os

from dare.conffileparser import ConfFileParser
from dare.conffileparser import ConfFileWriter

def wu_disc(step_name, step_conf, step_resource_conf, resource, working_directory, args, wus_count, dare_uuid):

    section_param ={}
    section_param["type"] = "compute"
    section_param["name"] = "wu_"+ str(wus_count)
    section_param["step_name"] = str(step_name)
    section_param["wus_count"] = str(wus_count)
    
    section_param["executable"]= step_conf["executable"]
    section_param["number_of_processes"]= step_conf["number_of_processes"]
    section_param["spmd_variation"]= step_conf["spmd_variation"]
    section_param["environment"]= step_resource_conf["environment"]    
    section_param["output"]= os.path.join(working_directory, "stdout-"+ str(dare_uuid) +"-"+str(wus_count)+".txt")
    section_param["error"]= os.path.join(working_directory, "stderr-"+ str(dare_uuid) +"-"+str(wus_count)+".txt" )
    section_param["appname"]= "simple"
    
    #varrying
    section_param["resource"] = resource
    section_param["working_directory"]= working_directory
    section_param["arguments"]= args

    return  section_param


###################################################################################################
###########             step = 0 (data)      ######################################################
###################################################################################################
def data(ft_type, source_url, input_list, dest_url, wus_count, step_name):

    sect_list = []
    for input_name in input_list:  
    
        section_param ={}
        section_param["name"] = "wu_"+ str(wus_count)
        section_param["wus_count"] = str(wus_count)
        section_param["type"] = "data"
        section_param["step_name"] = step_name

        section_param["appname"]="file_transfer"
        section_param["ft_type"]="scp"
        section_param["source_url"]=os.path.join(source_url , input_name)
        section_param["dest_url"]=os.path.join(dest_url, input_name)
        wus_count = wus_count + 1
        sect_list.append(section_param)
    ######increase wu count
    
    return  sect_list

def data2(step_name, wus_count, working_directory, input_dir, dare_uuid, input_list):


    sect_list = []
    for input_name in input_list:  

        section_param = {}
        section_param["name"] = "wu_"+ str(wus_count)
        section_param["wus_count"] = str(wus_count)
        section_param["type"] = "compute"
        section_param["step_name"] = step_name

        section_param["executable"]= "/bin/ln"
        section_param["number_of_processes"]="1"
        section_param["spmd_variation"]= "single"
        section_param["arguments"]= "-s " + os.path.join(input_dir,input_name) +" "+ os.path.join(working_directory,input_name)
        section_param["environment"]= ""
        section_param["working_directory"]= working_directory
        section_param["output"]= os.path.join(working_directory, "stdout-"+ str(dare_uuid) +"-"+str(wus_count)+".txt")
        section_param["error"]= os.path.join(working_directory, "stderr-"+ str(dare_uuid) +"-"+str(wus_count)+".txt" )
        section_param["appname"]= "linking"
        section_param["resource"]= 0
        sect_list.append(section_param)
        wus_count = wus_count + 1
    return  sect_list


def resource(resource_conf_file, walltime, total_core_count, resource_list):
    
    #read the resource conf file
    
    rcfp = ConfFileParser(resource_conf_file)

    sect_list= []
    for i in range(0, len(resource_list)):  
        resource_conf = rcfp.dict_section(resource_list[i])

        section_param ={}
        section_param["name"] = "resource_"+ str(i)
        section_param["type"] = "resource"

        section_param["type"]=  "bigjob"
        section_param["resource_url"]=  resource_conf["resource_url"]
        section_param["processes_per_host"]=   resource_conf["cores_per_node"]
        section_param["allocation"]=  resource_conf["allocation"]
        section_param["queue"]=  resource_conf["queue"]
        section_param["userproxy"]=  resource_conf["userproxy"]
        section_param["working_directory"]=  resource_conf["working_directory"]
        section_param["input_directory"]=  resource_conf["input_directory"]
        section_param["filetransfer_url"] = resource_conf["filetransfer_url"] 

    
        #changing parameters from job to job
        section_param["walltime"]=  walltime[i]
        section_param["total_core_count"]=   total_core_count[i]
        sect_list.append(section_param)
    
    return  sect_list
