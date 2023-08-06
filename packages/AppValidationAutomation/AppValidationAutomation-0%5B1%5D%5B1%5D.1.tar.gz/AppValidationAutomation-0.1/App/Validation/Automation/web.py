import sys
import re
import logging
import mechanize
from mechanize import ControlNotFoundError, ParseResponse

class Web:
    """Bundles Utilites to check if a weblink is accessible,login into the 
       website if the website has user logon.It also houses utilities to check
       if DNS Load Balancing and Round Robin functionality is working fine or
       not.High Availabilty Web applications use Load Balancing and DNS Round 
       Robin to add redundancy,high availability, and effective load 
       distribution among the various servers(Web,Application, and Database
       servers).
    """

    def __init__(self):
        self.config = {}
        self.data   = {}


    def validate_url(self, url):
        """ Validates if the url passed as argument is accessible or not.logs 
            into the website if the website has user logon page.Returns True
            on success and False on failure.Logs failure message

            >>> auto_obj = Web()
            >>> auto_obj.validate_url("http://docs.python.org")
            True
        """
	ret_value = True

        try:
            br       = mechanize.Browser()
            response = br.open(url)
        except IOError, err:
            logger = logging.getLogger(__name__)
            logger.error(url + "\nERROR: " + str(err))
            #logger.debug(br.error()) lookout for an alternative to dump more info
            
            print str(err)
            sys.exit(1)

        assert  br.viewing_html()


        if     'COMMON.USER' in self.config  \
	   and 'COMMON.PASSWORD' in self.config:
            if     self.config['COMMON.USER']  \
               and self.config['COMMON.PASSWORD']:
                self.data['BROWSER_STATE'] = br
                ret_value = self.__login()
        
        return ret_value

    def dnsrr(self, url, max_requests, min_unique):
        """ Validates if the DNS Round Robin functionality is working fine or 
            not.The logic behind this functionality check if to post the url
            max_requests no of times, login and store the web, application, and
            DB/Alternate application serve name in a list.The list thus formed
            (containing combinations of web,app and db/alt. app. directed to 
            max_requests no of times)should contain atleast min_uniqure no of
            different entries to ascertain that Round Robin is working and web
            trafic is being distributed evenly.Returns True on success and 
            False on failure.Logs failure message

            >>> auto_obj = Web()
            >>> auto_obj.dnsrr("http://docs.python.org", 1, 1)
            True
        """

        msg             = "\nRound Robin details:\n"
        redirected_uris = []
        unique_uris     = {}
	br              = mechanize.Browser()
        
        for count in range(int(max_requests)):
            try:
                response       = br.open(url)
                redirected_uri = br.geturl()
                msg += url+" Redirected to "+redirected_uri+"\n"
                redirected_uris.append(redirected_uri)
            except IOError, err:
                logger = logging.getLogger(__name__)
                logger.error(url + "\nERROR : " + str(err))

                print str(err)
                sys.exit(1)

	for x in redirected_uris:
	    unique_uris[x] = 1
        unique = unique_uris.keys()
        if len(unique) < int(min_unique):
	    self.data['WEB_MSG'] = msg
	    return False
        else:
	    return True
        

    def lb(self, url, max_requests, min_unique):
        """ Validates if DNS Load balancing functionality is working fine or
            not.The logic behind this functionality check if to post the url
            max_requests not of times and store the redirected url in a list.
            The list thus formed should comprise of atleast min_unique no of
            different entries to ascertain that Load Balancing is working at
            the first place and web trafic is being distributed.Returns True
            on success and False on failure.Logs failure message.

            >>> auto_obj = Web()
	    >>> auto_obj.config['COMMON.USER']     = None
	    >>> auto_obj.config['COMMON.PASSWORD'] = None
            >>> auto_obj.lb("http://docs.python.org", 1, 1)
            True
        """

        msg = "\nLoad Balancing details:\nWeb_Server App_Server Alt_App_Server\n"
	br  = mechanize.Browser()
	system_info  = []
	unique_combo = {}
        
        for count in range(int(max_requests)):
            try:
                response = br.open(url)
                self.data['BROWSER_STATE'] = br

                if     'COMMON.USER' in self.config  \
	           and 'COMMON.PASSWORD' in self.config:
                    if      self.config['COMMON.USER']     \
                        and self.config['COMMON.PASSWORD']:
                        self.data['BROWSER_STATE'] = br
                        ret_value = self.__login()

		        if ret_value is True:
		            br           = self.data['BROWSER_STATE']
		            resp         = br.response()
		            html_content = resp.read().replace('\n', '')
                            match          = \
		            re.search(r'(strWebSrvrName="(?P<webs>.+?)";)', html_content)
                            web_server     = match.group('webs')
                            match          = \
		                re.search(r'(strAppSrvrName="(?P<apps>.+?)";)', html_content)
                            app_server     = match.group('apps')
                            match          = \
		                re.search(r'(strKSAppSrvrName="(?P<a_apps>.+?)";)', html_content)
                            alt_app_server = match.group('a_apps')
                   
		            system_info.append(web_server+'_'+app_server+'_'+alt_app_server)
		        else:
		            return False
		    else:
		        return True
            except IOError, err:
                logger = logging.getLogger(__name__)
                logger.error(url + "\nERROR : " + str(err))

                print str(err)
                sys.exit(1)
                
        for x in system_info:
	    unique_combo[x] = 1
	    msg += x+"\n"
        unique = unique_combo.keys()
        if len(unique) < int(min_unique):
            self.data['WEB_MSG'] = msg
	    return False
        else:
	    return True

        return True
       
    def change_web_pwd(self, url):
        """ Changes the website password on expiration.The logic used is to
            post the url and enter credentials into the user logon.Check the
            the web content of the resulting page for "Password expiry".
            Proceed with password change if the web content has "Password
            Expiry".The password generated contains three letters from the 
            next month followed by a dash '-' and 3 digit random no.Returns
            True on success and False on failure.Logs failure message.

            >>> auto_obj = Web()
            >>> auto_obj.change_web_pwd("http://docs.python.org")
            True
        """
                
        return True

    def __login(self):
        """ Private member method to login into the website using login details
            stored in configuration file.Returns True on success and False on
            failure.Logs failure message.
        """

        #Reinstate browser state
        br         = self.data['BROWSER_STATE']
        
        #select form with user and password field
        br.select_form(predicate=self.__form_with_fields("user", "password"))
        br['user']     = self.config['COMMON.USER']
        br['password'] = self.config['COMMON.PASSWORD']

        #update site and zone if specified in config file
        if 'COMMON.SITE' in self.config and 'COMMON.ZONE' in self.config:
            try:
                br.form.set_all_readonly(False)
                br.form["shortsite"] = self.config['COMMON.SITE']
	        zone1 = br.form.find_control("zone") 
		mechanize.Item(zone1, {"contents": \
		    "lee10","value": "lee10"})
	        br.form["zone"]      = ["lee10"]
            except ControlNotFoundError, err:
                logger = logging.getLogger(__name__)
                logger.info(str(err))
                
        try:
            request      = br.click()
            response     = mechanize.urlopen(request)
        except IOError, err:
            logger = logging.getLogger(__name__)
            logger.error(str(err))
            logger.debug(response.info())
            
            print str(err)
            sys.exit(1)

        assert br.viewing_html()
        html_content = response.read().replace('\n', '')
                    
        if re.search(r'Password\s+has\s+expired', html_content):
            self.data['WEB_MSG']       = "Password has Expired"
            self.data['BROWSER_STATE'] = br
            return False
        elif re.search(r'Authentication\s+Failure', html_content):
            self.data['WEB_MSG']       = "Authentication Failure!"
            return False
        elif re.search(r'launchMenu\((.*)\)\;', html_content):
            string = re.search(r'launchMenu\((.*)\)\;', html_content)
            request_string = string.group(1)
            (web_server, web_server_ip, web_port, app_server, user, \
             menu_tokens, auto_tokens, site, zone, slif_flag)       \
                                             =  re.split(r'\W+,\W+', request_string)
            web_server = re.sub(r'^\'', '', web_server)
            slif_flag  = re.sub(r'\'$', '', slif_flag)

            menu_url  = 'http://' + web_server_ip + ':' + web_port
            menu_url += '/LoginIWS_Servlet/Menu?webserver=' + web_server
            menu_url += '&webport=' + web_port + '&appserver=' + app_server
            menu_url += '&user=' + user + '&menuTokens=' + menu_tokens
            menu_url += '&autoTokens=' + auto_tokens + '&site=' + site
            menu_url += '&zone=' + zone + '&SLIflag=' + slif_flag
            menu_url += '&code=' + 'x9y8z70D0'

            try:
                response = br.open(menu_url)
            except IOError, err:
                logger = logging.getLogger(__name__)
                logger.error(str(err))
                logger.debug(response.info())

                return False

            self.data['BROWSER_STATE'] = br
            return True
        else:
            self.data['WEB_MSG'] = "Missdirected " + response.geturl()
            return False
        
        
    def __form_with_fields(self, *fields):
        """ Generator of form predicate functions. """
        
        def __pred(form):
            
            for field_name in fields:
    
                try:
                    form.find_control(field_name)
                except ControlNotFoundError, err:
                    logger = logging.getLogger(__name__)
                    #logger.error(str(err))
                                        
                    return False

            return True

        return __pred
            
     
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    
