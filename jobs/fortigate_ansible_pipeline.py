from nautobot.apps.jobs import Job, register_jobs
import requests
import os
import time
from django.utils.html import escape


class AzurePipeline(Job):
    
    def run(self):
        url = "https://gitlab.msync.cz/api/v4/projects/4/trigger/pipeline"  
        payload = {
            "token": os.getenv("GITLAB_TRIGGER_TOKEN"),
            "ref": "main"
        }
        response = requests.post(url, data=payload)

        if response.ok:
            self.logger.info("Pipeline triggered successfully")
        else:
            self.logger.error(f"Failed: {response.status_code} {response.text}")

        pipeline_id = response.json()["id"]

        url = f"https://gitlab.msync.cz/api/v4/projects/4/pipelines/{pipeline_id}/jobs"  
        header = {
            "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
        }
        response = requests.get(url, headers=header)     
        pipeline_status = response.json()[0]["status"]

        while pipeline_status not in ["success"]:
            self.logger.info(f"Pipeline #{pipeline_id} status: {pipeline_status}. Waiting for completion...")
            time.sleep(10) 
            response = requests.get(url, headers=header)     
            pipeline_status = response.json()[0]["status"]
            pipeline_job_id = response.json()[0]["id"]
        self.logger.info(f"Pipeline #{pipeline_id} status: {pipeline_status}")


        url = f"https://gitlab.msync.cz/api/v4/projects/4/jobs/{pipeline_job_id}/artifacts/tfplan.txt"  
        header = {
            "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
        }
        response = requests.get(url, headers=header)  
        self.logger.info(f"Pipeline #{pipeline_id} job output:")
        self.logger.info(f"```Ansible\n{(response.text)}\n```")

   

register_jobs(AzurePipeline)