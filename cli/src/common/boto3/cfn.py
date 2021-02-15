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

from common.boto3.common import AWSExceptionHandler, Boto3Client


class CfnClient(Boto3Client):
    """Implement CFN Boto3 client."""

    def __init__(self):
        super().__init__("cloudformation")

    @AWSExceptionHandler.handle_client_exception
    def create_stack(self, stack_name, disable_rollback, tags, template_url=None, template_body=None):
        """Create CFN stack by using the given template."""
        if template_url:
            return self._client.create_stack(
                StackName=stack_name,
                TemplateUrl=template_url,
                Capabilities=["CAPABILITY_IAM"],
                DisableRollback=disable_rollback,
                Tags=tags,
            )
        else:
            return self._client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=["CAPABILITY_IAM"],
                DisableRollback=disable_rollback,
                Tags=tags,
            )
