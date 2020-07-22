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

        logging.info("attempting to read config file: {0}".format(cfg))

        try:
            with open(cfg, "r") as config_file:
                config = yaml.safe_load(config_file)
            logging.info("config file successfully loaded")
        except FileNotFoundError as e:
            logging.critical(e)
            sys.exit()

        logging.info("parsing information from config file")

        # Populate org and repos to triage
        self.repos = []
        logging.debug("parsing orgs and repositories from config file")
        for org in config["orgs"]:
            for repo in org["repos"]:
                self.repos.append((org["name"], repo))

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
                logging.error(
                    f"triager config malformed, key {exc!s} not found"
                )
            except TypeError:
                logging.error(
                    "triager config malformed, should be a dictionary"
                )
        else:
            logging.debug("triager not found in config, will not send email")

        # Set last triage date
        logging.debug("setting last triage date")
        self.last_triage_date = datetime.utcnow() - timedelta(
            days=int(config["timedelta"])
        )

        logging.info("config file successfully parsed")

    @property
    def token(self):
        logging.debug("fetching oauth token")
        if os.getenv("GH_TOKEN"):
            return {"Authorization": "token {0}".format(os.getenv("GH_TOKEN"))}

    @property
    def is_email_ready(self):
        return bool(self.sender and self.maintainers)
