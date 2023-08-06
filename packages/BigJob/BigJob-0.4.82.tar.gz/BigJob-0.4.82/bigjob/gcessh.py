#!/usr/bin/env python

from bigjob import logger
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
import httplib2
import os
import uuid
import time

import bliss.saga as saga

"""
AN OAUTH2 Client Id must be created at the Google API console at:

https://code.google.com/apis/console/

=> API Access

More information with respect to OAUTH: https://developers.google.com/compute/docs/api/how-tos/authorization
"""
OAUTH2_CLIENT_ID='1004462711324-55akehip32m59u6omdfrt9s8u8ehb0hm.apps.googleusercontent.com'
OAUTH2_CLIENT_SECRET='EIMML1W7anu0XijVghws0DY-'


GCE_PROJECT_ID='bigjob-pilot'

class gce_states:
    PROVISIONING="PROVISIONING"
    STAGING="STAGING"
    RUNNING="RUNNING"
    
    
class gcessh:
    """ Plugin for Google Compute Engine """

    def __init__(self, bootstrap_script=None):
        """Constructor"""
        self.bootstrap_script =  bootstrap_script
        self.id="bigjob-" + str(uuid.uuid1())
        self.network_ip=None
        
        # Do OAUTH authentication
        storage = Storage('gce.dat')
        self.credentials = storage.get()
        if self.credentials is None or self.credentials.invalid == True:
            flow = OAuth2WebServerFlow(
                                       client_id=OAUTH2_CLIENT_ID,
                                       client_secret=OAUTH2_CLIENT_SECRET,
                                       scope='https://www.googleapis.com/auth/compute',
                                       user_agent='bigjob-client/1.0')

            self.credentials = run(flow, storage)
        

    def run(self):
        request_dict = {
          "kind": "compute#instance",
          "disks": [],
          "networkInterfaces": [
            {
              "kind": "compute#instanceNetworkInterface",
              "accessConfigs": [
                {
                  "name": "External NAT",
                  "type": "ONE_TO_ONE_NAT"
                }
              ],
              "network": "https://www.googleapis.com/compute/v1beta12/projects/bigjob-pilot/networks/default"
            }
          ],         
          "zone": "https://www.googleapis.com/compute/v1beta12/projects/bigjob-pilot/zones/us-central1-a",
          "machineType": "https://www.googleapis.com/compute/v1beta12/projects/bigjob-pilot/machine-types/n1-standard-1",
          "name": self.id
        }
        
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        gce = build("compute", "v1beta12", http=http)
        #result = gce.instances().get(instance="bigjob-pilot", project="bigjob-pilot").execute()
        gce.instances().insert(project=GCE_PROJECT_ID, body=request_dict).execute()
        
        #wait for compute instance to become active
        self.wait()
        
        # spawn BJ agent via SSH
        compute_instance_details = self.__get_instance_resource()
        logger.debug("Compute Instance Details: " + str(compute_instance_details))
        self.network_ip = compute_instance_details["networkInterfaces"][0]["accessConfigs"][0]['natIP']
        
        js = saga.job.Service(os.path.join("ssh://". self.network_ip))
        

    def wait(self):
        while self.get_state()!=gce_states.RUNNING:
            time.sleep(5)
        
    
    def get_state(self):
        result=self.__get_instance_resource()
        return result["status"]
    
    
    def cancel(self):
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        gce = build("compute", "v1beta12", http=http)
        gce.instances().delete(project=GCE_PROJECT_ID, instance=self.id).execute()
        
    
    def __get_instance_resource(self):
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        gce = build("compute", "v1beta12", http=http)
        result = gce.instances().get(project=GCE_PROJECT_ID, instance=self.id).execute()
        return result
 
 
     
if __name__ == "__main__":
    gce = gcessh()
    gce.run()
    print gce.get_state()
