# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import os
import sys
from enum import Enum
from shutil import copyfile
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import yaml

from common.aws.aws_api import AWSApi
from common.boto3.common import AWSClientError
from common.utils import TemporaryFolder
from pcluster.cli import LOGGER

ROOT_VOLUME_TYPE = "gp2"
PCLUSTER_RESERVED_VOLUME_SIZE = 15
InstanceRole = Enum("InstanceRole", ("ROLE", "INSTANCE_PROFILE"))


def get_ami_id(parent_image):
    """Get ami id from parent image, parent image could be image id or image arn."""
    if parent_image.startswith("arn"):
        ami_id = AWSApi.instance().imagebuilder.get_image_id(parent_image)
    else:
        ami_id = parent_image
    return ami_id


def get_info_for_ami_from_arn(image_arn):
    """Get image resources returned by imagebuilder's get_image API for the given arn of AMI."""
    return AWSApi.instance().imagebuilder.get_image_resources(image_arn)


def wrap_bash_to_component(custom_component):
    """Wrap bash script to custom component data property."""
    scheme = urlparse(custom_component).scheme
    tmp_dir = TemporaryFolder.instance().folder

    try:
        tmp_bash_script_folder = os.path.join(tmp_dir, "bash_component")
        if not os.path.exists(tmp_bash_script_folder):
            os.mkdir(tmp_bash_script_folder)

        tmp_bash_script_path = os.path.join(
            tmp_bash_script_folder,
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + custom_component.split("/")[-1],
        )

        if scheme == "https":
            urlretrieve(custom_component, filename=tmp_bash_script_path)
        elif scheme == "s3":
            output = urlparse(custom_component)
            AWSApi.instance().s3.download_file(output.netloc, output.path.lstrip("/"), tmp_bash_script_path)
        else:
            copyfile(custom_component.replace("file://", ""), tmp_bash_script_path)
    except URLError as e:
        LOGGER.critical(e.reason)
        sys.exit(1)
    except IOError as err:
        LOGGER.critical("I/O error: %s", err)
        sys.exit(1)
    except AWSClientError as e:
        LOGGER.critical(e)
        sys.exit(1)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    custom_component_bash_template_file = os.path.join(
        current_dir, "..", "pcluster", "resources", "imagebuilder", "custom_component_bash_template.yaml"
    )

    with open(custom_component_bash_template_file, "r") as file:
        custom_component_bash_template = yaml.load(file)
    with open(tmp_bash_script_path, "r") as file:
        bash_script = file.read()

    custom_component_bash_template["phases"][0]["steps"][0]["inputs"]["commands"][0] = custom_component_bash_template[
        "phases"
    ][0]["steps"][0]["inputs"]["commands"][0].replace("{{ place-holder }}", bash_script)

    return yaml.dump(custom_component_bash_template)
