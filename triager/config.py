import json
import logging
import os
import sys
from datetime import datetime, timedelta
from email.headerregistry import Address

import yaml


class Config:
    def __init__(self, cfg):
        # select config.yaml from cwd
        logging.debug(f"Config.__init__ called with cfg: {cfg}")
        self.cfg_path = self._get_config_path(cfg)
        self.config_data = self._load_config_file()
        self._initialize_config()

    def _get_config_path(self, cfg):
        if not cfg:
            logging.info("config file not specified, setting default")
            return "./config.yaml"
        return cfg

    def _load_config_file(self):
        logging.info(f"attempting to read config file: {self.cfg_path}")
        try:
            with open(self.cfg_path, "r") as config_file:
                config_content = config_file.read()
            logging.debug(f"Raw config content: {config_content}")
            return self._parse_yaml(config_content)
        except FileNotFoundError as e:
            logging.critical(f"Config file not found: {e}")
            sys.exit(1)

    def _parse_yaml(self, content):
        try:
            config = yaml.safe_load(content)
            logging.debug(f"Parsed config: {config}")
            if config is None:
                raise ValueError("Config file is empty or not valid YAML")
            return config
        except yaml.YAMLError as e:
            logging.critical(f"Error parsing YAML file: {e}")
            sys.exit(1)
        except ValueError as e:
            logging.critical(str(e))
            sys.exit(1)

    def _initialize_config(self):
        logging.info("parsing information from config file")
        self._set_organization_info()
        self._set_repo_config()
        self._set_maintainers()
        self._set_email_config()
        self._set_last_triage_date()
        self._set_github_token()

    def _set_organization_info(self):
        self.organization_name = self.config_data.get("organization_name")
        logging.debug(f"organization_name: {self.organization_name}")
        self.workflow_name = self.config_data.get("workflow_name")
        logging.debug(f"workflow_name: {self.workflow_name}")

    def _set_repo_config(self):
        repo_config_json = os.environ.get("REPO_CONFIG")
        if repo_config_json:
            try:
                repo_config = json.loads(repo_config_json)
                logging.debug(f"Parsed repo config: {repo_config}")
            except json.JSONDecodeError as e:
                logging.critical(f"Error parsing REPO_CONFIG JSON: {e}")
                sys.exit(1)
        else:
            logging.critical("REPO_CONFIG environment variable not found")
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
    def _set_maintainers(self):
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
    def _set_email_config(self):
        self.sender = {
            "email": os.environ.get("EMAIL_SENDER"),
            "password": os.environ.get("EMAIL_PASSWORD"),
        }

        if self.sender["email"] and self.sender["password"]:
            logging.info("Email configuration found in environment variables")
        else:
            logging.warning(
                "Email configuration not found in environment variables",
            )

    # Set last triage date
    def _set_last_triage_date(self):
        self.last_triage_date = datetime.utcnow() - timedelta(
            days=int(self.config_data.get("timedelta", 14)),
        )
        logging.debug(f"Last triage date: {self.last_triage_date}")

    def _set_github_token(self):
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
        return bool(
            self.sender["email"] and self.sender["password"] and self.maintainers,
        )
