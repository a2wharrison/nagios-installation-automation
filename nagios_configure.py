#!/usr/bin/env python
##Works only on cPanel installations now
#Version: 1.02
import paramiko
import os
import tempfile
import re
import sys
import logging
###################
##Checking root privilage
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
###################
class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[0;32m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        DARKBLUE= '\033[0;34m'
        BROWN='\033[0;33m'

#####################################################
#logging at /var/log/naginstall.log
#####################################################
if not os.path.exists('/var/log/naginstall.log'):
    open('/var/log/naginstall.log', 'w').close() 
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/log/naginstall.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)
#####################################################


def CCONF(hostip, client_passwd):    
    t1 = tempfile.NamedTemporaryFile(delete=False) #Create temporary file
    SCFILE=t1.name #Assign name of temp file to variable
    DCFILE=t1.name #Assign name of temp file to variable
    logger.debug("Temp files created[for passing client side configurations]")    
    open(SCFILE, 'w').close()
    with open(SCFILE, 'a') as t:          # Write program to temporary file
        t.write("""
import os
import subprocess
import commands
import shutil
import tarfile

purl = "http://198.50.243.114/nagios-plugins-1.4.16.tar.gz"
nurl = "http://198.50.243.114/nrpe-2.13.tar.gz"

status, output = commands.getstatusoutput("dpkg -s nrpe")
print status
print output
str = 'install ok installed'
if str in output:
 print "nrpe installed"
 flgnrp=0
else:
 print "nrpe Not installed"
 flgnrp=1

if flgnrp:
 print "Proceeding to install nrpe.."
 os.chdir('/usr/local/src') #original
 print "Changing directory..."
 print os.getcwd()
 print "Downloading nagios plugin file"
 output = os.system("wget "+purl) #os.system command
 print output
 print "Extracting file.."

 fname1 = "nagios-plugins-1.4.16.tar.gz"
 tar = tarfile.open(fname1, "r:gz")
 tar.extractall()
 tar.close()

 print "Changing directory..."
 os.chdir('/usr/local/src/nagios-plugins-1.4.16') #original
 print os.getcwd()
 print "Installing plugin..."
 out1 = os.system("./configure")
 print out1
 if out1:
  print "Configure error!"
  #os._exit(0)
 out2 = os.system("make")
 print out2
 if out2:
  print "make error!"
  #os._exit(0)
 out3 = os.system("make install")
 print out3
 if out3:
  print "make install error!"
  #os._exit(0)
 print "Plugin installed"
 print "Adding nagios user"
 out4 = os.system("adduser nagios")
 print out4
 if out4:
  print "adding nagios user error!"
  #os._exit(0)
 out5 = os.system("usermod -s /sbin/nologin nagios")
 print out5
 out6 = os.system("chown nagios.nagios /usr/local/nagios")
 print out6
 out7 = os.system("chown -R nagios.nagios /usr/local/nagios/libexec")

 print "Changing directory...."
 os.chdir('/usr/local/src')

 print "Downloading nrpe file"
 out8 = os.system("wget "+nurl)
 print "Extracting file.."
 
 fname2 = "nrpe-2.13.tar.gz"
 tar = tarfile.open(fname2, "r:gz")
 tar.extractall()
 tar.close()

 print "Changing directory..."
 os.chdir('/usr/local/src/nrpe-2.13') #original
 out10 = os.system("./configure --with-ssl=/usr/bin/openssl --with-ssl-lib=/usr/lib/x86_64-linux-gnu")
 print out10
 if out10:
  print "Configure error!"
  #os._exit(0)
 out11 = os.system("make all")
 out12 = os.system("make install-plugin")
 out13 = os.system("make install-daemon")
 out14 = os.system("make install-daemon-config")
 F1 = "/usr/local/src/nrpe-2.13/init-script.in"
 F2 = "/etc/init.d/nrpe"
 shutil.copy2(F1, F2)
 
 os.chmod('/etc/init.d/nrpe', 0755)

 fpath="/etc/init.d/nrpe"
 sstr1="NrpeBin=/usr/local/nagios/bin/nrpe\\n"
 sstr2="NrpeCfg=/usr/local/nagios/etc/nrpe.cfg\\n"

 with open(fpath, 'r+') as f:
  lines = f.readlines()
  f.seek(0)
  f.truncate()
  for line in lines:
   if "NrpeBin=" in line:
	line=line.replace(line,sstr1)
   if "NrpeCfg=" in line:
	line=line.replace(line,sstr2)
   f.write(line)
 f.close()
 
 print "Specifying port in /etc/services"
 with open("/etc/services", "a") as myfile:
  myfile.write("nrpe 5666/tcp\\n")
 f.close()

 print "Adding nagios server IP in /usr/local/nagios/etc/nrpe.cfg"
 fpath = '/usr/local/nagios/etc/nrpe.cfg'
 addIP = ',aa.bb.cc.dd\\n'  #######Replace with Nagios Server Main IP##########
 with open(fpath, 'r+') as f:
  lines = f.readlines()
  f.seek(0)
  f.truncate()
  for line in lines:
   if "allowed_hosts=" in line:
	line=line.strip('\\n')+addIP
   f.write(line)
 f.close()

 out15 = os.system("/etc/init.d/nrpe restart")
 if out15:
  print "NRPE restart error!"
        """)
        t.close

##Enable for execution


    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(port=22, hostname=hostip, username='root', password=client_passwd)
    sftp = client.open_sftp()
    logger.info("Connecting to client server...")    
    sftp.put(SCFILE, DCFILE) # Copy temporary file to destination
    logger.info("Connected.Copying temp file to destination...")
    sftp.close
    
    stdin, stdout, stderr = client.exec_command('python '+DCFILE)
    logger.info(stdout)
    logger.error(stderr)    
    for line in stdout.readlines(): # Return the remote output, use stderr for printing errors
        print line.strip('\n')
        
    client.exec_command('rm -f '+DCFILE)
    client.close()
    os.remove(SCFILE)
    logger.info("Client side script execution complete")   
     
def HCONF():
    #Function for email validation
    def validateEmail(email):  
    
        if len(email) > 7:
            if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email):
                return 1
        return 0
    
    #Function for IP validation
    def is_ipv4(ip):
        match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", ip)
        if not match:
            return False
        quad = []
        for number in match.groups():
            quad.append(int(number))
        if quad[0] < 1:
            return False
        for number in quad:
            if number > 255 or number < 0:
                    return False
        return True
    
    #Function to list existing/choose clients
    def get_cl(cld,n):
        os.chdir(cld)
        all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
        if n == 1:
            for dir in all_subdirs:
                print dir
        elif n == 2:
            dlen = len(all_subdirs)
            for i in range(0, dlen):
                print str(i+1)+"\t-\t"+all_subdirs[i]
            chd=int(raw_input("Enter your choice: "))
            chd=chd-1
            return(cld+all_subdirs[chd])
                
    #Function to list existing/add new clients
    def get_cc(cld):
        print cld
        while True:
            print "1.Choose an existing client contact\n2.Add a new client contact"
            ch=int(raw_input("Enter your choice :"))
            if ch == 1:
                os.chdir(cld)
                curr=os.getcwd()
                print "-----"+curr+"---"
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                flen=len(files)
                print "Choose a client name"
                for i in range (0, flen):
                    print str(i+1)+'\t-\t'+os.path.splitext(files[i])[0]
                cnch=int(raw_input("Enter your choice : "))
                cname=os.path.splitext(files[cnch-1])[0]
                print "You have chosen "+cname
                return cname
            if ch == 2:
                while True:
                    cname=raw_input("Enter the client-contact name: ")
                    cname=cname.lower()
                    cname=''.join(e for e in cname if e.isalnum())
                    CCFG=cld+cname+'.cfg'
                    if os.path.isfile(CCFG):
                        print "The Client-Contact name already exits. Please choose a different one"
                    else:
                        break
                while True:
                    cmail=raw_input("Enter the client admin email: ")
                    if validateEmail(cmail):
                        break
                    else:
                        print 'Please enter a valid email address'
                open(CCFG, 'w').close()
                with open(CCFG, 'a') as cfile:
                    cfile.write("""
define contact{
        contact_name            <company>
        use                     generic-contact
        alias                   <company> admin
        service_notification_options w,u,c,r
        host_notification_options d,u,r
        email                  <client email>
        }

define contactgroup{
        contactgroup_name       <company/contactname>
        alias                   <company> admins
        members                 <contact_name mentioned above>,ssages
        }

                    """)
                cfile.close()
                s1='<company>'
                s2='<client email>'
                s3='<company/contactname>'
                s4='<contact_name mentioned above>'
                s=open(CCFG).read()
                if s1 or s2 or s3 or s4 in s:
                    s=s.replace(s1, cname)
                    s=s.replace(s2, cmail)
                    s=s.replace(s3, cname)
                    s=s.replace(s4, cname)
                    f=open(CCFG, 'w')
                    f.write(s)
                    f.flush()
                    f.close()
                return cname
            else:
                print "Enter a valid choice"
    
    
    NBIN='/usr/local/nagios/bin/nagios'
    NCFG='/usr/local/nagios/etc/nagios.cfg'
    NCON='/usr/local/nagios/etc/objects/contacts/'
    NCLI='/usr/local/nagios/etc/objects/clients/'

    
    out = os.system(NBIN+" -v "+NCFG+"&>/dev/null")
    if out == 0:
        cflag = 0
        while True:
            och=int(raw_input("1: List all clients\n2: Choose existing client\n3: Add new client\nEnter your choice : "))
            if och == 1:
                get_cl(NCLI,1)
            elif och == 2:
                HDIR = get_cl(NCLI,2)
                HDIR=HDIR+'/'
                cflag=1
                print HDIR
                break
            elif och == 3:
                cflag=2
                break
            else:
                print "Please enter a valid choice"
    
        #New client
        if cflag == 2:
            #os.system("ls "+NCON+" | grep -v 'contacts.cfg.Template' | sed s/\.[^\.]*$//")
            while True:
                cname=raw_input("Enter the client-contact name: ")
                cname=cname.lower()
                cname=''.join(e for e in cname if e.isalnum())
                CCFG=NCON+cname+'.cfg'
                if os.path.isfile(CCFG):
                    print "The Client-Contact name already exits. Please choose a different one"
                else:
                    break
            while True:
                cmail=raw_input("Enter the client admin email: ")
                if validateEmail(cmail):
                    break
                else:
                    print 'Please enter a valid email address'
            while True:
                name=raw_input("Enter the name of the client: ")        
                name=name.lower()
                name=''.join(e for e in name if e.isalnum())
                HDIR=NCLI+name+'/'
                if os.path.isdir(HDIR):
                    print "The Client name already exists. Please choose a different one"
                else:
                    break
            sname=raw_input("Enter the name of the server: ")
            HCFG=HDIR+sname+'.cfg'
            print "The name of the configuration file is "+HCFG
            cfch= raw_input("Press 1 to proceed with this name. Press any other key to choose a new name :")
            if (cfch != '1' or not cfch):
                cfname=raw_input("Enter the new name for configuration file :")
                HCFG = HDIR+cfname+'.cfg'
                print "The name of the configuration file is "+HCFG            
            aname=raw_input("Enter the name to be displayed  on the alerts: ")
            while True:
                sip=raw_input("Enter the IP address of the server: ")
                if is_ipv4(sip):
                    break
                else:
                    print 'Please enter a valid IP address'
    
    
    
            open(CCFG, 'w').close()
            with open(CCFG, 'a') as cfile:
                cfile.write("""
define contact{
        contact_name            <company>
        use                     generic-contact
        alias                   <company> admin
        service_notification_options w,u,c,r
        host_notification_options d,u,r
        email                  <client email>
        }

define contactgroup{
        contactgroup_name       <company/contactname>
        alias                   <company> admins
        members                 <contact_name mentioned above>,ssages
        }

                """)
            cfile.close()
            s1='<company>'
            s2='<client email>'
            s3='<company/contactname>'
            s4='<contact_name mentioned above>'
            s=open(CCFG).read()
            if s1 or s2 or s3 or s4 in s:
                s=s.replace(s1, cname)
                s=s.replace(s2, cmail)
                s=s.replace(s3, cname)
                s=s.replace(s4, cname)
                f=open(CCFG, 'w')
                f.write(s)
                f.flush()
                f.close()
        
        
            if os.path.isfile(HDIR):
                open(HCFG, 'w').close()
            else:
                os.makedirs(HDIR)
                open(HCFG, 'w').close()
                
            with open(HCFG, 'a') as hfile:
                hfile.write("""
define host{
        use        linux-server
        host_name   name_of_the_server
        alias       name_to_be_displayed_on_alerts
        address     yy.yy.yy.yy
        contact_groups  Client_Contact_group
        }
                """)
            hfile.close()
        
     
            h1='name_of_the_server'
            h2='name_to_be_displayed_on_alerts'
            h3='yy.yy.yy.yy'
            h4='Client_Contact_group'
        
            h=open(HCFG).read()
            if h1 or h2 or h3 or h4 in h:
                h=h.replace(h1, sname)
                h=h.replace(h2, aname)
                h=h.replace(h3, sip)
                h=h.replace(h4, cname)
                g=open(HCFG, 'w')
                g.write(h)
                g.flush()
                g.close()
        
        #Existing client        
        else:
            cname=get_cc(NCON)
            sname=raw_input("Enter the name of the server: ")
            HCFG=HDIR+sname+'.cfg'
            print "The name of the configuration file is "+HCFG
            cfch= raw_input("Press 1 to proceed with this name. Press any other key to choose a new name :")
            if (cfch != '1' or not cfch):
                cfname=raw_input("Enter the new name for configuration file :")
                HCFG = HDIR+cfname+'.cfg'
                print "The name of the configuration file is "+HCFG   
            aname=raw_input("Enter the name to be displayed  on the alerts: ")
            while True:
                sip=raw_input("Enter the IP address of the server: ")
                if is_ipv4(sip):
                    break
                else:
                    print 'Please enter a valid IP address'                
    

        
        #    if os.path.isfile(HDIR):
            open(HCFG, 'w').close()
            with open(HCFG, 'a') as hfile:
                hfile.write("""
define host{
        use        linux-server
        host_name   name_of_the_server
        alias       name_to_be_displayed_on_alerts
        address     yy.yy.yy.yy
        contact_groups  Client_Contact_group
        }
                """)
            hfile.close()
        
        
            h1='name_of_the_server'
            h2='name_to_be_displayed_on_alerts'
            h3='yy.yy.yy.yy'
            h4='Client_Contact_group'
        
            h=open(HCFG).read()
            if h1 or h2 or h3 or h4 in h:
                h=h.replace(h1, sname)
                h=h.replace(h2, aname)
                h=h.replace(h3, sip)
                h=h.replace(h4, cname)
                g=open(HCFG, 'w')
                g.write(h)
                g.flush()
                g.close()

                
    else:
        print 'Error in configuration file'
        #sip = server ip sname+hostname cname= contact_group HCFG=conf_file
    pword=raw_input("Enter the servers root password ")
    return (sip,sname,cname,HCFG,pword)
        
        
def NCONF(hostip, name_of_server, contact_group, conf_file, client_passwd):
    t1 = tempfile.NamedTemporaryFile(delete=False) #Create temporary file
    SCFILE=t1.name #Assign name of temp file to variable
    DCFILE=t1.name #Assign name of temp file to variable
    
    t2 = tempfile.NamedTemporaryFile(delete=False) #Create another file
    SFILE=t2.name
    DFILE=t2.name
    t3 = tempfile.NamedTemporaryFile(delete=False) #Create another file
    SBFILE=t3.name
    DBFILE=t3.name

    quote = """'"""        
    def server_template(service_description, check_command):
        service_des = "service_description\t" + service_description + "\n"
        check_comnd = "check_command\t\t" + check_command + "\n"
        seq = ["\ndefine service{\n", "\tuse\t\t\tfiveminutes\n", '\thost_name\t\t' + name_of_server + '\n\t', service_des, '\tcontact_groups\t\t' + contact_group + '\n\t', check_comnd,"\t}\n"]
        with open(conf_file, 'a') as f:
            f.writelines( seq )
        
    
    def query_yes_no(question, default="yes"):
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)
    
        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")    
    
    def check_template(check_name, command_name):
        display_1 = bcolors.DARKBLUE + '\nTesting ' + check_name + ' Check...\n' + bcolors.BROWN + 'Query Output:' + bcolors.ENDC
        print display_1,
        custom_check = ("MySQL","CPULoad")
        if check_name in custom_check:
            check_comm = 'check_command_' + check_name
            check_command = eval(check_comm)
        else:
            check_command = '/usr/local/nagios/libexec/' + command_name + ' -H 144.76.150.65' 
        print os.popen(check_command).read()
        check_qst = bcolors.BOLD + 'Add ' + check_name + ' check?' + bcolors.ENDC
        check_add = query_yes_no(check_qst)
        if check_add == True:
            if check_name == "DiskQuota":
                pass
            else:
                server_template(check_name ,command_name)
            if check_name == "CPULoad":
                cpu_warn = raw_input('Enter CPU warning range with comma seperation[1min,5min, 15min ]:\nExample: 1,2,3\n')
                cpu_crit = raw_input('Enter CPU warning range [1min,5min, 15min ]:\nExample: 4,5,6\n')
                load_comm = 'command[check_load_server]=/usr/local/nagios/libexec/check_load -w ' + cpu_warn + ' -c ' + cpu_crit
                open(SFILE, 'a').close()
                with open(SFILE, "a") as out_file:
                        cmd1 = str(load_comm) + '\n'
                        out_file.write(cmd1)
                        print(t2.name)
            
           
            if check_name == "DiskQuota":
                check_qstn = bcolors.BOLD + 'Add ' + check_name + ' check?' + bcolors.ENDC
                check_add_disk = query_yes_no(check_qstn)
                while check_add_disk == True:
                    disk_name = raw_input('Enter Hard drive name:\nExample: /dev/hda1\nEnter n to exit disk monitoring checks\n')
                    if disk_name == 'no':
                        pass
                    else:
                        disk_iden = disk_name.replace("/dev/","")
#                        print(disk_iden)
                        disk_warn = raw_input('Enter Load warning range:\nExample: 20%\n')
                        disk_crit = raw_input('Enter Load warning range:\nExample: 10%\n')
                        disk_commnd = 'command[check_disk_' + disk_iden + ']=/usr/local/nagios/libexec/check_disk -w ' + disk_warn + ' -c ' + disk_crit + ' -p ' + disk_name
#                        print(disk_commnd)
                        command_name_disk = 'nrpe!check_disk_' + disk_iden
                        
                        server_template(disk_iden, command_name_disk)
                        open(SFILE, 'a').close()
                        with open(SFILE, "a") as out_file:
                            cmd2 = str(disk_commnd) + '\n'
                            out_file.write(cmd2)
#Temp file                             print(t2.name)  
                            print bcolors.OKGREEN + '[Info]:' + bcolors.ENDC + 'Disk monitoring for ' + disk_name + ' configured'
                            disk_name = raw_input('Want to add more disks? [y/n]')
                            if disk_name == 'n':
                               check_add_disk = 'False' 
            print bcolors.OKGREEN + check_name + ' check added\n' + bcolors.ENDC
        else:
            print bcolors.OKGREEN + check_name + ' check not added\n' + bcolors.ENDC    
    
    def drawProgressBar(percent, barLen = 50):
        sys.stdout.write("\r")
        progress = ""
        for i in range(barLen):
            if i < int(barLen * percent):
                progress += "="
            else:
                progress += " "
        
        sys.stdout.write( bcolors.BOLD + "Basic service checks: [ %s ] %.2f%%" % (progress, percent * 100) + bcolors.ENDC )
        sys.stdout.flush()
     
    ##Script Starts here
       
    open(SCFILE, 'w').close()
    with open(SCFILE, 'a') as t:          # Write program to temporary file
        t.write("""
    import os
    def detectCPUs():
    
     """
     #Detects the number of CPUs on a system.
     """
     notfound = "Not a Linux Distro"
     # Linux, Unix and MacOS:
     if hasattr(os, "sysconf"):
         if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
             # Linux & Unix:
             ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
             if isinstance(ncpus, int) and ncpus > 0:
                 NumCPU = "Number of CPU = %s" % ncpus
                 return NumCPU
         else: 
             return notfound
     return notfound # Default
    
    
    print detectCPUs()
    out1 = os.system("df -h")
    print out1
    
        """)
        
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(port=22, hostname=hostip, username='root', password=client_passwd)
    sftp = client.open_sftp()
    sftp.put(SCFILE, DCFILE) # Copy temporary file to destination
    sftp.close
    
    
    stdin, stdout, stderr = client.exec_command('python '+DCFILE)
    
        
    for line in stdout.readlines(): # Return the remote output, use stderr for printing errors
        print line.strip('\n')
        
    client.exec_command('rm -f '+DCFILE)
    client.close()
#    os.remove(SCFILE)
    
    
    #####
    def nrpe_checks_write():
        fin = open(SFILE, "r")
        fin.close()
        open(SBFILE, 'w').close()
        print(t3.name)
        seq1 = ['\nconfig = open( ' + quote + DFILE + quote + ', "r")',  '\ndata2 = config.read()', '\nconfig.close()', '\nwith open(\'/usr/local/nagios/etc/nrpe.cfg\', \'a\') as f:', '\n\tf.write( data2 )', '\n\tf.close()', '\n',  'out = os.system("/etc/init.d/nrpe restart")\n', 'if out15:\n', '\tprint "NRPE restart error!"']        
        with open(SBFILE, 'a') as t:           # Write program to temporary file
            t.writelines( seq1 )
            
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(port=22, hostname=hostip, username='root', password=client_passwd)
        sftp = client.open_sftp()
        sftp.put(SBFILE, DBFILE) # Copy temporary file to destination
        sftp.put(SFILE, DFILE)
        sftp.close
    
        stdin, stdout, stderr = client.exec_command('python '+DBFILE)
    
        
        for line in stdout.readlines(): # Return the remote output, use stderr for printing errors
            print line.strip('\n')
        
        client.exec_command('rm -f '+DCFILE)
        client.close()
        os.remove(SBFILE)
    
    #########################################
    ##Checks to be added
    #########################################
    
    print bcolors.OKBLUE + 'Checking common services... Add the service checks required with y or [Enter] key' + bcolors.ENDC
    ##CPU Load Check
    check_template('DiskQuota', 'check_disk')
    drawProgressBar(.1)
    ##Check CPU Load
    check_template('CPULoad', 'check_nrpe!check_load')
    drawProgressBar(.2)
    ##HTTP
    check_template('HTTP', 'check_http')
    drawProgressBar(.3)
    ##MySQL
    check_template('MySQL', 'check_mysql')
    drawProgressBar(.4)
    ##IMAP
    check_template('IMAP', 'check_imap')
    drawProgressBar(.5)
    ##SMTP
    check_template('SMTP', 'check_smtp')
    drawProgressBar(.6)
    ##POP
    check_template('POP', 'check_pop')
    drawProgressBar(.7)
    ##DNS
    check_template('DNS', 'check_dns')
    drawProgressBar(.8)
    ##FTP
    check_template('FTP', 'check_ftp')
    drawProgressBar(.9)
    ##Ping
    check_template('Ping', 'check_ping!100.0,50%!500.0,90%')
    print bcolors.OKBLUE + 'Basic Checks complete' + bcolors.ENDC
    ##Write changes to nrpe.con(client)
    print '\nSaving all changes to configuration files' + bcolors.OKGREEN + '\t \t[Done]' + bcolors.ENDC
    nrpe_checks_write()
    #nrpe_checks_write()
    print '\nVerifying configuration file....' + bcolors.OKGREEN + '\t \t\t[Done]' + bcolors.ENDC
        

hostip, name_of_server, contact_group, conf_file, client_passwd = HCONF()
    ##Check Paths
check_command_MySQL = '/usr/local/nagios/libexec/check_tcp ' + hostip + ' -p 3306'
check_command_CPULoad = '/usr/local/nagios/libexec/check_nrpe -H ' + hostip + ' -c check_load'
    ##############
CCONF(hostip, client_passwd)
NCONF(hostip, name_of_server, contact_group, conf_file, client_passwd)
print bcolors.OKGREEN + "\n\n----------Summary----------\n" + bcolors.ENDC
print 'Configuration file = ' + conf_file 
print 'Checks Added -->'
with open(conf_file) as origin:
    for line in origin:
        if not "service_description" in line:
           continue
        try:
            print line.split('\t')[2]
        except IndexError:
            print
