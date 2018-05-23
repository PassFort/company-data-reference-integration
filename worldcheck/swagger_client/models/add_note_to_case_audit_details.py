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


class AddNoteToCaseAuditDetails(object):
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
        'case_name': 'str',
        'assignor_name': 'str',
        'assignee_name': 'str',
        'assignee_email': 'str',
        'title': 'str',
        'body': 'str'
    }

    attribute_map = {
        'case_id': 'caseID',
        'case_name': 'caseName',
        'assignor_name': 'assignorName',
        'assignee_name': 'assigneeName',
        'assignee_email': 'assigneeEmail',
        'title': 'title',
        'body': 'body'
    }

    def __init__(self, case_id=None, case_name=None, assignor_name=None, assignee_name=None, assignee_email=None, title=None, body=None):  # noqa: E501
        """AddNoteToCaseAuditDetails - a model defined in Swagger"""  # noqa: E501

        self._case_id = None
        self._case_name = None
        self._assignor_name = None
        self._assignee_name = None
        self._assignee_email = None
        self._title = None
        self._body = None
        self.discriminator = None

        self.case_id = case_id
        self.case_name = case_name
        self.assignor_name = assignor_name
        self.assignee_name = assignee_name
        self.assignee_email = assignee_email
        self.title = title
        self.body = body

    @property
    def case_id(self):
        """Gets the case_id of this AddNoteToCaseAuditDetails.  # noqa: E501

        ID of the case on which the note is set  # noqa: E501

        :return: The case_id of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Sets the case_id of this AddNoteToCaseAuditDetails.

        ID of the case on which the note is set  # noqa: E501

        :param case_id: The case_id of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if case_id is None:
            raise ValueError("Invalid value for `case_id`, must not be `None`")  # noqa: E501

        self._case_id = case_id

    @property
    def case_name(self):
        """Gets the case_name of this AddNoteToCaseAuditDetails.  # noqa: E501

        case name to be screened  # noqa: E501

        :return: The case_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._case_name

    @case_name.setter
    def case_name(self, case_name):
        """Sets the case_name of this AddNoteToCaseAuditDetails.

        case name to be screened  # noqa: E501

        :param case_name: The case_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if case_name is None:
            raise ValueError("Invalid value for `case_name`, must not be `None`")  # noqa: E501

        self._case_name = case_name

    @property
    def assignor_name(self):
        """Gets the assignor_name of this AddNoteToCaseAuditDetails.  # noqa: E501

        assignor's name  # noqa: E501

        :return: The assignor_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._assignor_name

    @assignor_name.setter
    def assignor_name(self, assignor_name):
        """Sets the assignor_name of this AddNoteToCaseAuditDetails.

        assignor's name  # noqa: E501

        :param assignor_name: The assignor_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if assignor_name is None:
            raise ValueError("Invalid value for `assignor_name`, must not be `None`")  # noqa: E501

        self._assignor_name = assignor_name

    @property
    def assignee_name(self):
        """Gets the assignee_name of this AddNoteToCaseAuditDetails.  # noqa: E501

        assignee's name  # noqa: E501

        :return: The assignee_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._assignee_name

    @assignee_name.setter
    def assignee_name(self, assignee_name):
        """Sets the assignee_name of this AddNoteToCaseAuditDetails.

        assignee's name  # noqa: E501

        :param assignee_name: The assignee_name of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if assignee_name is None:
            raise ValueError("Invalid value for `assignee_name`, must not be `None`")  # noqa: E501

        self._assignee_name = assignee_name

    @property
    def assignee_email(self):
        """Gets the assignee_email of this AddNoteToCaseAuditDetails.  # noqa: E501


        :return: The assignee_email of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._assignee_email

    @assignee_email.setter
    def assignee_email(self, assignee_email):
        """Sets the assignee_email of this AddNoteToCaseAuditDetails.


        :param assignee_email: The assignee_email of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if assignee_email is None:
            raise ValueError("Invalid value for `assignee_email`, must not be `None`")  # noqa: E501

        self._assignee_email = assignee_email

    @property
    def title(self):
        """Gets the title of this AddNoteToCaseAuditDetails.  # noqa: E501

        title  # noqa: E501

        :return: The title of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this AddNoteToCaseAuditDetails.

        title  # noqa: E501

        :param title: The title of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def body(self):
        """Gets the body of this AddNoteToCaseAuditDetails.  # noqa: E501

        message body  # noqa: E501

        :return: The body of this AddNoteToCaseAuditDetails.  # noqa: E501
        :rtype: str
        """
        return self._body

    @body.setter
    def body(self, body):
        """Sets the body of this AddNoteToCaseAuditDetails.

        message body  # noqa: E501

        :param body: The body of this AddNoteToCaseAuditDetails.  # noqa: E501
        :type: str
        """
        if body is None:
            raise ValueError("Invalid value for `body`, must not be `None`")  # noqa: E501

        self._body = body

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
        if not isinstance(other, AddNoteToCaseAuditDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
