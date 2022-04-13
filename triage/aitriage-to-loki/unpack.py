#!/usr/bin/env python3

import os
import os.path
import sys
import re
import tarfile
import json
import shutil
import urllib.request

LOKI_CLUSTER_URL_TEMPLATE = r"http://localhost:3000/explore?orgId=1&left=%7B%22datasource%22:%22Loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bcluster_id%3D%5C%22{cluster_id}%5C%22%7D%22%7D%5D,%22range%22:%7B%22from%22:%22now-90d%22,%22to%22:%22now%22%7D%7D"


class CollectorURLs:
    ClusterEventsJSON = None
    ClusterLogs = None
    InfraEnvJSON = None

    @classmethod
    def fields(cls):
        return (attr for attr in cls.__dict__ if not attr == "fields" and not attr.startswith("__"))


def maybe_adjust_base_url(base_url: str):
    """
    The AITRIAGE tickets logs are at an /#/ URL by default which is an HTML
    file browser, but this script needs the corresponding /files/ URL which is
    a JSON document. If the user accidentally gave us the /#/ URL we can just
    fix it ourselves to make the user's life easier
    """
    adjusted = base_url.replace("/#/", "/files/")

    if adjusted != base_url:
        print(f"Fixed URL from {base_url} to {adjusted}")

    return adjusted


def new_collector_urls(base_url):
    cluster_events_pattern = re.compile(r"cluster_\S+_events.json")
    infraenv_events_pattern = re.compile(r"infraenv_\S+_events.json")

    curl = CollectorURLs()
    with urllib.request.urlopen(base_url) as response:
        data = response.read()
        encoding = response.info().get_content_charset("utf-8")
        decoded = data.decode(encoding)

        try:
            JSON_object = json.loads(decoded)
        except json.decoder.JSONDecodeError:
            print("Error: Could not parse JSON data from collector URL:")
            print(decoded)
            sys.exit(1)

        for fileObj in JSON_object:
            name = fileObj.get("name")
            if not name:
                continue
            if name.endswith("_logs.tar"):
                curl.ClusterLogs = base_url + "/" + name
            if cluster_events_pattern.match(name):
                curl.ClusterEventsJSON = base_url + "/" + name
            if infraenv_events_pattern.match(name):
                curl.InfraEnvJSON = base_url + "/" + name

    if not curl.ClusterEventsJSON:
        raise Exception("Failed to find cluster events JSON")
    if not curl.ClusterLogs:
        raise Exception("Failed to find cluster logs archive")
    if not curl.InfraEnvJSON:
        raise Exception("Failed to find infra events JSON")
    return curl


def done(message, cluster_id):
    loki_url = LOKI_CLUSTER_URL_TEMPLATE.format(cluster_id=cluster_id)
    print(f"{message} - the logs can eventually be viewed at {loki_url}")


def main():
    if len(sys.argv) < 2:
        print("Usage: unpack.py <logs_url>")
        print("See README.md for more information")
        return 1

    base_url = sys.argv[1]
    base_url = maybe_adjust_base_url(base_url)

    cluster_id = base_url.rstrip("/").split("/")[-1].split("_")[-1]
    if cluster_id.strip() == "":
        print(f"Couldn't get cluster ID from {base_url}")
        return 1

    print(f"Fetching {cluster_id} info from {base_url}")

    collectorURLs = new_collector_urls(base_url)
    dest_dir = os.path.join("/tmp", "aitriage-loki", cluster_id)
    try:
        os.makedirs(dest_dir)
    except FileExistsError:
        done(
            f"{dest_dir} already exists! If you want to re-process the logs, delete it and try again",
            cluster_id,
        )
        return 0

    artifacts_dir = os.path.join(dest_dir, "artifacts")

    print(f"Fetching files to {artifacts_dir}")
    os.makedirs(artifacts_dir)

    for field in CollectorURLs.fields():
        url = getattr(collectorURLs, field)
        filename = url.split("/")[-1]
        with urllib.request.urlopen(url) as response:
            dest_file = os.path.join(artifacts_dir, filename)
            with open(dest_file, mode="wb") as tmp_file:
                shutil.copyfileobj(response, tmp_file)
                print(f"Fetched {url} to {dest_file}")

    if collectorURLs.ClusterLogs:
        print(f"Unpacking logs")
        # extract the first tar file
        filename = collectorURLs.ClusterLogs.split("/")[-1]
        logs_dst_dir = os.path.join(dest_dir, filename.split(".")[0])
        filepath = os.path.join(artifacts_dir, filename)
        file = tarfile.open(filepath)
        file.extractall(logs_dst_dir)
        file.close()

        for filename in os.listdir(logs_dst_dir):
            filepath = os.path.join(logs_dst_dir, filename)
            if not os.path.isfile(filepath):
                continue

            print(f"Extracting {filename}")
            file = tarfile.open(filepath)
            file.extractall(logs_dst_dir)
            file.close()

    done("Logs extracted!", cluster_id)


if __name__ == "__main__":
    sys.exit(main())
