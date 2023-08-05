#!/usr/bin/env python

#Author Sharath Maddineni
"""
A tool to run applications in Distributed environments
depends on Troy-BigJob and local file trasfer mechanisms like
"""

import sys
import os
import time
import pdb
import traceback

#add troy path

try:
    from troy import Callback
except:
    if os.getenv("TROY_HOME")!=None:
       TROY_HOME= os.getenv("TROY_HOME")
    else:
       TROY_HOME = "/home/cctsg/software/troy_trunk/"

    sys.path.insert(0,TROY_HOME)
from troy import Callback
from troy import PilotJobService, PilotJobDescription
from troy import WorkUnitService, WorkUnitDescription
from troy import State


class Compute():

    def __init__(self):
        self.wus = WorkUnitService()
        self.wu_repo = []

    def ComputeService(self,pj_descs):

        # Initiate the PilotJobService
        for pj_desc_conf in pj_descs:
            pjs = PilotJobService()
            # Create a PilotJob on Ranger, let the "system" decide which type
            pj_desc = PilotJobDescription()
            pj_desc.total_core_count = pj_desc_conf['total_core_count']
            pj_desc.processes_per_host =  pj_desc_conf['processes_per_host']
            pj_desc.working_directory =  pj_desc_conf['working_directory']
            pj_desc.wall_time_limit = pj_desc_conf['walltime']

            print "[DAREINFO]", pj_desc_conf
            pj = pjs.create_pilotjob(pj_desc_conf['resource_url'], pj_desc, pj_desc_conf['type'])

        # Initiate the WorkUnitService
        self.wus.add(pjs)

    def submit_wu(self, wu_desc_conf):
       # print "[INFO]", wu_desc_conf
        wu_desc = WorkUnitDescription()
        wu_desc.executable =  wu_desc_conf['executable']
        wu_desc.arguments = wu_desc_conf['arguments'].split(",")
        wu_desc.environment = wu_desc_conf['environment'].split(",")
        wu_desc.number_of_processes = wu_desc_conf['number_of_processes']
        wu_desc.working_directory = wu_desc_conf['working_directory']
        wu_desc.spmd_variation = wu_desc_conf['spmd_variation']
        wu_desc.output= wu_desc_conf['output']
        wu_desc.error = wu_desc_conf['error']
        wu = self.wus.submit(wu_desc)

        self.wu_repo.append(wu)

    def wait_for_wus(self):
        while self.wu_repo:
            for w in self.wu_repo:
                print 'Workunit: %s (state: %s)' % (w.wu_id, w.get_state())

                if w.get_state() == State.Done:
                    print 'Workunit is done, removing from list'
                    self.wu_repo.remove(w)

                if w.get_state() == State.Failed:
                    print 'Workunit is Failed, removing from list'
                    self.wu_repo.remove(w)


            print 'Application going to sleep'
            time.sleep(5)
