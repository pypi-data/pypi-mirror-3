#
# DARE API
#

class Manager():
    # For coordinating the scheudled steps, compute and data engines

    #read dare conf file

    def startdare():
        #start pilot jobs
        #for each step in conf file
        # submit wu to wus or start a file transfer
        #wait for tasks to finish


class Compute():
    #take care of launching pilot jobs and just give a work unit service
    def ComputeService(pj_descs):
        # start pilot jobs
        # return a work unit service
        retrun wus

class Data():
    # transferring required data
    def SubmitFiletransfer(ft_descs):
        pass


class Updater():
    #To update jobs status to the database for WEB use if necessary
    pass

class State(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5
