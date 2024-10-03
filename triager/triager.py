import logging
from datetime import datetime

import requests
from requests.exceptions import RequestException

REQUEST_FMT = "https://api.github.com/repos/{0}/{1}/issues"


def triage(config, repos):
    issues = {}
    headers = config.token
    if headers:
        logging.info("Using authentication token for request")
    else:
        logging.warning(
            "No authentication token provided. "
            "Proceeding without authentication token",
        )

    for org, repo_name in repos:
        params = dict(since=config.last_triage_date.isoformat(), assignee="none")
        issues[repo_name] = []

        logging.info(f"Requesting issue details for {org}/{repo_name}")
        logging.debug(f"Request params: {params}")

        try:
            resp = requests.get(
                REQUEST_FMT.format(org, repo_name),
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            logging.debug(f"Response status code: {resp.status_code}")
            logging.debug(f"Response content: {resp.text[:500]}...")
        except RequestException as e:
            logging.error(f"Error fetching issues for {org}/{repo_name}: {str(e)}")
            if isinstance(e, requests.exceptions.HTTPError):
                logging.error(f"HTTP Status Code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.content}")
                if e.response.status_code == 403:
                    logging.error(
                        "This might be due to rate limiting or authentication "
                        "issues. Check your GitHub token.",
                    )
                elif e.response.status_code == 404:
                    logging.error(
                        "Repository not found. Check if the repository exists "
                        "and you have access to it.",
                    )
            continue

        try:
            items = resp.json()
            logging.debug(f"Number of items retrieved: {len(items)}")
        except ValueError:
            logging.error(f"Failed to parse JSON response for {org}/{repo_name}")
            continue

        for item in items:
            created_at = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if created_at >= config.last_triage_date:
                issues[repo_name].append(
                    {
                        "url": item["html_url"],
                        "title": item["title"],
                        "type": "Pull Request" if item.get("pull_request") else "Issue",
                    },
                )

        logging.info(
            f"Found {len(issues[repo_name])} new issues/PRs for {org}/{repo_name}",
        )

    if not any(issues.values()):
        logging.warning("No new issues found across all repositories.")
    else:
        logging.info("Triage completed successfully")

    return issues
