import requests
import os
from pprint import pprint
import time



url = "https://gitlab.msync.cz/api/v4/projects/3/trigger/pipeline"  
payload = {
    "token": os.getenv("GITLAB_TRIGGER_TOKEN"),
    "ref": "main"
}
    
response = requests.post(url, data=payload)
pipeline_id = response.json()["id"]

url = f"https://gitlab.msync.cz/api/v4/projects/3/pipelines/{pipeline_id}/jobs"  
header = {
    "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
}
response = requests.get(url, headers=header)     
pipeline_status = response.json()[0]["status"]

while pipeline_status not in ["success"]:
    print(f"Pipeline #{pipeline_id} status: {pipeline_status}. Waiting for completion...")
    time.sleep(10) 
    response = requests.get(url, headers=header)     
    pipeline_status = response.json()[0]["status"]
    pipeline_job_id = response.json()[0]["id"]
print(f"Pipeline #{pipeline_id} status: {pipeline_status}")


url = f"https://gitlab.msync.cz/api/v4/projects/3/jobs/{pipeline_job_id}/artifacts/tfplan.txt"  
header = {
    "Authorization": f"Bearer {os.getenv('GITLAB_BEARER_TOKEN')}"
}
response = requests.get(url, headers=header)  
print(f"Pipeline #{pipeline_id} job output:")
print(response.text) 


