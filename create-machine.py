#!/usr/bin/env python

# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example of using the Compute Engine API to create and delete instances.

Creates a new compute engine instance and uses it to apply a caption to
an image.

    https://cloud.google.com/compute/docs/tutorials/python-guide

For more information, see the README.md under /compute.
"""

import argparse
import os
import time

import googleapiclient.discovery


def list_instances(
    compute: object,
    project: str,
    zone: str,
) -> list:
    """Lists all instances in the specified zone.

    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone in which the instances should be listed.

    Returns:
      A list of instances.
    """
    result = compute.instances().list(project=project, zone=zone).execute()
    return result["items"] if "items" in result else None

def create_firewall(compute: object, project: str, name: str, network: str="default") -> str:
    """Creates a firewall rule.
    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone in which the firewall rule should be created.
      name: the name of the firewall rule.
      network: the name of the network in which the firewall rule should be created.
    """
    # First, check if the firewall rule already exists
    try:
        existing = compute.firewalls().get(project=project, firewall=name).execute()
        print(f"Firewall rule '{name}' already exists.")
        return existing
    except Exception as e:
        # Firewall doesn't exist, proceed to create it
        pass
    
    config = {
        "allowed": [{"IPProtocol": "tcp", "ports": ["5000"]}],
        "direction": "INGRESS",
        "kind": "compute#firewall",
        "name": name,
        "network": f"projects/{project}/global/networks/{network}",
        "priority": 1000,
        "sourceRanges": ["0.0.0.0/0"],
        "targetTags": [name]  # This tag should match the instance tag
    }
    return compute.firewalls().insert(project=project, body=config).execute()

def set_instance_tags(
    compute: object,
    project: str,
    zone: str,
    instance_name: str,
    tags: list,
) -> dict:
    """Sets tags on a compute instance.
    
    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone where the instance is located.
      instance_name: the name of the instance.
      tags: a list of tag strings to apply to the instance.
    
    Returns:
      The operation object.
    """
    # Get the current fingerprint of the instance
    instance = compute.instances().get(
        project=project, zone=zone, instance=instance_name
    ).execute()
    
    # Set the tags (fingerprint is required to prevent conflicts)
    tags_body = {
        "items": tags,
        "fingerprint": instance.get("tags", {}).get("fingerprint", "")
    }
    
    return compute.instances().setTags(
        project=project,
        zone=zone,
        instance=instance_name,
        body=tags_body
    ).execute()


# [START compute_create_instance]
def create_instance(
    compute: object,
    project: str,
    zone: str,
    name: str,
    startup_script: str,
) -> str:
    """Creates an instance in the specified zone.

    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone in which the instances should be created.
      name: the name of the instance.

    Returns:
      The instance object.
    """
    # Get the latest Debian Jessie image.
    image_response = (
        compute.images()
        .getFromFamily(project="ubuntu-os-cloud", family="ubuntu-2204-lts")
        .execute()
    )
    source_disk_image = image_response["selfLink"]

    # Configure the machine
    machine_type = "zones/%s/machineTypes/e2-standard-2" % zone
    script_path = os.path.join(os.path.dirname(__file__), f"{startup_script}.sh")
    with open(script_path, "r", newline=None) as f:
        startup_script = f.read().replace("\r\n", "\n").replace("\r", "\n")

    config = {
        "name": name,
        "machineType": machine_type,
        # Specify the boot disk and the image to use as a source.
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_disk_image,
                },
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
        # Allow the instance to access cloud storage and logging.
        "serviceAccounts": [
            {
                "email": "default",
                "scopes": [
                    "https://www.googleapis.com/auth/devstorage.read_write",
                    "https://www.googleapis.com/auth/logging.write",
                ],
            }
        ],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        "metadata": {
            "items": [
                {
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    "key": "startup-script",
                    "value": startup_script,
                }
            ]
        },
    }

    return compute.instances().insert(project=project, zone=zone, body=config).execute()


def get_instance_public_ip(compute: object, project: str, zone: str, name: str) -> str:
    """Gets the public IP address of an instance.
    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone in which the instance is located.
      name: the name of the instance.
    """
    return compute.instances().get(project=project, zone=zone, instance=name).execute()["networkInterfaces"][0]["accessConfigs"][0]["natIP"]


def delete_instance(
    compute: object,
    project: str,
    zone: str,
    name: str,
) -> str:
    """Deletes an instance.

    Args:
      compute: An initialized compute service object.
      project: The Google Cloud project ID.
      zone: The name of the zone in which the instances should be deleted.
      name: The name of the instance.

    Returns:
      Execute to delete the instance object.
    """
    return (
        compute.instances().delete(project=project, zone=zone, instance=name).execute()
    )


# [START compute_wait_for_operation]
def wait_for_operation(
    compute: object,
    project: str,
    zone: str,
    operation: str,
) -> dict:
    """Waits for the given operation to complete.

    Args:
      compute: an initialized compute service object.
      project: the Google Cloud project ID.
      zone: the name of the zone in which the operation should be executed.
      operation: the operation ID.

    Returns:
      The result of the operation.
    """
    print("Waiting for operation to finish...")
    while True:
        result = (
            compute.zoneOperations()
            .get(project=project, zone=zone, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)


# [END compute_wait_for_operation]


def main(
    project: str,
    zone: str,
    instance_name: str,
    startup_script: str,
) -> None:
    """Runs the demo.

    Args:
      project: the Google Cloud project ID.
      bucket: the name of the bucket in which the image should be written.
      instance_name: the name of the instance.
      wait: whether to wait for the operation to complete.

    Returns:
      None.
    """
    compute = googleapiclient.discovery.build("compute", "v1")
    
    print("Creating firewall.")

    operation = create_firewall(compute, project, "allow-5000")
    #wait_for_operation(compute, project, zone, operation["name"])

    print("Creating instance.")

    operation = create_instance(compute, project, zone, instance_name, startup_script)
    wait_for_operation(compute, project, zone, operation["name"])

    instances = list_instances(compute, project, zone)

    print(f"Instances in project {project} and zone {zone}:")
    for instance in instances:
        print(f' - {instance["name"]}')

    print("Setting tags on instance.")
    operation = set_instance_tags(compute, project, zone, instance_name, ["allow-5000"])
    wait_for_operation(compute, project, zone, operation["name"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project_id", help="Your Google Cloud project ID.")
    parser.add_argument(
        "--zone", default="us-west1-a", help="Compute Engine zone to deploy to."
    )
    
    parser.add_argument("--name", help="New instance name.")
    
    parser.add_argument("--startup_script", help="Startup script to run on the instance.")

    args = parser.parse_args()

    main(args.project_id, args.zone, args.name, args.startup_script)