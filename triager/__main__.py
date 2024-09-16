import argparse
import logging
from datetime import datetime

from triager import triager
from triager.config import Config
from triager.mailer import send_mail
from triager.release import __ver__
from triager.tablemaker import make_table
from triager.ci_report import generate_ci_report

def run(args):
    # setup logger
    logging_level = logging.DEBUG if args.debug else logging.INFO
    if args.log_to_file:
        logging.basicConfig(filename=args.log_to_file, level=logging_level)
    elif args.log:
        logging.basicConfig(
            format="%(levelname)-10s%(message)s", level=logging_level
        )

    config = Config(args.config_file)
    if args.bugs:
        issues = triager.triage(config)
        if issues:
            table = make_table(issues)
            logging.info("Printing triaged table to console")
            print(table)
            if args.send_email and config.is_email_ready:
                send_mail(content=table, config=config, subject="Ansible Network Weekly Triage")
    elif args.ci:
        ci_report = generate_ci_report(config)
        if ci_report:
            table = make_table(ci_report, ci=True)
            logging.info("Printing CI report table to console")
            print(table)
            report_date = ci_report.get("date", datetime.now().strftime("%Y-%m-%d"))
            status = ci_report.get("overall_status", "Unknown")
            if args.send_email and config.is_email_ready:
                send_mail(content=table, config=config, subject=f"Ansible Network Nightly CI Report - {report_date} - {status}")


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
