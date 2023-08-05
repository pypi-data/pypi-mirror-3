import os
import time

from compute import Compute
from updater import Updater
from data import Data
from conffileparser import ConfFileParser

class Manager():

    def __init__(self, dcfw, jobid, steps_order):


         
        try: 
            DARE_JOB_DIR = os.path.join(os.getenv("HOME"), "dare", "jobs",str(jobid))
        except:
            DARE_JOB_DIR = os.path.join("/tmp", "dare", "jobs",str(jobid))

        #application working directory
        print "[INFO] Working Directory is " , DARE_JOB_DIR


        ###############  write the config file for dare.py        ##################################
        dare_conffile = os.path.join(DARE_JOB_DIR, str(jobid) +"-darejob.cfg")

        print "[INFO] Wrinting conf file", dare_conffile
        dcfw.write(dare_conffile, jobid, steps_order)

        self.wus = []
        self.wu_start_times = {}
        self.wu_states = {}
        #todo load conf file

        self.dcfp = ConfFileParser(dare_conffile)

        self.webupdate= "false"

        self.DAREJOB=self.dcfp.dict_section("DAREJOB")

        self.resource_list = []

        for i in range(0, int(self.DAREJOB["num_resources"])):
              self.resource_list.append(self.dcfp.dict_section("resource_"+ str(i) ))

        self.num_steps = self.DAREJOB["num_steps"]
        self.steps_order = self.DAREJOB["steps_order"]
        self.wus = {}
        for i in range(0, int(self.DAREJOB["num_wus"])):
            self.wus["wu_"+str(i)]= self.dcfp.dict_section("wu_"+ str(i))

        self.webupdater = Updater()

    def start(self):

        #create multiple manyjobs
        print "Create Compute Engine service "

        cmps = Compute()
        cmps.ComputeService(self.resource_list)
        data = Data()
        total_number_of_jobs=0


        ### run the steps
        wus_count = 0

        for STEP in self.steps_order.split(","):
            starttime = time.time()

            #job started update status
            self.webupdater.update_status(self.webupdate,self.DAREJOB["jobid"], "Running"," In step " + str(STEP))

            step_wus = self.DAREJOB[STEP].split(',')
            print STEP, step_wus
            p = []
            if (str(STEP)) not in self.DAREJOB["ft_steps"].split(','):
                 ### submit the each step wus to bigjob
                 for i in range(0 ,len(step_wus)):
                     print self.wus[step_wus[i]]
                     wu = cmps.submit_wu(self.wus[step_wus[i]])
                     wus_count = wus_count +1

                 cmps.wait_for_wus()
            else:

                 for i in range(0 ,len(step_wus)):

                     p = data.submit_filetransfer(self.wus[step_wus[i]])
                     wus_count = wus_count +1

                 data.wait_for_transfers()

            runtime = time.time()-starttime

            #all jobs done update status
            self.webupdater.update_status(self.webupdate, self.DAREJOB["jobid"], "Done","")


