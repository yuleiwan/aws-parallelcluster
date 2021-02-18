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
import json
import os
import shutil
from tempfile import mkdtemp
from urllib.request import urlopen

import yaml


def download_file(url):
    """Download file from given url."""
    response = urlopen(url)
    return response.read().decode("utf-8")


def load_yaml_dict(config_file):
    """Read the content of a yaml file."""
    with open(config_file) as conf_file:
        yaml_content = yaml.load(conf_file, Loader=yaml.SafeLoader)
    # TODO prevent yaml.load from converting 1:00:00 to int 3600

    # TODO use from cfn_flip import load_yaml
    return yaml_content


def load_yaml(source_dir, file_name):
    """Get string data from yaml file."""
    return yaml.dump(load_yaml_dict(os.path.join(source_dir, file_name)))


def validate_json_format(data):
    """Validate the input data in json format."""
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


class TemporaryFolder:
    """
    Create a temporary folder.

    Singleton pattern is implemented to keep one temporary folder in global scope.
    """

    _instance = None

    def __init__(self):
        self.folder = mkdtemp()

    @staticmethod
    def instance():
        """Get temporary folder instance."""
        if not TemporaryFolder._instance:
            TemporaryFolder._instance = TemporaryFolder()
        return TemporaryFolder._instance

    @staticmethod
    def delete_folder():
        """Delete temporary folder."""
        try:
            if TemporaryFolder._instance:
                shutil.rmtree(TemporaryFolder._instance.folder)
                TemporaryFolder._instance = None
        except OSError as e:
            print("Error: %s : %s" % (TemporaryFolder._instance.folder, e.strerror))
