import logging
import os
import sys
import json
from datetime import datetime, timedelta
from email.headerregistry import Address

import yaml


class Config:
    def __init__(self, cfg):
        # select config.yaml from cwd
        logging.debug(f"Config.__init__ called with cfg: {cfg}")
        if not cfg:
            logging.info("config file not specified, setting default")
            cfg = "./config.yaml"

        logging.info(f"attempting to read config file: {cfg}")

        try:
            with open(cfg, "r") as config_file:
                config_content = config_file.read()
                logging.debug(f"Raw config content: {config_content}")
                config = yaml.safe_load(config_content)
            logging.debug(f"Parsed config: {config}")
            
            if config is None:
                raise ValueError("Config file is empty or not valid YAML")
            
        except FileNotFoundError as e:
            logging.critical(f"Config file not found: {e}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.critical(f"Error parsing YAML file: {e}")
            sys.exit(1)
        except ValueError as e:
            logging.critical(str(e))
            sys.exit(1)

        logging.info("parsing information from config file")
        self.organization_name = config.get("organization_name")
        logging.debug(f"organization_name: {self.organization_name}")
        self.workflow_name = config.get("workflow_name")
        logging.debug(f"workflow_name: {self.workflow_name}")

        # Parse repo_config.json
        repo_config_path = config.get("repo_config", "repo_config.json")
        logging.info(f"Attempting to read repo config file: {repo_config_path}")
        try:
            with open(repo_config_path, "r") as repo_config_file:
                repo_config_content = repo_config_file.read()
                logging.debug(f"Raw repo config content: {repo_config_content}")
                repo_config = json.loads(repo_config_content)
            logging.debug(f"Parsed repo config: {repo_config}")
        except FileNotFoundError as e:
            logging.critical(f"Repo config file not found: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.critical(f"Error parsing repo config JSON: {e}")
            sys.exit(1)

        # Initialize repos
        self.bug_repos = []
        self.ci_repos = []

        # Parse repos from repo_config
        for org, repos in repo_config.items():
            logging.debug(f"Processing org: {org}")
            for repo in repos.get("ci_and_bug_repos", []):
                self.bug_repos.append((org, repo))
                self.ci_repos.append(f"{org}/{repo}")
            for repo in repos.get("bug_specific_repos", []):
                self.bug_repos.append((org, repo))

        logging.debug(f"Bug repos: {self.bug_repos}")
        logging.debug(f"CI repos: {self.ci_repos}")

        # Parse maintainers
        maintainers_json = os.environ.get("MAINTAINERS", "[]")
        logging.debug(f"MAINTAINERS env var: {maintainers_json}")
        try:
            maintainers_list = json.loads(maintainers_json)
            self.maintainers = [
                Address(item["name"], addr_spec=item["email"])
                for item in maintainers_list
            ]
        except json.JSONDecodeError:
            logging.error("Failed to parse MAINTAINERS JSON. Using empty list.")
            self.maintainers = []

        logging.debug(f"Maintainers: {self.maintainers}")

        # Parse email configuration
        self.sender = {
            "email": os.environ.get("EMAIL_SENDER"),
            "password": os.environ.get("EMAIL_PASSWORD"),
        }
        
        if self.sender["email"] and self.sender["password"]:
            logging.info("Email configuration found in environment variables")
        else:
            logging.warning("Email configuration not found in environment variables")

        # Set last triage date
        self.last_triage_date = datetime.utcnow() - timedelta(
            days=int(config.get("timedelta", 14))
        )
        logging.debug(f"Last triage date: {self.last_triage_date}")

        self.github_token = os.environ.get("GITHUB_TOKEN")
        if self.github_token:
            logging.info("Using GitHub token from environment")
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
        return bool(self.sender["email"] and self.sender["password"] and self.maintainers)