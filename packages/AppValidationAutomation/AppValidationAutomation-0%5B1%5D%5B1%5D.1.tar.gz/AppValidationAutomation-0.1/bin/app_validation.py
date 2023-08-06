import os
import re
import sys
import getopt
import logging
import profile
from types import *
from pyDes import *
from datetime import date, datetime, time
from ConfigParser import *
from App.Validation.automation import AppValidationAutomation
    
class AutoWrapper(AppValidationAutomation):

    def __init__(self):
        self.config = {}
        self.data   = {}

    def parse_cmdline(self):
        """Parse and store command line options and values"""

        try:
            opts, args = getopt.getopt(
                sys.argv[1:], "hc:p:f", ["help", "config=", "passphrase=", "forcerun"])
        except getopt.GetoptError, err:
            print str(err)
            self.display_usage()
            sys.exit(2)
    
        if len(opts) == 0:
            print "No cmd line args specified"
            self.display_usage()
            print "Exiting..."
            sys.exit(1)
            
        for o, a in opts:
            if o in ("-h", "--help"):
                self.display_usage()
                sys.exit()
            elif o in ("-c", "--config"):
                self.config['config_file'] = a
            elif o in ("-p", "--passphrase"):
                self.config['pass_phrase'] = a
            elif o in ("-f", "--forcerun"):
                self.config['forced_run']  = True
            else:
                assert False, "Unhandled Option"

        return True

    def store_config(self):
        """Parse and store configuration file in self.config"""

        try:
            config = ConfigParser()
            config.read(self.config['config_file'])
         
            if len(config.sections()) < 1:
                print "Config file missing min. data to proceed.Exiting..."
                sys.exit(1)

            for section in config.sections():
                for kv_pair in config.items(section):
                    key = section + '.' + kv_pair[0].upper()
                    self.config[key] = kv_pair[1]

            #Read encrypted stored in config file
            pass_file \
                = self.config['COMMON.DEFAULT_HOME'] + '/' + self.config['COMMON.ENC_PASS_FILE']
            fhandle = open(pass_file)
            encrypted_password = fhandle.read()
            self.config['COMMON.PASSWORD'] \
                = self.__decrypt_password(encrypted_password)
        except ParsingError, err:
            print "Exception in parsing config file...Exiting!",str(err)
            sys.exit(1)
        except NoSectionError, err:
            print "Section missing.Cannot proceed further...Exiting!",str(err)
            sys.exit(1)
        except IOError, err:
            print "Unable to read pass_file ...Exiting!",str(err)
            sys.exit(1)

        return self.config # for testing


    def create_logfile(self):
        """Creates Log file"""

        log_dir    = self.config['COMMON.LOG_DIR'] + '/'
        date_stamp = date.today()
        log_extn   = '.' + self.config['COMMON.LOG_EXTN']
        log_file   = log_dir + os.path.basename(sys.argv[0]) + \
	             str(date_stamp) + log_extn
        log_level  = self.config['COMMON.LOG_LEVEL']

        logging.basicConfig(filename=log_file,level=logging.INFO)

        return True


    def chk_mtce_on(self):
        """Check if in a Maintenance window"""

        mtce_window          = self.config['COMMON.MTCE_WINDOW']
        day_map = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}
        mtce_day, mtce_time  = mtce_window.split() 
        mtce_start, mtce_end = mtce_time.split('-')
        mtce_start, mtce_end = int(mtce_start), int(mtce_end)

        #Look out for a better way
        time_stamp       = str(datetime.now()).split()[1:]
        hour, min, sec   = time_stamp[0].split(':', 2)
        time_now         = int(hour + min)
        year, month, day = str(date.today()).split('-')
        day = date(int(year), int(month), int(day)).isoweekday()
        day = day_map[day]
     
        if day == mtce_day and (hour >= mtce_start and hour <= mtce_end):
            return True
        else:
	    return False
         

    def display_usage(self):
        """Print Script's Usage"""

        use = "Script run with incorrect parameters.Usage:\n "
        use += " %r -c <path_to_configfile> -p <passphrase> -f \n     OR \n"
        use += " %r --config <path_to_configfile> --passphrase  <pssphrase> --forcerun"

        print use % (sys.argv[0], sys.argv[0])

    
    def __decrypt_password(self, encrypted_password):
        """Decrypt Password"""

        key = des(self.config['pass_phrase'], pad=None, padmode=PAD_PKCS5)

        return key.decrypt(encrypted_password)
        

if __name__ == "__main__":
            
    auto_obj  = AutoWrapper()
    logger = logging.getLogger(__name__)
    #profile.Profile.bias = 2.5e-06
    #ret_value = profile.run('auto_obj.parse_cmdline()')
    #ret_value = profile.run('auto_obj.store_config()')
    #ret_value = profile.run('auto_obj.create_logfile()')
    #ret_value = profile.run('auto_obj.purge()')
    #ret_value = profile.run('auto_obj.validate_urls()')
    #ret_value = profile.run('auto_obj.check_dnsrr_lb()')
    ret_value = auto_obj.parse_cmdline()
    ret_value = auto_obj.store_config()
    ret_value = auto_obj.create_logfile()

    #prepare ground for log file purging
    log_dir        = auto_obj.config['COMMON.LOG_DIR']
    log_extn       = auto_obj.config['COMMON.LOG_EXTN']
    log_ret_period = int(auto_obj.config['COMMON.RET_PERIOD']) * 24 * 3600
    ret_value      = auto_obj.purge(log_dir, log_ret_period, log_extn)

    #Prepare ground for url validation,dns round robin,load
    #balancing,process and mountpoint validation
    only_urls      = re.compile(r'LINKS')
    only_processes = re.compile(r'PROCESSES')
    validation_map = {}
    urls           = []
    url            = auto_obj.config['COMMON.LINK']
    max_requests   = int(auto_obj.config['COMMON.MAX_REQ'])
    min_unique     = int(auto_obj.config['COMMON.MIN_UNQ'])

    if      'COMMON.REMOTE_USER' in auto_obj.config \
        and auto_obj.config['COMMON.REMOTE_USER'] is not None:
        user = auto_obj.config['COMMON.REMOTE_USER']
    else:
	user = os.environ['USER']

    for key in auto_obj.config.keys():
        if only_processes.search(key):
            match = re.search(r'(?P<host>.*)\..*$', key)
	    hostname = match.group('host')
	    mount_key = hostname+'.FILE_SYS'
            validation_map[hostname] = \
	        {'USER': user, 'PASSWORD': None, \
		 'PROCESSES': auto_obj.config[key], \
		 'FILE_SYS': auto_obj.config[mount_key]}
        if only_urls.search(key):
	    ws_urls = auto_obj.config[key].split(',')
	    [urls.append(ws_url) for ws_url in ws_urls]
	    
    ret_value = auto_obj.validate_urls(urls)

    ret_value = auto_obj.check_dnsrr_lb(url, max_requests, min_unique)

    ret_value  = \
        auto_obj.validate_processes_mountpoints(validation_map)

    if auto_obj.chk_mtce_on() is True and 'forced_run' not in auto_obj.config:
        msg  = "Maintenance is on - " + auto_obj.config['COMMON.MTCE_WINDOW']
        msg += " Cannot proceed.To run in maintenance use forcerun cmd switch"

        logger.info(msg)
        print msg
        auto_obj.display_usage()

        sys.exit(1)
