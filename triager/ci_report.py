import logging
import textwrap
from datetime import date

import requests

WRAPPER = textwrap.TextWrapper(width=120)
REQUEST_FMT = "https://api.github.com/repos/{0}/actions/workflows/{1}/runs"


def generate_ci_report(config):
    data = []
    overall_status = "Success"
    workflow = config.workflow_name

    for repo in config.ci_repos:
        repo_name = repo["name"] if isinstance(repo, dict) else repo
        try:
            resp = requests.get(
                REQUEST_FMT.format(repo_name, workflow),
                params={"event": "schedule", "branch": "main"},
                headers=config.token,
                timeout=1000,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch CI data for {repo_name}: {str(e)}")
            if resp.status_code == 403:
                logging.error("API rate limiting or authentication issues.")
            logging.debug(f"Response content: {resp.content}")
            continue

        resp_json = resp.json()
        if not resp_json["workflow_runs"]:
            logging.warning(f"No workflow runs found for {repo_name}")
            continue

        latest_run = resp_json["workflow_runs"][0]
        status = latest_run["conclusion"]

        if status is None:
            logging.info(f"Workflow for {repo_name} is still in progress")
            continue

        if status != "success":
            overall_status = "Failure"

        temp = {
            "repo": repo_name,
            "status": status,
            "url": latest_run["html_url"],
        }
        logging.info(f"CI data fetched for {repo_name}: {status}")
        data.append(temp)

    return {
        "data": data,
        "overall_status": overall_status,
        "date": date.today().isoformat(),
    }
