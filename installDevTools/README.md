# installDevTool.py

This tool installs tools (mostly cli) directly from github.
It requires a config for each tool in toolConfigs.yml 
Option:

* You can install a specific tool with the -t <toolName>
* without options it will try to get the latest release from all tools specified in config.yml (toolsToInstall list)

## required Python modules
```bash 
pip install wget jinja2 pyaml-env
```  