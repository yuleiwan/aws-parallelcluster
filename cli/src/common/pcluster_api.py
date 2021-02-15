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
import yaml

from common.aws.aws_api import AWSApi
from pcluster.models.imagebuilder import ImageBuilderActionError
from pcluster.schemas.cluster_schema import ClusterSchema
from pcluster.schemas.imagebuilder_schema import ImageBuilderSchema
from pcluster.templates.cdk_builder import CDKTemplateBuilder
from pcluster.utils import get_installed_version, get_stack, get_stack_name, get_stack_output_value, get_stack_version


class ApiFailure:
    """Represent a generic api error."""

    def __init__(self, message: str = None, config_validation_errors: list = None):
        self.message = message or "Something went wrong."
        self.config_validation_errors = config_validation_errors or []


class PclusterApi:
    """Proxy class for all Pcluster API commands used in the CLI."""

    def __init__(self):
        pass

    @staticmethod
    def build_image(imagebuilder_config: dict, image_name: str, region: str = None, disable_rollback: bool = False):
        """
        Load imagebuilder model from imagebuilder_config and create stack.

        :param imagebuilder_config: cluster configuration (yaml dict)
        :param image_name: the name to assign to the image
        :param region: AWS region
        :param disable_rollback: Disable rollback in case of failures
        """
        try:
            # Generate model from imagebuilder dict
            imagebuild = ImageBuilderSchema().load(imagebuilder_config)
            imagebuilder_template = CDKTemplateBuilder().build_imagebuilder_template(imagebuild=imagebuild)
            imagebuild.imagebuild_template = imagebuilder_template
            response = imagebuild.create(image_name, region, disable_rollback)
            return response

        except ImageBuilderActionError as e:
            print(e)
            return ApiFailure(e)
