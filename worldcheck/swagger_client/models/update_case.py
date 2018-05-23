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

from swagger_client.models.field import Field  # noqa: F401,E501
from swagger_client.models.provider_type import ProviderType  # noqa: F401,E501


class UpdateCase(object):
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
        'case_id': 'str',
        'name': 'str',
        'provider_types': 'list[ProviderType]',
        'custom_fields': 'list[Field]',
        'secondary_fields': 'list[Field]'
    }

    attribute_map = {
        'case_id': 'caseId',
        'name': 'name',
        'provider_types': 'providerTypes',
        'custom_fields': 'customFields',
        'secondary_fields': 'secondaryFields'
    }

    def __init__(self, case_id=None, name=None, provider_types=None, custom_fields=None, secondary_fields=None):  # noqa: E501
        """UpdateCase - a model defined in Swagger"""  # noqa: E501

        self._case_id = None
        self._name = None
        self._provider_types = None
        self._custom_fields = None
        self._secondary_fields = None
        self.discriminator = None

        if case_id is not None:
            self.case_id = case_id
        self.name = name
        self.provider_types = provider_types
        if custom_fields is not None:
            self.custom_fields = custom_fields
        if secondary_fields is not None:
            self.secondary_fields = secondary_fields

    @property
    def case_id(self):
        """Gets the case_id of this UpdateCase.  # noqa: E501

        Case ID provided by the client or else generated by the system for the client  # noqa: E501

        :return: The case_id of this UpdateCase.  # noqa: E501
        :rtype: str
        """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Sets the case_id of this UpdateCase.

        Case ID provided by the client or else generated by the system for the client  # noqa: E501

        :param case_id: The case_id of this UpdateCase.  # noqa: E501
        :type: str
        """
        if case_id is not None and len(case_id) > 1000:
            raise ValueError("Invalid value for `case_id`, length must be less than or equal to `1000`")  # noqa: E501

        self._case_id = case_id

    @property
    def name(self):
        """Gets the name of this UpdateCase.  # noqa: E501

        Name to screen for this case  # noqa: E501

        :return: The name of this UpdateCase.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UpdateCase.

        Name to screen for this case  # noqa: E501

        :param name: The name of this UpdateCase.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if name is not None and len(name) > 1000:
            raise ValueError("Invalid value for `name`, length must be less than or equal to `1000`")  # noqa: E501

        self._name = name

    @property
    def provider_types(self):
        """Gets the provider_types of this UpdateCase.  # noqa: E501

        Provider Types required to Screen this case  # noqa: E501

        :return: The provider_types of this UpdateCase.  # noqa: E501
        :rtype: list[ProviderType]
        """
        return self._provider_types

    @provider_types.setter
    def provider_types(self, provider_types):
        """Sets the provider_types of this UpdateCase.

        Provider Types required to Screen this case  # noqa: E501

        :param provider_types: The provider_types of this UpdateCase.  # noqa: E501
        :type: list[ProviderType]
        """
        if provider_types is None:
            raise ValueError("Invalid value for `provider_types`, must not be `None`")  # noqa: E501

        self._provider_types = provider_types

    @property
    def custom_fields(self):
        """Gets the custom_fields of this UpdateCase.  # noqa: E501

        Case Custom Fields. Available custom fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :return: The custom_fields of this UpdateCase.  # noqa: E501
        :rtype: list[Field]
        """
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, custom_fields):
        """Sets the custom_fields of this UpdateCase.

        Case Custom Fields. Available custom fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :param custom_fields: The custom_fields of this UpdateCase.  # noqa: E501
        :type: list[Field]
        """

        self._custom_fields = custom_fields

    @property
    def secondary_fields(self):
        """Gets the secondary_fields of this UpdateCase.  # noqa: E501

        Case Secondary Fields. Available secondary fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :return: The secondary_fields of this UpdateCase.  # noqa: E501
        :rtype: list[Field]
        """
        return self._secondary_fields

    @secondary_fields.setter
    def secondary_fields(self, secondary_fields):
        """Sets the secondary_fields of this UpdateCase.

        Case Secondary Fields. Available secondary fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :param secondary_fields: The secondary_fields of this UpdateCase.  # noqa: E501
        :type: list[Field]
        """

        self._secondary_fields = secondary_fields

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
        if not isinstance(other, UpdateCase):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
