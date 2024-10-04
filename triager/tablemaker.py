import logging
import textwrap

import prettytable

WRAPPER = textwrap.TextWrapper(width=80)


def make_table(data, ci=False):
    logging.info("building table from data")
    if ci:
        table = prettytable.PrettyTable(["Repo", "Status", "URL"])
        table.align["URL"] = "l"
        table.max_width["URL"] = 120
        for entry in data["data"]:
            table.add_row(
                [
                    entry["repo"],
                    entry["status"],
                    entry["url"],
                ],
            )
    else:
        table = prettytable.PrettyTable(["Repo", "Title", "URL", "Type"])
        table.align["URL"] = "l"
        table.max_width["URL"] = 120
        for repo, entries in data.items():
            for entry in entries:
                table.add_row(
                    [
                        repo,
                        "\n".join(WRAPPER.wrap(text=entry["title"])),
                        entry["url"],
                        entry["type"],
                    ],
                )

    table.hrules = prettytable.ALL
    logging.info("successfully built table from data")
    return table
