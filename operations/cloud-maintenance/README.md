# Cloud maintenance operations

Scripts in this directory are meant to be deployed in the cloud.

## AWS maintenance scripts

AWS maintenance scripts are deployed by using `aws-cli` image and the scripts deployed using
a configmap. In this way we do not need to produce an artifact for this purpose.

## S3 Cleanup script

S3 cleanup script accepts AWS bucket and access key/secret as env vars by referencing a secret with
a well-known format (`AWS_S3_SECRET_NAME`) and a list of of folder (in AWS that would be object
prefixes) to be removed.

Example list of object prefixes:

```yaml
- name: OBJECTS_TO_BE_DELETED
  value: "my-folder
yet-another-folder
example-folder
your-folder"
```

Declaring a list like above would delete all objects with such prefix, for example:

```
my-folder/myfile.txt
my-folder/anotherfile.txt
my-folder/foo.txt
yet-another-folder/bar.txt
yet-another-folder/foobar.txt
example-folder/mylog.log
example-folder/apache.log
example-folder/syslog.log
...
```

The script defaults in dry-run mode, but it can overridden by emptying `S3_CLEANER_EXTRA_PARAMS` variable.
