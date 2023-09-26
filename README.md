# README - links-checker

## Goal
This tool searches dead links.

It starts from a page and crawls from it with a specified depth.

It only crawls within Confluence.

It generates Tab Separated Values (.csv) files where it lists:
1. all pages visited (visited.csv)
2. all links pointing to invalid pages (invalid.csv)
3. all links pointing to Bitbucket repositories (bitbucket.csv)
4. all links pointing to Connections (connections.csv)
5. all links discarded for any reason (discarded.csv)

The tool also lists whether the page is tagged ina way that it should be referred to a specific team.


## Before running
Update OWNERS_TAGS in main.py following the list available in https://confluence.aws.abnamro.org/display/GRIDAD/Compliance+Dashboard

The script automatically downloads the latest version of the Chrome driver. This will work only if on has the latest version of Chrome installed.

## TIA ROOT CA 2022 certificate
The links checker needs the TIA ROOT CA 2022 certificate to connect to Confluence. Read the [Certificate Hell](https://confluence.aws.abnamro.org/pages/viewpage.action?spaceKey=MOBP&title=Certificate+Hell) page for information about downloading the required .pem file.

## Usage
Use Python 3.10.0 (managed via [pyenv](https://github.com/pyenv/pyenv))
Configuration settings (e.g. search entry point and depth) are in `main.py` but can be overridden via command line.
Use the -d option to use defaults.

If the ABN AMRO certificate has been downloaded in `$HOME/TIAROOT2022.pem`

```
python -m venv venv
source venv/bin/activate
pip --cert "$HOME/TIAROOT2022.pem" install -r requirements.txt
cat $HOME/certs/TIAROOTCA2022.pem >> venv/lib/python3.10/site-packages/certifi/cacert.pem
cat $HOME/certs/TIAROOTCA2022.pem >> venv/lib/python3.10/site-packages/pip/_vendor/certifi/cacert.pem
python main.py -d
deactivate
```

Note: ZScaler will show a warning when the server proxy is used in the configuration of the links checker.

## Tech

### Constraints
Various sites use SSO to connect (SAML+Kerberos):
1. the script cannot be run in a pipeline since the agents are not SSO
2. using only direct REST calls is too time-consuming
3. most pages do not provide REST APIs to fetch the content 

### Adopted Strategy
1. We use Python for maintainability
2. We use Selenium, which is slower but handles the SSO automatically
   
   Note: this is not the recommended approach (see https://www.selenium.dev/documentation/en/worst_practices/link_spidering/), but a full implementation of SAML on top of Kerberos is not practical.


