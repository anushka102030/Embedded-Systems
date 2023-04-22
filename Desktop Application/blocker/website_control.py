#Import libraries
import ctypes, sys

#The callable functions that overwrite the system hosts file and implement blocking of sites. 

#---------------------IMPORTANT VARIABLES--------------------------------------------------

#Windows host file path (it is just etc\hosts in Linux/MacOS)
HOSTPATH=r"C:\Windows\System32\drivers\etc\hosts"

#---------------------------------------------------------------------------------------------

#Call function to block sites - writes over hosts file.
#Parameter: List of sites (url strings) to block
#Return: 0 for success
#        1 for exception
def block_write(websites=[]):
    redirect="127.0.0.1"

    try:
       #Writing to the hosts file
       with open(HOSTPATH,'r+') as file:
          #Read data from file
          content = file.read()
          for site in websites:
             if site in content:
                pass
             else:
                file.write(redirect+" "+site+"\n")
       return 0

    #Catch any exception
    except Exception as e:
        print("Exception writing to hosts file (website blocking): " + str(e))
        return 1


#Rewrites hosts file when called to unblock sites.
#Parameter: list of sites (url strings) to unblock.
#return: 0 for success
#        1 for exception
def unblock_write(websites=[]):

    try:
        #Writing to the hosts file
        with open(HOSTPATH,'r+') as file:
            # read content from file
            content = file.readlines()
            #We will write from the start of the file
            file.seek(0)
            #Iterate over contents of host file.
            for line in content:
                #If line in hosts file does not contain the sites we need to unblock
                #we can write it to the host file.
                if not any(site in line for site in websites):
                    file.write(line)
                    #Once we've written everything we need, get rid of any extra characters
                    #left from overwriting file.
                    file.truncate()
        return 0

    #Catch any exception
    except Exception as e:
         print("Exception writing to hosts file (website unblocking): " + str(e))
         return 1
