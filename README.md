# Ansible Network Triager

Set repositories of interest and run with `triager -c /path/to/config.yaml`

This tool assists in weekly bug triages and CI reports by fetching all issues, pull requests, and CI statuses from repositories specified in the configuration file. It retrieves items that were created (or updated) since a pre-defined number of days (`timedelta`). These are also filtered by the `labels` set in the config file. In case no `labels` are specified, then items that are currently unassigned are pulled.

By default, this prints out a table built from the fetched content to the console.
When run with `--send-email` it also emails this table to all the listed maintainers.

## Installation

pip install git+https://github.com/ansible-network/ansible-network-triager.git@master

git clone https://github.com/ansible-network/ansible-network-triager.git

cd ansible-network-triager

pip install -r requirements.txt

## Configuration

1. add your details such as organization_name, workflow_name in `config.yaml` file:


organization_name: "Ansible Networking"
workflow_name: "tests.yml"
repo_config: "repo_config.json"
timedelta: 14


2. update the `repo_config.json` file with your repos:


{
  "ansible-collections": {
    "ci_and_bug_repos": [
      "cisco.nxos",
      "cisco.ios"
    ],
    "bug_specific_repos": [
      "ansible.scm"
    ]
  }
}


3. Create a `.env` file in the root of your directory and add these details:


EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
MAINTAINERS=[{"name": "Your Name", "email": "your_email@example.com"}]
#GITHUB_TOKEN=your_github_token (optional - enter your github token here to make authenticated requests or comment this line to make unauthenticated API requests)


## Usage

### Local Usage

1. Run the bug scrub:

   triager --bugs -c config.yaml --log --send-email


2. Run the CI report:

   triager --ci -c config.yaml --log --send-email


### Docker Usage

1. Build the Docker image:

   docker-compose build


2. Run the bug scrub:

   docker-compose run triager --bugs -c config.yaml --log --send-email


3. Run the CI report:

   docker-compose run triager --ci -c config.yaml --log --send-email


### GitHub Actions

1. Store your secrets (EMAIL_SENDER, EMAIL_PASSWORD, MAINTAINERS, GITHUB_TOKEN) in GitHub Actions secrets.

To securely store sensitive information like email passwords and recipients, we'll use GitHub Secrets:
a) Go to your GitHub repository.
b) Click on "Settings" tab.
c) In the left sidebar, click on "Secrets and variables", then "Actions".
d) Click on "New repository secret".
e) Add the following secrets:

Name: EMAIL_SENDER (Your tools email address from which you want to send emails)
Name: EMAIL_PASSWORD (Your tools email password)
MAINTAINERS: A JSON string containing the maintainers information.

For example:

EMAIL_SENDER=your-tool-email@gmail.com
EMAIL_PASSWORD=your-email-password
MAINTAINERS=[{"name": "John Doe", "email": "john.doe@example.com"}, {"name": "Jane Doe", "email": "jane.doe@example.com"}]


2. Use the provided workflow files in `.github/workflows/` to set up automated runs.

## Options

Options | Usage
--- | ---
'-c'|Path to config file (selects 'config.yaml' in current working directory by default)
'--bugs'|Generate a bug scrub report
'--ci'|Generate a CI report
'--log'|Print logging information on the console (default level set to INFO)
'--log-to-file'|Dump logging information to a specified file (if no file is specified, the data will be written to /tmp/triager_{{ timestamp }}.log)
'--debug'|Bumps logging level to DEBUG
'--send-email'|Send the triaged table as an email to the list of maintainers

## Notes
- An example config file (example-config.yaml) has been placed in this repository for reference.
- Tested with Python 3.11
- This tool gets installed as a part of `ansible-network-tools` package.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
