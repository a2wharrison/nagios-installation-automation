# nagios-installation-automation
SupportSages which provides 24/7 server monitoring uses this script to automate nagios installation on RPM based client servers

This script is to ease the task of adding servers to Nagios Monitor. Instead of manually compiling and installing nrpe and configuring it in the Nagios Monitor server, this script helps do that for you.

This script is tested on Nagios Server 3.4.4 and Client running cPanel server (Centos 6). This assumes that the following are the configuration directories:

Contact directory path: /usr/local/nagios/etc/objects/contacts

Client directory path: /usr/local/nagios/etc/objects/clients

If the directories are different, edit the script with the correct path

This script is to be placed and executed from Nagios Monitor server. Make the following changes before executing the script [only once, setting configuration with reference to environment]:

line55: purl = "http://198.50.243.114/nagios-plugins-1.4.16.tar.gz" --Change URL with nagios plugins URL

line56: nurl = "http://198.50.243.114/nrpe-2.13.tar.gz" --Change URL with NRPE download URL

line168: addIP = ',aa.bb.cc.dd\n' --Replace with Nagios Server Public IP

Before executing the script whitelist bothe server IPs in each other depending on the firewall configuration.

After that execute the script with root privilages
python nagios_configure.py

Enter the client server root logins and the client name / configurations in the interactive prompt which follows and the status of the installation will be shown as output.

How To Use
-----------

run the file by using the command 
python <filename>.py

A prompt to enter the email account will appear as follows 
Enter Email Account:

A confirmation prompt will appear with the account detail and email address along with a new password prompt
Account: example 
Domain: example.com 
Enter new Email Password:

Enter the new password in the prompt.

A success message will be printed in case of a successful password change.


Sample output
-------------

Enter Email Account:example@example.com
EmailAccount: example@example.com 
Account: example 
Domain: example.com 
Enter new Email Password:redred
"-------------------------------------------------------------------
Password changed successfully to redred


