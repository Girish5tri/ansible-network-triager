import logging
import os
import sys
from datetime import datetime, timedelta
from email.headerregistry import Address

import yaml


class Config:
    def __init__(self, cfg):
        # select config.yaml from cwd
        if not cfg:
            logging.info("config file not specified, setting default")
            cfg = "./config.yaml"

        logging.info(f"attempting to read config file: {cfg}")

        try:
            with open(cfg, "r") as config_file:
                config = yaml.safe_load(config_file)
            logging.info("config file successfully loaded")
        except FileNotFoundError as e:
            logging.critical(e)
            sys.exit()

        logging.info("parsing information from config file")
        self.organization_name = config.get("organization_name", "Generic Organization")
        self.workflow_name = config.get("workflow_name", "tests.yml")

        # Populate org and repos to triage
        self.bug_repos = []
        self.ci_repos = []
        logging.debug("parsing orgs and repositories from config file")
        for org in config.get("orgs", []):
            org_name = org["name"]
            for repo in org.get("ci_and_bug_repos", []):
                repo_name = repo["name"] if isinstance(repo, dict) else repo
                self.bug_repos.append((org_name, repo_name))
                self.ci_repos.append(f"{org_name}/{repo_name}")
            for repo in org.get("bug_specific_repos", []):
                repo_name = repo["name"] if isinstance(repo, dict) else repo
                self.bug_repos.append((org_name, repo_name))

        # Populate maintainers list
        logging.debug("parsing list of maintainers from config file")
        self.maintainers = [
            Address(item["name"], addr_spec=item["email"])
            for item in config.get("maintainers", [])
        ]

        # Set address to send triage emails from
        logging.debug("parsing triager email and password from config file")
        self.sender = None
        if "triager" in config:
            try:
                self.sender = {
                    "email": config["triager"]["address"],
                    "password": config["triager"]["password"],
                }
            except KeyError as exc:
                logging.error(f"triager config malformed, key {exc!s} not found")
            except TypeError:
                logging.error("triager config malformed, should be a dictionary")
        else:
            logging.warning("triager not found in config, will not send email")

        # Set last triage date
        logging.debug("setting last triage date")
        self.last_triage_date = datetime.utcnow() - timedelta(
            days=int(config["timedelta"])
        )

        self.github_token = config.get("github_token")
        if self.github_token:
            logging.info("Using GitHub token from config file") 
        elif os.getenv("GH_TOKEN"):
            self.github_token = os.getenv("GH_TOKEN")
            logging.info("Using GitHub token from environment variable")
        else:
            logging.warning("No GitHub token found. Proceeding without Token")

        logging.info("config file successfully parsed")

    @property
    def token(self):
        if self.github_token:
            return {"Authorization": f"token {self.github_token}"}
        return None

    @property
    def is_email_ready(self):
        return bool(self.sender and self.maintainers)