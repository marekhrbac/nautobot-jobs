from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import Prefix
import requests
import os


class AzurePipeline(Job):
    
    def run(self):
        url = "https://gitlab.msync.cz/api/v4/projects/3/trigger/pipeline"  
        payload = {
            "token": os.getenv("GITLAB_TRIGGER_TOKEN"),
            "ref": "main"
        }
        response = requests.post(url, data=payload)
        
        is_vnet_prefixes = Prefix.objects.filter( _custom_field_data__is_vnet=True)
        for prefix in is_vnet_prefixes:
            vnet = prefix.custom_fields.get("vnet")
            if not vnet:
                self.logger.warning(f"Prefix {prefix} is marked as VNet but has no 'VNET NAME' custom field value.")
                return
            
        if response.ok:
            self.logger.info("Pipeline triggered successfully")
        else:
            self.logger.error(f"Failed: {response.status_code} {response.text}")

register_jobs(AzurePipeline)