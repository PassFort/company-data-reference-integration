# coding: utf-8

"""
    Thomson Reuters World-Check One API

    The World-Check One API enables developers to integrate the next generation of Thomson Reuters screening capabilities into existing workflows and internal systems (such as CRMs) in order to help streamline the processes for on-boarding, KYC and third party due diligence. The API provides, among other features: - The ability to screen entity names, with or without secondary fields such as date of birth for individuals. These names are called “cases” within the World-Check One system. - The ability to retrieve results of the screening process from the World-Check database - The ability to flag cases for Ongoing Screening, and retrieve the World-Check results from the Ongoing Screening process. > © 2017 Thomson Reuters. All rights reserved. Republication or redistribution of Thomson Reuters content, including by framing or similar means, is prohibited without the prior written consent of Thomson Reuters. 'Thomson Reuters' and the Thomson Reuters logo are registered trademarks and trademarks of Thomson Reuters and its affiliated companies.   # noqa: E501

    OpenAPI spec version: 1.2.0
    Contact: Thomson-FCR.PS@Thomsonreuters.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from swagger_client.models.detail_type import DetailType  # noqa: F401,E501


class Detail(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'detail_type': 'DetailType',
        'text': 'str',
        'title': 'str'
    }

    attribute_map = {
        'detail_type': 'detailType',
        'text': 'text',
        'title': 'title'
    }

    def __init__(self, detail_type=None, text=None, title=None):  # noqa: E501
        """Detail - a model defined in Swagger"""  # noqa: E501

        self._detail_type = None
        self._text = None
        self._title = None
        self.discriminator = None

        if detail_type is not None:
            self.detail_type = detail_type
        if text is not None:
            self.text = text
        if title is not None:
            self.title = title

    @property
    def detail_type(self):
        """Gets the detail_type of this Detail.  # noqa: E501


        :return: The detail_type of this Detail.  # noqa: E501
        :rtype: DetailType
        """
        return self._detail_type

    @detail_type.setter
    def detail_type(self, detail_type):
        """Sets the detail_type of this Detail.


        :param detail_type: The detail_type of this Detail.  # noqa: E501
        :type: DetailType
        """

        self._detail_type = detail_type

    @property
    def text(self):
        """Gets the text of this Detail.  # noqa: E501


        :return: The text of this Detail.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this Detail.


        :param text: The text of this Detail.  # noqa: E501
        :type: str
        """

        self._text = text

    @property
    def title(self):
        """Gets the title of this Detail.  # noqa: E501


        :return: The title of this Detail.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Detail.


        :param title: The title of this Detail.  # noqa: E501
        :type: str
        """

        self._title = title

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Detail):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
