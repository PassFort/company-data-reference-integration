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

from swagger_client.models.resolution_status_type import ResolutionStatusType  # noqa: F401,E501


class ResolutionField(object):
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
        'id': 'str',
        'label': 'str',
        'type': 'ResolutionStatusType'
    }

    attribute_map = {
        'id': 'id',
        'label': 'label',
        'type': 'type'
    }

    def __init__(self, id=None, label=None, type=None):  # noqa: E501
        """ResolutionField - a model defined in Swagger"""  # noqa: E501

        self._id = None
        self._label = None
        self._type = None
        self.discriminator = None

        self.id = id
        self.label = label
        if type is not None:
            self.type = type

    @property
    def id(self):
        """Gets the id of this ResolutionField.  # noqa: E501

        The ID for the resolution label  # noqa: E501

        :return: The id of this ResolutionField.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ResolutionField.

        The ID for the resolution label  # noqa: E501

        :param id: The id of this ResolutionField.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def label(self):
        """Gets the label of this ResolutionField.  # noqa: E501

        The label for the resolution label  # noqa: E501

        :return: The label of this ResolutionField.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this ResolutionField.

        The label for the resolution label  # noqa: E501

        :param label: The label of this ResolutionField.  # noqa: E501
        :type: str
        """
        if label is None:
            raise ValueError("Invalid value for `label`, must not be `None`")  # noqa: E501

        self._label = label

    @property
    def type(self):
        """Gets the type of this ResolutionField.  # noqa: E501


        :return: The type of this ResolutionField.  # noqa: E501
        :rtype: ResolutionStatusType
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ResolutionField.


        :param type: The type of this ResolutionField.  # noqa: E501
        :type: ResolutionStatusType
        """

        self._type = type

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
        if not isinstance(other, ResolutionField):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
