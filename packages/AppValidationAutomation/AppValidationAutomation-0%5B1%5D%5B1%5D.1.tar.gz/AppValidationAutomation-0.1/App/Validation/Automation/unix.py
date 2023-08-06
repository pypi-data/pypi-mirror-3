import os, ssh, re
import logging
import types 
import pyDes

class Unix:
    """Bundles utilities to login a remote server and checks if correct no
       of processes are running and mountpoints are accessible.The remote
       hosts, processes and mountpoints are stored in configuration file.
       All member methods return True on success and False on failure.The
       error message is logged into the log file in case of error.
    """

    def __init__(self):
        self.config = {}
        self.data   = {}

    def connect_to(self, remote_host, user, passwd=None):
        """Connects to remote host passed as an argument,logs in using user
           and returns True on success.On failure, logs error message and 
           returns False.

           >>> auto_obj = Unix()
	   >>> auto_obj.connect_to(socket.getfqdn(),"user",passwd="hur")
           True
        """
        
	client    = ssh.SSHClient()
	if passwd is None:
	    key_dir   = self.config['COMMON.SSH_DIR']
	    key_files = [key_dir + '/' + key_file for key_file in \
	                                            os.listdir(key_dir)]
	client.set_missing_host_key_policy(ssh.AutoAddPolicy())
	logger = logging.getLogger(__name__)

        try:
	    if passwd is None:
	        client.connect(remote_host, port=22, username=user,\
	                                          key_filename=key_files)
	    else:
	        client.connect(remote_host, port=22, username=user,\
		                                           password=passwd)
	except ssh.AuthenticationException, err:
	    logger = logging.getLogger(__name__)
	    logger.error(user+" Unable to login into "+remote_host+ \
	                                             "\nERROR:"+str(err))
	    logger.info("Continuing with the next host...")
	    self.data['UNIX_MSG'] = str(err)

	    return False
	except ssh.SSHException, err:
	    logger = logging.getLogger(__name__)
	    logger.error(user+" Unable to login into "+remote_host+ \
	                                             "\nERROR:"+str(err))
	    logger.info("Continuing with the next host...")
	    self.data['UNIX_MSG'] = str(err)

	    return False
	
	self.data['CONN_STATE'] = client

        return True

    def validate_process(self, process_tmpl, remote_pcmd_tmpl):
        """Validates if process count of a given process is correct(as per
           process_tmpl passed as an argument.Returns True on sucess and False 
           on Failure. Also logs the error/process count message.

           >>> auto_obj = Unix()
	   >>> remote_pcmd_tmpl = \
	           'ps -eaf | grep -i %s | grep -v grep | wc -l'
	   >>> auto_obj.connect_to(socket.getfqdn(),"user",passwd="hur")
	   True
           >>> auto_obj.validate_process("ssh:3", remote_pcmd_tmpl)
           True
        """

	client          = self.data['CONN_STATE']

	match = re.search(r'(?P<proc>.*)\:(?P<count>.*)$', process_tmpl)
	process_name =  match.group('proc')
	min_count    =  match.group('count')
        remote_cmd   =  remote_pcmd_tmpl % process_name

	try:
	    stdin, stdout, stderr = client.exec_command(remote_cmd)
        except ssh.SSHException, err:
	    logger.error("Unable to fire cmd:"+remote_cmd+ \
	                                     "\nERROR:"+str(err))
	    logger.info("Continuing with the next cmd...")
	    self.data['UNIX_MSG'] = str(err)

	    return False
	
	process_count = stdout.readline().strip()
	process_count = process_count.strip('\n')

	if stderr.readline(): 
	    msg                 = "Remote Cmd Fired:"+remote_cmd+":Failed\n"
	    msg                += "ERROR:"+stderr.readline()
	    self.data['UNIX_MSG'] = msg

	    return False

	if process_count < min_count:
	    msg  = "Remote Cmd Fired:"+remote_cmd+"\n"
	    msg += "Expected "+min_count+" found "+process_count+" running"
	    self.data['UNIX_MSG'] = msg

	    return False

        return True

    def validate_mountpoint(self, mountpoint, remote_mcmd_tmpl):
        """Validate if the mountpoint if presented and accessible.Returns True
           on success and False on Failure.Logs the error message in case of
           Failure.

           >>> auto_obj         = Unix()
	   >>> remote_mcmd_tmpl = 'cd %s'
	   >>> auto_obj.connect_to(socket.getfqdn(),"user",passwd="hur")
	   True
           >>> auto_obj.validate_mountpoint("/export/home/", \
	           remote_mcmd_tmpl)
           True
        """

	client          = self.data['CONN_STATE']
        remote_cmd      =  remote_mcmd_tmpl % mountpoint

	try:
	    stdin, stdout, stderr = client.exec_command(remote_cmd)
        except ssh.SSHException, err:
	    logger.error("Unable to fire cmd:"+remote_cmd+
	                                      "\nERROR:"+str(err))
	    logger.info("Continuing with the next cmd...")
	    self.data['UNIX_MSG'] = str(err)

	if stderr.readline(): 
	    msg                 = "Remote Cmd Fired:"+remote_cmd+":Failed\n"
	    msg                += "ERROR:"+stderr.readline()
	    self.data['UNIX_MSG'] = msg

	    return False

        return True

    def change_unix_pwd(self):
        """Change password at unix level after password expiration at website
           Level.Uses secret passphrase, old password and new password while
           changing password.Returns True on success and False on failure.Also,
           logs the error message incase of failure.
        """
        old_pwd        = self.config['COMMON.OLD_PASSWORD']
        new_pwd        = self.config['COMMON.PASSWORD']
        home           = self.config['COMMON.DEFAULT_HOME']
        enc_pwd_file   = self.config['COMMON.ENC_PASS_FILE']
        secret_pphrase = self.config['pass_phrase']
        
        if old_pwd == new_pwd:
            self.data['UNIX_MSG'] = "Password change failed : old pwd = new pwd"
            return False
           
        try:
            key     = pyDes.des(secret_pphrase, pad=None, padmode=PAD_PKCS5)
            enc_pwd = key.encrypt(new_pwd)    
            
            enc_file_loc = home + '/' +  enc_pwd_file
            fhandle = open(enc_file_loc, "w")
            fhandle.write(enc_pwd)
        except IOError, err:
            logger.error("Password change failed :ERROR: "+str(err))
            return False
            
        return True

if __name__ == '__main__':
    import doctest, socket
    
    doctest.testmod()
