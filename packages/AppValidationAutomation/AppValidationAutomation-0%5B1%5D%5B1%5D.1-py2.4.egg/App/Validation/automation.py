import string
from App.Validation.Automation.unix import *
from App.Validation.Automation.web import *
from App.Validation.Automation.purging import *
from App.Validation.Automation.alarming import *

__version__ = '0.1'

class AppValidationAutomation(Unix, Web, Alarming, Purging):
    """ A Validation Framework to check if your Application is running
        fine or not.This module can be used for Applications that are built
        on Unix and have a Web interface. The suite has the capabilty to
        check Application web urls for accessiblity,and also login into
        each of those urls to ascertain database connectivity along with
        sub url accessbility.One can also verfiy processes and mountpoints
        on the remote hosts which house the application. The password for
        logging into the web urls is stored in an encrypted file.The Module
        also has capability to test if Load Balancing and DNS Round Robin
        is funtioning.High Availabilty Web applications use Load Balancing
        and DNS Round Robin to add redundancy,high availability, and
        effective load distribution among the various
        servers(Web,Application, and Database servers).Further to frontend
	validations the module provides methods to validate the backend.To
        carryout backend verification it connects to remote hosts using
        SSH.Backend verfication involves checking if correct not of
        processe are running and file systems are
        accessible.AppValidationAutomation is driven by a tunable
        configuration file(sample config bundled with this
        distribution)which is formated in Windows .ini format.Please take a
        look at the configuration file under cfg/.
        AppValidationAutomation inherits Web, Unix, Purging and Alarming 
	parent classes and provides a common interface to the user.The user 
	is free to either  inherit AppValidationAutomation or the parent 
        classes.AppValidationAutomation does some ground work for the parents.
        For e.g. read the configuration file and convert the data in
	the format  needed by the parent classes.
    """

    def __init__(self):
        self.config = {}
        self.data   = {}

    def validate_urls(self, urls):
        """ Parses the configuration file and calls Web.validate_url method 
            for each web link.Handles password expiration along with authen
            -tication failure.On password expiry calls Web.change_web_pwd &
            Unix.change_unix_pwd to change password both at Web and Unix end.
            Returns True on success and False on failure.Also notifies via text
            page and email along with logging the error message.

            >>> auto_obj = AppValidationAutomation()
            >>> auto_obj.validate_urls()
            True
        """
        
        logger = logging.getLogger(__name__)
	logging.basicConfig(level=logging.WARN)
        inaccessible_urls = []

	if urls: pass
	else:
	    logger.error('No url to check accessbility')
	    return False

	for url in urls:
	    if self.validate_url(url) is False:
                if re.search(r'Pas.+?Exp',self.data['WEB_MSG']):
                    self.__handle_pwd_expiry(url)
                elif re.search(r'Auth.+?Fai',self.data['WEB_MSG']):
                    msg = self.data['WEB_MSG'] + "Incorrect credentials...Exiting!"
                    logger.error( msg )
                    sys.exit(1)
                elif re.search(r'Missdirected',self.data['WEB_MSG']):
                    msg = url + " : Inaccessible\nERROR: " + \
		                            self.data['WEB_MSG']
                    logger.error( msg )
                    inaccessible_urls.append(url)
                else:
                        logger.info(url + " : OK")

        if inaccessible_urls: 
	    mail_from    = self.config['COMMON.MAIL_FROM']
	    mail_to      = self.config['COMMON.MAIL_TO']
	    smtp         = self.config['COMMON.SMTP']
            subject      = "App Valildation -> Failed"
            body         = "Following links are inaccessible ->\n"
            body        += string.join(inaccessible_urls, "\n")  
            body        += "\n Refer logs under" + self.config['COMMON.LOG_DIR']

            self.mail(mail_from, mail_to, smtp, subject, body)
            logger.error(self.data['MAIL_MSG'])
            
	    mail_from    = self.config['COMMON.PAGE_FROM']
	    mail_to      = self.config['COMMON.PAGE_TO']

            self.page(mail_from, mail_to, smtp, subject, body)
            logger.error(self.data['PAGE_MSG'])

            return False

        return True
    
    def __handle_pwd_expiry(self, url):
        """Changes password for logging into web url both at unix and web
           level
        """
        logger = logging.getLogger(__name__)
	logging.basicConfig(level=logging.WARN)
        
        msg    = self.data['WEB_MSG'] + " : About to change at Web level :"
        if self.change_web_pwd(url) is True: logger.info("msg : OK")
        else : logger.error(msg + self.data['WEB_MSG']); sys.exit(1)           

        msg    = "About to change at Unix level :"
        if self.change_unix_pwd(url) is True: logger.info("msg : OK")
        else : logger.error(msg + self.data['UNIX_MSG']); sys.exit(1)

        return True


    def check_dnsrr_lb(self, url, max_requests=1, min_unique=1):
        """ Calls Web.dnsrr and Web.lb with parameters read from the configur
            -ation file.Returns True on success and False on failure.Also 
            notifies via text page and email along with logging the error message.

            >>> auto_obj = AppValidationAutomation()
            >>> auto_obj.check_dnsrr_lb()
            True
        """

	mail_from    = self.config['COMMON.MAIL_FROM']
	mail_to      = self.config['COMMON.MAIL_TO']
	smtp         = self.config['COMMON.SMTP']
        subject      = "App Valildation -> Failed"
        log_dir      = self.config['COMMON.LOG_DIR']
        logger       = logging.getLogger(__name__)
        fail_flag    = False
	logging.basicConfig(level=logging.WARN)

	if url: pass
	else:
	    logger.error('No url supplied to test dnsrr and lb')
	    return False
        
        if self.dnsrr(url, max_requests, min_unique) is True:
            logger.info("DNS Round Robin Validated ")
        else:
            fail_flag = True
            logger.error(url + self.data['WEB_MSG'])

            body  = "DNS Round Robin Validation Failed\n";
            body += "\nRefer logs under" + log_dir + "for details"
            self.mail(mail_from, mail_to, smtp, subject, body)
            logger.error(self.data['MAIL_MSG'])

        if self.lb(url, max_requests, min_unique) is True:
            logger.info("Load balancing Validated ")
        else:
            fail_flag = True
            logger.error(url + self.data['WEB_MSG'])

            body  = "Load Balancing Validation Failed\n";
            body += "\nRefer logs under" + log_dir + "for details"
            self.mail(mail_from, mail_to, smtp, subject, body)
            logger.error(self.data['MAIL_MSG'])

        if fail_flag is True: 
	    return False
        else: 
	    return True
       

    def validate_processes_mountpoints(self, validation_map=None):
        """ Performs process and mountpoint validation checks.Reads the process
            and mountpoint related info from the configuration file and calls 
            Unix.validate_process and Unix.validate_mountpoint to do the actual 
            work.True on success and False on failure.Also notifies via text page
            and email along with logging the error message.

            >>> auto_obj = AppValidationAutomation()
            >>> auto_obj.validate_processes_mountpoints()
            True
        """

	mail_from        = self.config['COMMON.MAIL_FROM']
	mail_to          = self.config['COMMON.MAIL_TO']
	smtp             = self.config['COMMON.SMTP']
	remote_pcmd_tmpl = self.config['COMMON.PROCESS_TMPL']
	remote_mcmd_tmpl = self.config['COMMON.FILESYS_TMPL']
        logger           = logging.getLogger(__name__)
	logging.basicConfig(level=logging.WARN)
	faulty_processes, faulty_mountpoints, unavailable_hosts  = [], [], []

        if validation_map: pass
	else:
	    logger.error('No remote_host/user/pwd/process/filesys Passed')
	    return False
	for remote_host in validation_map.keys():
	    user   = validation_map[remote_host]['USER']
            passwd = validation_map[remote_host]['PASSWORD']  
	    logger.info("Connecting to " +remote_host+ '...')
	    if self.connect_to(remote_host, user, passwd) is True:
                logger.info("Connection Successful!")
		logger.info("Validating Processes...")
		proc_tmpls = \
		    validation_map[remote_host]['PROCESSES'].split(',')
		for proc_tmpl in proc_tmpls:
		    if self.validate_process(proc_tmpl, remote_pcmd_tmpl) is True:
		        logger.info(remote_host+':'+proc_tmpl+':OK')
		    else:
		        logger.error(remote_host+':'+proc_tmpl+':NOT OK:'\
			                     +self.data['UNIX_MSG'])
                        faulty_processes.append(proc_tmpl)
	            
		logger.info("Validating Mountpoints...")
		filesystems = \
		    validation_map[remote_host]['FILE_SYS'].split(',')
                for fs in filesystems:
		    if self.validate_mountpoint(fs, remote_mcmd_tmpl) is True:
                        logger.info(remote_host+':'+fs+':OK')
		    else:
		        logger.error(remote_host+':'+fs+':NOT OK:'\
			                     +self.data['UNIX_MSG'])
		        faulty_mountpoints.append(fs)
            else:
	        unavailable_hosts.append(remote_host)

        if faulty_processes or faulty_mountpoints or unavailable_hosts:
	    subject = "App Validation -> Failed"
	    body    = "Unix Validation Failed\n\nRefer logs under" +\
	                    self.config['COMMON.LOG_DIR'] + " for details"
            self.mail(mail_from, mail_to, smtp, subject, body)
	    logger.info(self.data['MAIL_MSG'])

	    return False

        return True

if __name__ == '__main__':
    import doctest
    
    doctest.testmod()
