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
from swagger_client.models.provider_type import ProviderType  # noqa: F401,E501


class ScreenCaseAuditDetails(object):
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
        'user_id': 'str',
        'case_system_id': 'str',
        'status_code': 'str',
        'screening_state': 'str',
        'no_of_new_results': 'int',
        'no_of_review_required_results': 'int',
        'no_of_excluded_results': 'int',
        'no_of_auto_resolved_results': 'int',
        'provider_types': 'list[ProviderType]'
    }

    attribute_map = {
        'user_id': 'userId',
        'case_system_id': 'caseSystemId',
        'status_code': 'statusCode',
        'screening_state': 'screeningState',
        'no_of_new_results': 'noOfNewResults',
        'no_of_review_required_results': 'noOfReviewRequiredResults',
        'no_of_excluded_results': 'noOfExcludedResults',
        'no_of_auto_resolved_results': 'noOfAutoResolvedResults',
        'provider_types': 'providerTypes'
    }

    def __init__(self, user_id=None, case_system_id=None, status_code=None, screening_state=None, no_of_new_results=None, no_of_review_required_results=None, no_of_excluded_results=None, no_of_auto_resolved_results=None, provider_types=None):  # noqa: E501
        """ScreenCaseAuditDetails - a model defined in Swagger"""  # noqa: E501

        self._user_id = None
        self._case_system_id = None
        self._status_code = None
        self._screening_state = None
        self._no_of_new_results = None
        self._no_of_review_required_results = None
        self._no_of_excluded_results = None
        self._no_of_auto_resolved_results = None
        self._provider_types = None
        self.discriminator = None

        self.user_id = user_id
        self.case_system_id = case_system_id
        self.status_code = status_code
        self.screening_state = screening_state
        self.no_of_new_results = no_of_new_results
        self.no_of_review_required_results = no_of_review_required_results
        self.no_of_excluded_results = no_of_excluded_results
        self.no_of_auto_resolved_results = no_of_auto_resolved_results
        self.provider_types = provider_types

    @property
    def user_id(self):
        """Gets the user_id of this ScreenCaseAuditDetails.  # noqa: E501

        Identifier of the user who screened the case  # noqa: E501

        :return: The user_id of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """Sets the user_id of this ScreenCaseAuditDetails.

        Identifier of the user who screened the case  # noqa: E501

        :param user_id: The user_id of this ScreenCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if user_id is None:
            raise ValueError("Invalid value for `user_id`, must not be `None`")  # noqa: E501
        if user_id is not None and len(user_id) > 255:
            raise ValueError("Invalid value for `user_id`, length must be less than or equal to `255`")  # noqa: E501

        self._user_id = user_id

    @property
    def case_system_id(self):
        """Gets the case_system_id of this ScreenCaseAuditDetails.  # noqa: E501

        System generated ID for the Case  # noqa: E501

        :return: The case_system_id of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._case_system_id

    @case_system_id.setter
    def case_system_id(self, case_system_id):
        """Sets the case_system_id of this ScreenCaseAuditDetails.

        System generated ID for the Case  # noqa: E501

        :param case_system_id: The case_system_id of this ScreenCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if case_system_id is None:
            raise ValueError("Invalid value for `case_system_id`, must not be `None`")  # noqa: E501
        if case_system_id is not None and len(case_system_id) > 255:
            raise ValueError("Invalid value for `case_system_id`, length must be less than or equal to `255`")  # noqa: E501

        self._case_system_id = case_system_id

    @property
    def status_code(self):
        """Gets the status_code of this ScreenCaseAuditDetails.  # noqa: E501

        Status code of the screening operation (ie COMPLETED)  # noqa: E501

        :return: The status_code of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """Sets the status_code of this ScreenCaseAuditDetails.

        Status code of the screening operation (ie COMPLETED)  # noqa: E501

        :param status_code: The status_code of this ScreenCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if status_code is None:
            raise ValueError("Invalid value for `status_code`, must not be `None`")  # noqa: E501

        self._status_code = status_code

    @property
    def screening_state(self):
        """Gets the screening_state of this ScreenCaseAuditDetails.  # noqa: E501

        Screening state (ie ANONYMOUS, INITIAL, ONGOING)  # noqa: E501

        :return: The screening_state of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._screening_state

    @screening_state.setter
    def screening_state(self, screening_state):
        """Sets the screening_state of this ScreenCaseAuditDetails.

        Screening state (ie ANONYMOUS, INITIAL, ONGOING)  # noqa: E501

        :param screening_state: The screening_state of this ScreenCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if screening_state is None:
            raise ValueError("Invalid value for `screening_state`, must not be `None`")  # noqa: E501

        self._screening_state = screening_state

    @property
    def no_of_new_results(self):
        """Gets the no_of_new_results of this ScreenCaseAuditDetails.  # noqa: E501

        Number of new results added after the screening run  # noqa: E501

        :return: The no_of_new_results of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: int
        """
        return self._no_of_new_results

    @no_of_new_results.setter
    def no_of_new_results(self, no_of_new_results):
        """Sets the no_of_new_results of this ScreenCaseAuditDetails.

        Number of new results added after the screening run  # noqa: E501

        :param no_of_new_results: The no_of_new_results of this ScreenCaseAuditDetails.  # noqa: E501
        :type: int
        """
        if no_of_new_results is None:
            raise ValueError("Invalid value for `no_of_new_results`, must not be `None`")  # noqa: E501

        self._no_of_new_results = no_of_new_results

    @property
    def no_of_review_required_results(self):
        """Gets the no_of_review_required_results of this ScreenCaseAuditDetails.  # noqa: E501

        Number of screening Results requiring a review  # noqa: E501

        :return: The no_of_review_required_results of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: int
        """
        return self._no_of_review_required_results

    @no_of_review_required_results.setter
    def no_of_review_required_results(self, no_of_review_required_results):
        """Sets the no_of_review_required_results of this ScreenCaseAuditDetails.

        Number of screening Results requiring a review  # noqa: E501

        :param no_of_review_required_results: The no_of_review_required_results of this ScreenCaseAuditDetails.  # noqa: E501
        :type: int
        """
        if no_of_review_required_results is None:
            raise ValueError("Invalid value for `no_of_review_required_results`, must not be `None`")  # noqa: E501

        self._no_of_review_required_results = no_of_review_required_results

    @property
    def no_of_excluded_results(self):
        """Gets the no_of_excluded_results of this ScreenCaseAuditDetails.  # noqa: E501

        Number of results have been excluded from the result set due to auto resolution rules  # noqa: E501

        :return: The no_of_excluded_results of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: int
        """
        return self._no_of_excluded_results

    @no_of_excluded_results.setter
    def no_of_excluded_results(self, no_of_excluded_results):
        """Sets the no_of_excluded_results of this ScreenCaseAuditDetails.

        Number of results have been excluded from the result set due to auto resolution rules  # noqa: E501

        :param no_of_excluded_results: The no_of_excluded_results of this ScreenCaseAuditDetails.  # noqa: E501
        :type: int
        """
        if no_of_excluded_results is None:
            raise ValueError("Invalid value for `no_of_excluded_results`, must not be `None`")  # noqa: E501

        self._no_of_excluded_results = no_of_excluded_results

    @property
    def no_of_auto_resolved_results(self):
        """Gets the no_of_auto_resolved_results of this ScreenCaseAuditDetails.  # noqa: E501

        Number of results have been auto resolved as False set due to auto resolution rules  # noqa: E501

        :return: The no_of_auto_resolved_results of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: int
        """
        return self._no_of_auto_resolved_results

    @no_of_auto_resolved_results.setter
    def no_of_auto_resolved_results(self, no_of_auto_resolved_results):
        """Sets the no_of_auto_resolved_results of this ScreenCaseAuditDetails.

        Number of results have been auto resolved as False set due to auto resolution rules  # noqa: E501

        :param no_of_auto_resolved_results: The no_of_auto_resolved_results of this ScreenCaseAuditDetails.  # noqa: E501
        :type: int
        """
        if no_of_auto_resolved_results is None:
            raise ValueError("Invalid value for `no_of_auto_resolved_results`, must not be `None`")  # noqa: E501

        self._no_of_auto_resolved_results = no_of_auto_resolved_results

    @property
    def provider_types(self):
        """Gets the provider_types of this ScreenCaseAuditDetails.  # noqa: E501

        Array of provider types used in screening  # noqa: E501

        :return: The provider_types of this ScreenCaseAuditDetails.  # noqa: E501
        :rtype: list[ProviderType]
        """
        return self._provider_types

    @provider_types.setter
    def provider_types(self, provider_types):
        """Sets the provider_types of this ScreenCaseAuditDetails.

        Array of provider types used in screening  # noqa: E501

        :param provider_types: The provider_types of this ScreenCaseAuditDetails.  # noqa: E501
        :type: list[ProviderType]
        """
        if provider_types is None:
            raise ValueError("Invalid value for `provider_types`, must not be `None`")  # noqa: E501

        self._provider_types = provider_types

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
        if not isinstance(other, ScreenCaseAuditDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
