from nautobot.apps.jobs import Job, register_jobs
from nautobot.apps.jobs import JobButtonReceiver
import requests
import os

name = "Import VNET to Azure"

class AzurePipeline(JobButtonReceiver):
    
    class Meta:
        name = "Import VNET to Azure"
        
    def run(self,obj):
        url = "https://gitlab.msync.cz/api/v4/projects/3/trigger/pipeline"  
        payload = {
            "token": os.getenv("GITLAB_TRIGGER_TOKEN"),
            "ref": "main"
        }
        self.logger.debug("Running Azure Pipeline Job.")
        response = requests.post(url, data=payload)
        
        self.logger.debug(response.text)


register_jobs(AzurePipeline)