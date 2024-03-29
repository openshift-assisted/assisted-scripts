# Cloud maintenance operations

Scripts in this directory are meant to be deployed in the cloud.

## AWS maintenance scripts

AWS maintenance scripts are deployed by using `aws-cli` image and the scripts deployed using
a configmap. In this way we do not need to produce an artifact for this purpose.

## S3 Bootlog Cleanup script

S3 cleanup script accepts AWS bucket and access key/secret as env vars by referencing a secret with
a well-known format (`AWS_S3_SECRET_NAME`).

The script will look for bootlog tar for each host, and remove it.

The script defaults in dry-run mode, but it can overridden by emptying `S3_CLEANER_EXTRA_PARAMS` variable.
