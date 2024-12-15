import re
import os
import logging
import sys
import subprocess
import pprint
import stat

logging.basicConfig(stream=sys.stdout,level='DEBUG')
logger = logging.getLogger('testSnippets.py')

pattern = "hallo"
testString = "Hallo Stefan"
match = re.search(pattern,testString,re.IGNORECASE)
if match != None:
   match.group(0)
else:
  print "not found"

def testGrep():
    ipv6Enabled=False 
    sysconfig_network_file=os.path.join(os.path.sep,'etc','sysconfig','network')
    with open(sysconfig_network_file) as inFile:
        fileContent=inFile.read()
        if fileContent.find('NETWORKING_IPV6=yes') != -1:
            ipv6Enabled=True
    logger.debug('ipv6Enabled = %s' % (ipv6Enabled))

def testFirewall():
    KS_PORT='VAL_KS_PORT'
    KS_SERVER='VAL_KS_SERVER'
    SMASH_HTTP_PORT='VAL_SMASH_HTTP_PORT'
    SMASH_HTTPS_PORT='VAL_SMASH_HTTPS_PORT'
    logger.debug("configuring firewall.sh on Linux")
    fw_parms=['firewall.sh','open','-dest',KS_SERVER,'-dport',KS_PORT]
    logger.debug("calling firewall.sh with parameters: " + pprint.pformat(fw_parms))
    subprocess.call(fw_parms)
    fw_parms=['firewall.sh','open','tcpin','-dport',SMASH_HTTP_PORT]
    logger.debug("calling firewall.sh with parameters: " + pprint.pformat(fw_parms))
    subprocess.call(fw_parms)
    fw_parms=['firewall.sh','open','tcpin','-dport',SMASH_HTTPS_PORT]
    logger.debug("calling firewall.sh with parameters: " + pprint.pformat(fw_parms))
    subprocess.call(fw_parms)
    filename=os.path.join(os.path.sep,'home','zinks','bin','firewall_sh.log')
    curMode = os.stat(filename).st_mode
    os.chmod(filename,curMode | stat.S_IXUSR )

def testCutUrls():
    # cut last / from KERNEL_SERVICE_URL
    cfg={'KERNELSERVICE_URL' :"https://9.152.137.44:9443/myurl/", 'DEPLOYMENT_URL':'https://9.152.137.44:9444/storehouse/user/deployments/d-2aa9d69d-f49d-4372-8c92-06a1c548d193'
    }
    if cfg['KERNELSERVICE_URL'].endswith('/'):
        (KS_URL,rest)=cfg['KERNELSERVICE_URL'].rsplit('/',1)
    else:
        KS_URL=cfg['KERNELSERVICE_URL']
    (first,DEP_ID)=cfg['DEPLOYMENT_URL'].rsplit('/',1)
    logger.debug('DEP_ID=%s | KS_URL=%s' % (DEP_ID,KS_URL))   

def testCreateCommandLine():
    i=100
    while i<170:
        CMD="'[-uid u"+str(i)+" -password pw4u"+str(i)+" -confirmPassword pw4u"+str(i)+" -cn user -sn u"+str(i)+" -mail u"+str(i)+"@example.com]' "
        print CMD
        i=i+1
        #AdminTask.createUser ('[-uid u100 -password pw4u100 -confirmPassword pw4u100 -cn user -sn u100 -mail u100@example.com]')

### main starts here
#testGrep()
#testFirewall()
#testCutUrls()
testCreateCommandLine()
     