import logging
import smtplib
import textwrap
from datetime import date
from email.headerregistry import Address
from email.message import EmailMessage

import prettytable
import requests

WRAPPER = textwrap.TextWrapper(width=120)
REQUEST_FMT = "https://api.github.com/repos/{0}/actions/workflows/{1}/runs"

def generate_ci_report(config):
    data = []
    overall_status = "Success"
    
    for repo in config.ci_repos:
        repo_name = repo['name'] if isinstance(repo, dict) else repo
        workflow = "tests.yml"
        resp = requests.get(
            REQUEST_FMT.format(repo_name, workflow),
            params={"event": "schedule", "branch": "main"},
            timeout=1000,
        )
        
        if resp.status_code != 200:
            logging.error(f"Failed to fetch CI data for {repo_name}: {resp.status_code}")
            logging.error(f"Response content: {resp.content}")
            continue
        
        resp_json = resp.json()
        if not resp_json["workflow_runs"]:
            continue
        
        latest_run = resp_json["workflow_runs"][0]
        status = latest_run["conclusion"]
        if status != "success":
            overall_status = "Failure"
        
        temp = {"repo": repo_name, "status": status, "url": latest_run["html_url"]}
        logging.info(f"CI data fetched for {repo_name}: {status}")
        data.append(temp)
        
    return {
        "data": data,
        "overall_status": overall_status,
        "date": date.today().isoformat(),
    }
