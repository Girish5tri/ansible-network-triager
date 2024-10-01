import argparse
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from triager import triager
from triager.config import Config
from triager.mailer import send_mail
from triager.release import __ver__
from triager.tablemaker import make_table
from triager.ci_report import generate_ci_report

def run(args):
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(levelname)-10s%(message)s')

    load_dotenv()

    try:
        config = Config(args.config_file)
        report_date = datetime.now().strftime("%Y-%m-%d")

        if args.bugs:
            issues = triager.triage(config, config.bug_repos)
            if issues:
                table = make_table(issues)
                print(table)
                if args.send_email and config.is_email_ready:
                    send_mail(content=table, config=config, subject=f"{config.organization_name} Weekly Triage - {report_date}")
            else:
                message = "No new issues found or error occurred during triage."
                print(message)
                if args.send_email and config.is_email_ready:
                    send_mail(content=message, config=config, subject=f"{config.organization_name} Weekly Triage - No New Issues - {report_date}")
        elif args.ci:
            ci_report = generate_ci_report(config)
            if ci_report:
                table = make_table(ci_report, ci=True)
                print(table)
                report_date = ci_report.get("date", datetime.now().strftime("%Y-%m-%d"))
                status = ci_report.get("overall_status", "Unknown")
                if args.send_email and config.is_email_ready:
                    send_mail(content=table, config=config, subject=f"{config.organization_name} Nightly CI Report - {report_date} - {status}")
            else:
                logging.warning("No CI report generated or error occurred during CI report generation.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Triage issues and pull-requests from repositories of interest.",
        prog="Ansible Network Triager",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        action="store",
        help="Path to config file (selects 'config.yaml' in cwd by default)",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--bugs",
        action="store_true",
        help="Generate a bug scrub report"
    )
    group.add_argument(
        "--ci",
        action="store_true",
        help="Generate a CI report"
    )
    parser.add_argument(
        "--log-to-file",
        nargs="?",
        const="/tmp/triager-{0}.log".format(
            datetime.now().strftime("%Y-%m-%d-%X")
        ),
        dest="log_to_file",
        help="save logging information to a file",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="display logging data on console"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Bump logging level to debug"
    )

    parser.add_argument(
        "--send-email",
        action="store_true",
        help="send the report as an email to the list of maintainers",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="show version number"
    )

    args = parser.parse_args()

    if args.version:
        print("Ansible Network Triager, version {0}".format(__ver__))
    else:
        run(args)


if __name__ == "__main__":
    main()
