from nautobot.apps.jobs import Job, register_jobs
import requests
import os


class AzurePipeline(Job):
    
    def run(self):
        url = "https://gitlab.msync.cz/api/v4/projects/3/trigger/pipeline"  
        payload = {
            "token": os.getenv("GITLAB_TRIGGER_TOKEN"),
            "ref": "main"
        }
        self.logger.debug("Running Azure Pipeline Job.")
        response = requests.post(url, data=payload)
        
        self.logger.debug(response.text)


register_jobs(AzurePipeline)