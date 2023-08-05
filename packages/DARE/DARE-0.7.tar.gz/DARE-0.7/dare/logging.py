import logging






        #create a logfile
        LOG_FILENAME = self.job_conf["log_filename"]
        print LOG_FILENAME
        self.logger = logging.getLogger('dare_multijob')
        hdlr = logging.FileHandler(LOG_FILENAME)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        #first info in log file
        self.logger.info("Job id  is "+ self.job_conf["jobid"]  )
        self.logger.info("RESOURCES used are " + self.job_conf["num_resources"] )
