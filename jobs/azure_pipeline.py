from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import Prefix
import requests
import os
import time
from django.utils.html import escape


class AzurePipeline(Job):
    
    def run(self):
        is_vnet_prefixes = Prefix.objects.filter( _custom_field_data__is_vnet=True)
        for prefix in is_vnet_prefixes:
            vnet_name = prefix.custom_field_data.get("vnet")
            if not vnet_name:
                self.logger.warning(f"Prefix {prefix} is marked as VNet but has no 'VNET NAME' custom field value.")
                return
            rg = prefix.custom_field_data.get("resource_group")
            if not rg:
                self.logger.warning(f"Prefix {prefix} is marked as VNet but has no 'RESOURCE GROUP' custom field value.")
                return
        
        url = "https://gitlab.msync.cz/api/v4/projects/3/trigger/pipeline"  
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

        url = f"https://gitlab.msync.cz/api/v4/projects/3/pipelines/{pipeline_id}/jobs"  
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


        url = f"https://gitlab.msync.cz/api/v4/projects/3/jobs/{pipeline_job_id}/artifacts/tfplan.txt"  
        header = {
            "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
        }
        response = requests.get(url, headers=header)  
        self.logger.info(f"Pipeline #{pipeline_id} job output:")
        self.logger.info(f'<span style="font-family: monospace;">{response.text}</span>')

   
            
register_jobs(AzurePipeline)