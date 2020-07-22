import logging
from datetime import datetime

import requests

REQUEST_FMT = "https://api.github.com/repos/{0}/{1}/issues"


def triage(config):
    issues = {}
    for org, repo in config.repos:
        repo_name = repo["name"]
        repo_labels = repo.get("labels", [])

        params = dict(since=config.last_triage_date.isoformat())
        if repo_labels:
            params["labels"] = ",".join(repo_labels)
        else:
            params["assignee"] = "none"

        issues[repo_name] = []

        logging.info(
            "requesting issue details for {0}/{1}".format(org, repo_name)
        )
        resp = requests.get(
            REQUEST_FMT.format(org, repo_name),
            params=params,
            headers=config.token,
        )

        if not resp.ok:
            logging.critical(resp.json()["message"])
            return {}

        for item in resp.json():
            created_at = datetime.strptime(
                item["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
            if created_at >= config.last_triage_date:
                issues[repo_name].append(
                    {
                        "url": item["html_url"],
                        "title": item["title"],
                        "type": "Pull Request"
                        if item.get("pull_request")
                        else "Issue",
                    }
                )

    logging.info("triage successfully completed")
    return issues
