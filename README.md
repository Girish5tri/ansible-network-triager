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
timedelta: 14

2. Create a `.env` file in the root of your directory and add these details:

EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
MAINTAINERS=[{"name": "Your Name", "email": "your_email@example.com"}]
#GITHUB_TOKEN=your_github_token (optional - enter your github token here to make authenticated requests or comment this line to make unauthenticated API requests)
REPO_CONFIG = {
<organization>: {
"ci_and_bug_repos": [<list of repositories>],
"bug_specific_repos": [<list of repositories>]
}
}

## Usage

### Local Usage

1. Run the bug scrub:

   triager --bugs -c config.yaml --log --send-email

2. Run the CI report:

   triager --ci -c config.yaml --log --send-email

### Docker Usage

1. Build the Docker image:

   sudo docker-compose build

2. Run the bug scrub:

   sudo docker-compose run triager

3. Run the CI report:

   sudo docker-compose run ci_report

### GitHub Actions

This tool uses GitHub Actions for automated reporting. To set up the workflows:

1. Store your secrets in GitHub Actions:
   a) Go to your GitHub repository
   b) Click on "Settings" tab
   c) In the left sidebar, click on "Secrets and variables", then "Actions"
   d) Click on "New repository secret"
   e) Add the following secrets:

   - `EMAIL_SENDER`: Your tool's email address for sending reports
   - `EMAIL_PASSWORD`: Your tool's email password
   - `MAINTAINERS`: A JSON string containing the maintainers' information
   - `REPO_CONFIG`: A JSON string containing the repository configuration

2. The following workflows are available in `.github/workflows/`:

   - `bug_triager_workflow.yml`: Runs weekly bug triage
   - `ci_workflow.yml`: Runs daily CI status report

### Workflow Details

#### Bug Triage Workflow

This workflow runs every Wednesday at 2:30 PM IST (9:00 AM UTC) and can also be triggered manually.

```yaml
name: Bug Triage Workflow

on:
  schedule:
    - cron: '0 9 * * 3'
  workflow_dispatch:

jobs:
  run-bug-triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - run: pip install -r requirements.txt
      - run: python -m triager --bugs -c example-config.yaml --log --send-email
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          GITHUB_TOKEN: ${{ github.token }}
          MAINTAINERS: ${{ secrets.MAINTAINERS }}
          REPO_CONFIG: ${{ secrets.REPO_CONFIG }}

#### CI Report Workflow

This workflow runs daily at 12:00 PM IST (6:30 AM UTC) and can also be triggered manually.

''''yaml
name: Nightly CI Report Workflow

on:
  schedule:
    - cron: '30 6 * * *'
  workflow_dispatch:

jobs:
  run-ci-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - run: pip install -r requirements.txt
      - run: python -m triager --ci -c example-config.yaml --log --send-email
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          GITHUB_TOKEN: ${{ github.token }}
          MAINTAINERS: ${{ secrets.MAINTAINERS }}
          REPO_CONFIG: ${{ secrets.REPO_CONFIG }}


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

## Pre-commit Hooks

This tool uses pre-commit hooks to ensure code quality. The hooks perform the following checks:

- Check for merge conflicts
- Verify symlinks
- Detect debug statements
- Fix end of files
- Remove trailing whitespace
- Add trailing commas
- Format code with Prettier
- Sort import statements with isort
- Format Python code with Black
- Lint Python code with Flake8

To use pre-commit:

1. Install pre-commit: `pip install pre-commit`
2. Install the git hook scripts: `pre-commit install`
3. (Optional) Run against all files: `pre-commit run --all-files`

Pre-commit will now run automatically on `git commit`. You can also run it manually on staged files with `pre-commit run`.


## Notes
- An example config file (example-config.yaml) has been placed in this repository for reference.
- Tested with Python 3.11
- This tool gets installed as a part of `ansible-network-tools` package.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
```
