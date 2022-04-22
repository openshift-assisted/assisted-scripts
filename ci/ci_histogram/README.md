# CI Histogram

With this script we can make a search query to search.ci.openshift.org for a specified timespan, and get the number of hits per day

This is useful to see how often an error (or a pattern) happens on CI

## How this works
The script makes a query to search.ci.openshift.org and iterates through the resultin json

Usually each log line starts with a datetime, which we use to know when a log was produced. However, there are cases that we want to search for patterns that are in lines without a date, in those cases we need to use the `exhaustive mode` (see below)

## Configuration
There are a few things we can configure:
- `job_regex` is a regular expresion to match the jobs that we want to filter. It defaults to `.*e2e-metal-assisted.*|.*ai-operator.*` regex
- `age` is the number of hours that we want to search back. It defaults to 504h that is 7 days

## Exhaustive date extractor
When the log lines that have the pattern we're looking do not start with a datetime, the script can use exhaustive mode by passing `-e` argument

In exhaustive mode, we get the job ids that match, and we generate a new query per job to get the starting time of the job

Take notice that this can potentially initiate many new http requests, if the result has many jobs matching

If you see discrepancies in numbers, take into account that in normal mode the script counts log lines that match, while in exhaustive mode the script counts jobs that match

We can tweak how many parallel requests are to be made with the `-p` argument

## Help
The help of the script should be pretty explanatory, so here it is:
~~~
Usage:
    ci_histogram [-e [-p num]] [-j job_regex] [-t age] <search_regex>
    ci_histogram --help

Options:
    -e              Exhaustive date extractor. Get date from PROW's started.json file
    -p num          Number of concurrent requests to get prow files (only applies with -e) [default: 10]
    -j job_regex    Search only jobs specified by this regex [default: .*e2e-metal-assisted.*|.*ai-operator.*]
    -t age          Timeframe to look backwards for logs [default: 504h]
    search_regex    Search this text in build-log
~~~

## Examples

### Normal mode
~~~
arale ~$ ci_histogram "the output has been hidden"
2022-04-12      1
~~~
We can tell that in the last 3 weeks only happent once, so it's probably a one time problem


### Exhaustive mode
~~~
arale ~$ ci_histogram "minikube: command not found"
./scripts/download_logs.sh:     22
arale ~$ ci_histogram -e "minikube: command not found"
2022-04-08      5
2022-04-10      1
2022-04-11      5
2022-04-12      10
2022-04-20      1
~~~
We can see that it is something that happens from time to time, but maybe often enough to give it a better look
