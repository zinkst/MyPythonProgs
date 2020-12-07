#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import glob
import sys
import re
import string
import logging
import json



description = """This program creates zone files for bind reverse lookup zone files
you need to specify the parameters in a json file like this:
{
    "dns_hostname": "cil150-003", 
    "domain": "cil150.dev", 
    "hostnameDelimiter": "-", 
    "hostnamePrefix": "cil", 
    "subnet": "172.16", 
    "subnetNumbers": [
        150
    ], 
    "subnetReverse": "16.172",
    "outFilePath" : "/links/persdata/Stefan/myPrg/MyPythonPrgs/GenerateBindZoneFile/"
}
    
"""

############################################################################
def initLogger():
    try: 
        rootLogger = logging.getLogger()
        logging.config.fileConfig("pyLoggerConfig.cfg")
    except:    
        logHandler = logging.StreamHandler(sys.stdout)
        #logging.basicConfig(stream=logHandler)
        rootLogger.addHandler(logHandler)
        rootLogger.setLevel(logging.DEBUG)
        rootLogger.setLevel(logging.INFO)
    return rootLogger

############################################################################

def writeZoneReverseFile(netConfig,subnetNumber,outFilePath):
    logging.info('########################################### writeZoneReverseFile #####################')
    outFileName = os.path.join(outFilePath, "rev." + str(subnetNumber) + "."+netConfig["subnetReverse"]+".in-addr.arpa")
    with open(outFileName, 'wb') as outfile:
        outfile.write( "@     IN      SOA    " + netConfig["dns_hostname"] + "." + netConfig["domain"] +". postmaster." + netConfig["domain"] + " (\n")     
        outfile.write("""                        2006081401;
                        8H;
                        4H;
                        4W;
                        1D;
)
""")
        outfile.write('\n')
        outfile.write("    IN  NS  " + netConfig["dns_hostname"] + "." + netConfig["domain"] +".\n") 
        for counter in range(0, 256):
            outLine = '{:<3}'.format(counter) + " IN PTR " + netConfig["hostnamePrefix"] + str(subnetNumber).zfill(3) + netConfig["hostnameDelimiter"] + str(counter).zfill(3) + "."+netConfig["domain"]+"."
            logging.info( outLine)
            outfile.write(outLine + '\n')
    
############################################################################

def writeNamedFile(netConfig,outFilePath,):
    logging.info('########################################### writeNamedFile #####################')
    outFileName = os.path.join(outFilePath, "named.conf")
    with open(outFileName, 'wb') as outfile:
        logging.info('--------------------- write zone entry')
        outLine = 'zone "'+netConfig["domain"]+'" IN {'
        logging.info( outLine)
        outfile.write(outLine + '\n')
        outLine='     type master;'
        logging.info( outLine)
        outfile.write(outLine + '\n')
        outLine='     file "/etc/named/'+netConfig["domain"]+'.db";'
        logging.info( outLine)
        outfile.write(outLine + '\n')
        outLine='};'
        logging.info( outLine)
        outfile.write(outLine + '\n')
        outfile.write('\n')
        logging.info('---------------- write reverse zone entries ')
        for counter in netConfig["subnetNumbers"]:
            outLine = 'zone "'+str(counter)+'.'+netConfig["subnetReverse"]+'.in-addr.arpa" {'
            logging.info( outLine)
            outfile.write(outLine + '\n')
            outLine='     type master;'
            logging.info( outLine)
            outfile.write(outLine + '\n')
            outLine='     file "/etc/named/rev.'+str(counter)+'.'+netConfig["subnetReverse"]+'.in-addr.arpa";'
            logging.info( outLine)
            outfile.write(outLine + '\n')
            outLine='};'
            logging.info( outLine)
            outfile.write(outLine + '\n')
            outfile.write('\n')
   
############################################################################

def writeZoneFile(netConfig, outFilePath):
    logging.info('########################################### writeZoneFile #####################')
    outFileName = os.path.join(outFilePath, netConfig["domain"]+".db")
    with open(outFileName, 'wb') as outfile:
        outfile.write("""$ORIGIN .
$TTL 86400""")
        outfile.write('\n')
        outfile.write(netConfig['domain'] + ".     IN      SOA    " + netConfig["dns_hostname"] + "." + netConfig["domain"] +". postmaster." + netConfig["domain"] + " (\n")     
        outfile.write("""                        2006081401;
                        8H;
                        4H;
                        4W;
                        1D;
)
""")
        outfile.write('\n')
        outfile.write(netConfig["domain"] + "       IN         NS        "+ netConfig["dns_hostname"] + "." + netConfig["domain"] +".\n")
        outfile.write(netConfig["domain"] + "       IN         MX 10        postmaster." + netConfig["domain"] +".")
        outfile.write('\n')
        outfile.write('$ORIGIN '+ netConfig["domain"] + ".\n")
        
        for subnetNumber in netConfig["subnetNumbers"]:
            for counter in range(0, 256):
                outLine = netConfig["hostnamePrefix"]+str(subnetNumber).zfill(3)+netConfig["hostnameDelimiter"]+str(counter).zfill(3) + " IN A " + netConfig["subnet"] +"."+ str(subnetNumber) +"."+ str(counter)
                logging.info( outLine)
                outfile.write(outLine + '\n')

############################################################################

def processNetConfig(netConfig, outFilePath, ):
    for i in netConfig["subnetNumbers"]:
        writeZoneReverseFile(netConfig, i, outFilePath)
    writeZoneFile(netConfig, outFilePath)
    writeNamedFile(netConfig, outFilePath)


############################################################################
# main starts here
rootLogger = initLogger()

if len(sys.argv) != 2  :
    print description
    print sys.argv[0] + " <configFile>"  
else:
    configFile = sys.argv[1]
    with open(configFile, 'rb') as cfgfile:
        netConfig = json.load(cfgfile)

    processNetConfig(netConfig, netConfig["outFilePath"])





##################################################################        

def oldCreateConfig():
    netConfigBB = {}
    netConfigBB["domain"] = "ha3214.dev"
    netConfigBB["subnetReverse"] = "102.10"
    netConfigBB["subnet"] = "10.102"
    netConfigBB["hostnamePrefix"] = "t"
    netConfigBB["dns_hostname"] = "t100-004"
    netConfigBB["subnetNumbers"] = range(0, 256)
    netConfigBB["hostnameDelimiter"] = '-'
    netConfigCil = {}
    netConfigCil["domain"] = "cil150.dev"
    netConfigCil["subnetReverse"] = "16.172"
    netConfigCil["subnet"] = "172.16"
    netConfigCil["hostnamePrefix"] = "cil"
    netConfigCil["dns_hostname"] = "cil150-003"
    netConfigCil["subnetNumbers"] = range(150, 151)
    netConfigCil["hostnameDelimiter"] = '-'
    netConfigTSlCil = {}
    netConfigTSlCil["domain"] = "cil021029.ibm.com"
    netConfigTSlCil["subnetReverse"] = "21.172"
    netConfigTSlCil["subnet"] = "172.21"
    netConfigTSlCil["hostnamePrefix"] = "cil021"
    netConfigTSlCil["dns_hostname"] = "cil021029005"
    netConfigTSlCil["subnetNumbers"] = range(29, 30)
    netConfigTSlCil["hostnameDelimiter"] = ''
    outFilePath = sys.argv[1]
    with open(os.path.join(outFilePath, "netConfigBB.json"), 'wb') as outfile:
        json.dump(netConfigBB, outfile, indent=4, sort_keys=True) #json.dump(netConfigBB, outfile)
    with open(os.path.join(outFilePath, "netConfigCil.json"), 'wb') as outfile:
        json.dump(netConfigCil, outfile, indent=4, sort_keys=True)
    with open(os.path.join(outFilePath, "netConfigTSlCil.json"), 'wb') as outfile:
        json.dump(netConfigTSlCil, outfile, indent=4, sort_keys=True)
    
    

