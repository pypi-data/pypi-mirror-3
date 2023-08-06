The README file helps one on the Generation of SSH Public/Private Keys
and How to use the config file.

How to generate Public/Private key pairs for SSH:

The utility ssh-keygen is used to generate that Public/Private key
pair:

user@localhost>ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/user/.ssh/id_rsa.
Your public key has been saved in /home/user/.ssh/id_rsa.pub.
The key fingerprint is: f6:61:a8:27:35:cf:4c:6d:13:22:70:cf:4c:c8:a0:23

The command ssh-keygen -t rsa initiated the creation of the key
pair.Adding a passphrase is not required so just press enter.The
private key gets saved in .ssh/id_rsa. This file is read-only and only
for you. No one else must see the content of that file, as it is used
to decrypt all correspondence encrypted with the public key. The public
key gets stored in .ssh/id_rsa.pub.The content of the id_rsa.pub needs
to be copied in the file .ssh/authorized_keys of the system you wish to
SSH to without being prompted for a password. 
Here are the steps:

Create .ssh dir on remote host(The dir may already exist,No issues):

user@localhost>ssh user@remotehost mkdir -p .ssh 
user@remotehost's password:

Append user's new public key to user@remotehost : .ssh/authorized_keys
and enter user's password:
user@localhost>cat .ssh/id_rsa.pub | ssh user@remotehost 'cat >>
.ssh/authorized_keys' user@remotehost's password:

Test login without password:
user@localhost>ssh user@remotehost
user@remotehost>hostname
remotehost

How to Use configuration file:
AppValidationAutomation is driven by a tunable configuration file.The
configuration file is in Windows .ini format.The wrapper script using
App::Validation::Automation needs to either read the configuration file
or build the configuration itself.The configuration file is broadly
divided into two parts COMMON and Remote host specific.The COMMON part
contains generic info used by AppValidationAutomation not specific to
any host.

Example:

[COMMON]
#User to login into Web links
USER = web_user
#Common User to login into remote host
REMOTE_USER = user
#Post link MAX_REQ no of times, used while testing Load #Balancing and
DNS round robin functionality
MAX_REQ = 10
#Minimum distinct redirected uris to ascertain Load Balancing #and DNS
round robin is working fine
MIN_UNQ = 2
#Log file extension
LOG_EXTN = log
#Print SSH debugging info to STDOUT
DEBUG_SSH = 1
#Try SSH2 protocol first and then SSH1
SSH_PROTO = '2,1'
#Private keys for each server(AA,KA...) used for SSH
ID_RSA = /home/user/.ssh/id_rsa_AA,/home/user/.ssh/id_rsa_KA
MAIL_TO = 'xyz@yahoo.com,123@gmail.com'
PAGE_TO = '8168168164@vodafone.in'
FROM = xy@localhost.com
SMTP = localhost.com
#Text file containing Encrypted password for USER
ENC_PASS_FILE = pass.txt
DEFAULT_HOME = /home/App/Validation
LOG_DIR = /home/App/Validation/log
#Log file retention period, delete log file older than 5 days
RET_PERIOD = 5
#Main Weblink used for Load Balancing and DNS round robin test
LINK = http://cpan.org
#Remote command fired to get process count.%s is replaced process name
PROCESS_TMPL = ps -eaf | grep -i %s | grep -v grep | wc -l
#Remote command fired to check filesystem.%s is replaced by filesystem
name
FILESYS_TMPL = cd %s

#FQDN of remote server
[AA.xyz.com]
#Processes to verify on remote hosts along with their minimum quantity
PROCESSES = BBL:1, EPsrv:1, WEBLEPsrv:1
#Filesystems to verify on remote hosts
FILE_SYS = /test, /export/home

#FQDN of remote server
[KA.xyz.com]
#Processes to verify on remote hosts along with their minimum quantity
PROCESSES = BBL:1, EPsrv:1, WEBLEPsrv:1
#Filesystems to verify on remote hosts
FILE_SYS = /test, /export/home
#Links specific to KA server these links are checked for accessibility
LINKS = http://KA.xyz.com:7000,http://KA.xyz.com:7100
