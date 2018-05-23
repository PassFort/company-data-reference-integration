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

from swagger_client.models.field_definition import FieldDefinition  # noqa: F401,E501
from swagger_client.models.group_screening_type import GroupScreeningType  # noqa: F401,E501
from swagger_client.models.secondary_fields_by_entity import SecondaryFieldsByEntity  # noqa: F401,E501


class CaseTemplateResponse(object):
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
        'group_screening_type': 'GroupScreeningType',
        'group_id': 'str',
        'custom_fields': 'list[FieldDefinition]',
        'secondary_fields_by_provider': 'dict(str, SecondaryFieldsByEntity)'
    }

    attribute_map = {
        'group_screening_type': 'groupScreeningType',
        'group_id': 'groupId',
        'custom_fields': 'customFields',
        'secondary_fields_by_provider': 'secondaryFieldsByProvider'
    }

    def __init__(self, group_screening_type=None, group_id=None, custom_fields=None, secondary_fields_by_provider=None):  # noqa: E501
        """CaseTemplateResponse - a model defined in Swagger"""  # noqa: E501

        self._group_screening_type = None
        self._group_id = None
        self._custom_fields = None
        self._secondary_fields_by_provider = None
        self.discriminator = None

        self.group_screening_type = group_screening_type
        self.group_id = group_id
        if custom_fields is not None:
            self.custom_fields = custom_fields
        if secondary_fields_by_provider is not None:
            self.secondary_fields_by_provider = secondary_fields_by_provider

    @property
    def group_screening_type(self):
        """Gets the group_screening_type of this CaseTemplateResponse.  # noqa: E501


        :return: The group_screening_type of this CaseTemplateResponse.  # noqa: E501
        :rtype: GroupScreeningType
        """
        return self._group_screening_type

    @group_screening_type.setter
    def group_screening_type(self, group_screening_type):
        """Sets the group_screening_type of this CaseTemplateResponse.


        :param group_screening_type: The group_screening_type of this CaseTemplateResponse.  # noqa: E501
        :type: GroupScreeningType
        """
        if group_screening_type is None:
            raise ValueError("Invalid value for `group_screening_type`, must not be `None`")  # noqa: E501

        self._group_screening_type = group_screening_type

    @property
    def group_id(self):
        """Gets the group_id of this CaseTemplateResponse.  # noqa: E501


        :return: The group_id of this CaseTemplateResponse.  # noqa: E501
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """Sets the group_id of this CaseTemplateResponse.


        :param group_id: The group_id of this CaseTemplateResponse.  # noqa: E501
        :type: str
        """
        if group_id is None:
            raise ValueError("Invalid value for `group_id`, must not be `None`")  # noqa: E501

        self._group_id = group_id

    @property
    def custom_fields(self):
        """Gets the custom_fields of this CaseTemplateResponse.  # noqa: E501


        :return: The custom_fields of this CaseTemplateResponse.  # noqa: E501
        :rtype: list[FieldDefinition]
        """
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, custom_fields):
        """Sets the custom_fields of this CaseTemplateResponse.


        :param custom_fields: The custom_fields of this CaseTemplateResponse.  # noqa: E501
        :type: list[FieldDefinition]
        """

        self._custom_fields = custom_fields

    @property
    def secondary_fields_by_provider(self):
        """Gets the secondary_fields_by_provider of this CaseTemplateResponse.  # noqa: E501

        Mapping from ProviderType to SecondaryFieldsByEntity which contains all secondary fields that is available for that ProviderType.   # noqa: E501

        :return: The secondary_fields_by_provider of this CaseTemplateResponse.  # noqa: E501
        :rtype: dict(str, SecondaryFieldsByEntity)
        """
        return self._secondary_fields_by_provider

    @secondary_fields_by_provider.setter
    def secondary_fields_by_provider(self, secondary_fields_by_provider):
        """Sets the secondary_fields_by_provider of this CaseTemplateResponse.

        Mapping from ProviderType to SecondaryFieldsByEntity which contains all secondary fields that is available for that ProviderType.   # noqa: E501

        :param secondary_fields_by_provider: The secondary_fields_by_provider of this CaseTemplateResponse.  # noqa: E501
        :type: dict(str, SecondaryFieldsByEntity)
        """

        self._secondary_fields_by_provider = secondary_fields_by_provider

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
        if not isinstance(other, CaseTemplateResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
