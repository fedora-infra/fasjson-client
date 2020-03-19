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
from openapi_client.models.inline_response2003 import InlineResponse2003  # noqa: E501
from openapi_client.rest import ApiException

class TestInlineResponse2003(unittest.TestCase):
    """InlineResponse2003 unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test InlineResponse2003
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.inline_response2003.InlineResponse2003()  # noqa: E501
        if include_optional :
            return InlineResponse2003(
                result = openapi_client.models.user.user(
                    login = '0', 
                    surname = '0', 
                    givenname = '0', 
                    mails = [
                        '0'
                        ], 
                    ircnick = '0', 
                    locale = '0', 
                    timezone = '0', 
                    gpgkeyids = [
                        '0'
                        ], 
                    creationts = '0', 
                    locked = True, )
            )
        else :
            return InlineResponse2003(
        )

    def testInlineResponse2003(self):
        """Test InlineResponse2003"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
