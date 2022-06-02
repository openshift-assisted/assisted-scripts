# Triage Scripts

A collection of scripts that can be useful when triaging Assisted Installer tickets.

* [download-logs.py](download-logs.py) &mdash; takes the URL of cluster logs as it appears in a triage ticket, downloads them into a subdirectory, and recursively unpacks popular archive formats (e.g. `.tar.gz`, `.tar.bz2`, `.tar.xz`). By default, the last part of the URL will be used as the subdirectory name. Optionally, a custom name can be specified in the second argument, such as a triage ticket ID. The path is relative to the working directory, unless an absolute path is given.