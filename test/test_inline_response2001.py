# coding: utf-8

"""
    Fedora Account Service JSON API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import openapi_client
from openapi_client.models.inline_response2001 import InlineResponse2001  # noqa: E501
from openapi_client.rest import ApiException

class TestInlineResponse2001(unittest.TestCase):
    """InlineResponse2001 unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test InlineResponse2001
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.inline_response2001.InlineResponse2001()  # noqa: E501
        if include_optional :
            return InlineResponse2001(
                result = openapi_client.models.group_page.group_page(
                    data = [
                        openapi_client.models.group.group(
                            cn = '0', )
                        ], 
                    pagination = openapi_client.models.user_ref_page_pagination.user_ref_page_pagination(
                        current = 56, 
                        previous = 56, 
                        next = 56, ), )
            )
        else :
            return InlineResponse2001(
        )

    def testInlineResponse2001(self):
        """Test InlineResponse2001"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
