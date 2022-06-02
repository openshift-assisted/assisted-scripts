Triage Scripts
====

A collection of scripts that can be useful when triaging Assisted Installer tickets.

* [aitriage-to-loki](aitriage-to-loki) uses the Loki+Promtail+Grafana stack to parse and search triage logs. More details can be found in the script's [README](aitriage-to-loki/README.md).

* [download-logs.py](download-logs.py) is a simple script that requires only Python 3. It takes the URL of a cluster failure logs as it appears in a triage ticket, downloads them into a subdirectory, and recursively unpacks popular archive formats (e.g. `.tar.gz`, `.tar.bz2`, `.tar.xz`). By default, the last part of the URL will be used as the subdirectory name. Optionally, a custom name can be specified in the second argument, such as the triage ticket ID. The path is relative to working directory, unless an absolute path is given.