from nautobot.apps.jobs import Job, register_jobs
import requests
import os
import time
from django.utils.html import escape


class FortigateAnsiblePipeline(Job):
    
    def run(self):
        url = "https://gitlab.msync.cz/api/v4/projects/4/trigger/pipeline"  
        payload = {
            "token": os.getenv("GITLAB_TRIGGER_TOKEN_ANSIBLE"),
            "ref": "main"
        }
        response = requests.post(url, data=payload)

        if response.ok:
            self.logger.info("Pipeline triggered successfully")
        else:
            self.logger.error(f"Failed: {response.status_code} {response.text}")

        pipeline_id = response.json()["id"]

        url = f"https://gitlab.msync.cz/api/v4/projects/4/pipelines/{pipeline_id}"  
        header = {
            "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
        }
        response = requests.get(url, headers=header)     
        pipeline_status = response.json()["status"]

        while pipeline_status not in ["success", "failed", "canceled", "skipped", "manual"]:
            self.logger.info(f"Pipeline #{pipeline_id} status: {pipeline_status}. Waiting for completion...")
            time.sleep(10) 
            response = requests.get(url, headers=header)     
            pipeline_status = response.json()["status"]
        self.logger.info(f"Pipeline #{pipeline_id} status: {pipeline_status}")

        url = f"https://gitlab.msync.cz/api/v4/projects/4/pipelines/{pipeline_id}/jobs"
        response = requests.get(url, headers=header)
        
        for job in reversed(response.json()):
            if job["status"] == "skipped":
                continue
            trace = requests.get(
                f"https://gitlab.msync.cz/api/v4/projects/4/jobs/{job['id']}/trace",
                headers=header,
            )
            self.logger.info(f"Job {job['name']}: {job['status']}\n```\n{trace.text[-5000:]}\n```")

        if pipeline_status != "success":
            raise RuntimeError(f"Pipeline #{pipeline_id} status: {pipeline_status}")
   

register_jobs(FortigateAnsiblePipeline)