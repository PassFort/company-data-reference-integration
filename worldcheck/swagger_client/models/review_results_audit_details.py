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

from swagger_client.models.abstract_audit_details import AbstractAuditDetails  # noqa: F401,E501


class ReviewResultsAuditDetails(object):
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
        'result_ids': 'list[str]',
        'remark': 'str'
    }

    attribute_map = {
        'result_ids': 'resultIds',
        'remark': 'remark'
    }

    def __init__(self, result_ids=None, remark=None):  # noqa: E501
        """ReviewResultsAuditDetails - a model defined in Swagger"""  # noqa: E501

        self._result_ids = None
        self._remark = None
        self.discriminator = None

        self.result_ids = result_ids
        self.remark = remark

    @property
    def result_ids(self):
        """Gets the result_ids of this ReviewResultsAuditDetails.  # noqa: E501

        Identifiers of the reviewed results  # noqa: E501

        :return: The result_ids of this ReviewResultsAuditDetails.  # noqa: E501
        :rtype: list[str]
        """
        return self._result_ids

    @result_ids.setter
    def result_ids(self, result_ids):
        """Sets the result_ids of this ReviewResultsAuditDetails.

        Identifiers of the reviewed results  # noqa: E501

        :param result_ids: The result_ids of this ReviewResultsAuditDetails.  # noqa: E501
        :type: list[str]
        """
        if result_ids is None:
            raise ValueError("Invalid value for `result_ids`, must not be `None`")  # noqa: E501

        self._result_ids = result_ids

    @property
    def remark(self):
        """Gets the remark of this ReviewResultsAuditDetails.  # noqa: E501

        Remark describing the review  # noqa: E501

        :return: The remark of this ReviewResultsAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._remark

    @remark.setter
    def remark(self, remark):
        """Sets the remark of this ReviewResultsAuditDetails.

        Remark describing the review  # noqa: E501

        :param remark: The remark of this ReviewResultsAuditDetails.  # noqa: E501
        :type: str
        """
        if remark is None:
            raise ValueError("Invalid value for `remark`, must not be `None`")  # noqa: E501

        self._remark = remark

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
        if not isinstance(other, ReviewResultsAuditDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
