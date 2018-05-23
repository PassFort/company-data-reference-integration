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

from swagger_client.models.case_entity_type import CaseEntityType  # noqa: F401,E501
from swagger_client.models.case_screening_state import CaseScreeningState  # noqa: F401,E501
from swagger_client.models.field import Field  # noqa: F401,E501
from swagger_client.models.lifecycle_state import LifecycleState  # noqa: F401,E501
from swagger_client.models.new_case import NewCase  # noqa: F401,E501
from swagger_client.models.provider_type import ProviderType  # noqa: F401,E501
from swagger_client.models.user_summary import UserSummary  # noqa: F401,E501


class Case(object):
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
        'secondary_fields': 'list[Field]',
        'group_id': 'str',
        'entity_type': 'CaseEntityType',
        'case_system_id': 'str',
        'case_screening_state': 'CaseScreeningState',
        'lifecycle_state': 'LifecycleState',
        'creator': 'UserSummary',
        'modifier': 'UserSummary',
        'creation_date': 'datetime',
        'modification_date': 'datetime',
        'outstanding_actions': 'bool'
    }

    attribute_map = {
        'case_id': 'caseId',
        'name': 'name',
        'provider_types': 'providerTypes',
        'custom_fields': 'customFields',
        'secondary_fields': 'secondaryFields',
        'group_id': 'groupId',
        'entity_type': 'entityType',
        'case_system_id': 'caseSystemId',
        'case_screening_state': 'caseScreeningState',
        'lifecycle_state': 'lifecycleState',
        'creator': 'creator',
        'modifier': 'modifier',
        'creation_date': 'creationDate',
        'modification_date': 'modificationDate',
        'outstanding_actions': 'outstandingActions'
    }

    def __init__(self, case_id=None, name=None, provider_types=None, custom_fields=None, secondary_fields=None, group_id=None, entity_type=None, case_system_id=None, case_screening_state=None, lifecycle_state=None, creator=None, modifier=None, creation_date=None, modification_date=None, outstanding_actions=None):  # noqa: E501
        """Case - a model defined in Swagger"""  # noqa: E501

        self._case_id = None
        self._name = None
        self._provider_types = None
        self._custom_fields = None
        self._secondary_fields = None
        self._group_id = None
        self._entity_type = None
        self._case_system_id = None
        self._case_screening_state = None
        self._lifecycle_state = None
        self._creator = None
        self._modifier = None
        self._creation_date = None
        self._modification_date = None
        self._outstanding_actions = None
        self.discriminator = None

        if case_id is not None:
            self.case_id = case_id
        self.name = name
        self.provider_types = provider_types
        if custom_fields is not None:
            self.custom_fields = custom_fields
        if secondary_fields is not None:
            self.secondary_fields = secondary_fields
        self.group_id = group_id
        self.entity_type = entity_type
        if case_system_id is not None:
            self.case_system_id = case_system_id
        if case_screening_state is not None:
            self.case_screening_state = case_screening_state
        if lifecycle_state is not None:
            self.lifecycle_state = lifecycle_state
        if creator is not None:
            self.creator = creator
        if modifier is not None:
            self.modifier = modifier
        if creation_date is not None:
            self.creation_date = creation_date
        if modification_date is not None:
            self.modification_date = modification_date
        if outstanding_actions is not None:
            self.outstanding_actions = outstanding_actions

    @property
    def case_id(self):
        """Gets the case_id of this Case.  # noqa: E501

        Case ID provided by the client or else generated by the system for the client  # noqa: E501

        :return: The case_id of this Case.  # noqa: E501
        :rtype: str
        """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Sets the case_id of this Case.

        Case ID provided by the client or else generated by the system for the client  # noqa: E501

        :param case_id: The case_id of this Case.  # noqa: E501
        :type: str
        """
        if case_id is not None and len(case_id) > 1000:
            raise ValueError("Invalid value for `case_id`, length must be less than or equal to `1000`")  # noqa: E501

        self._case_id = case_id

    @property
    def name(self):
        """Gets the name of this Case.  # noqa: E501

        Name to screen for this case  # noqa: E501

        :return: The name of this Case.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Case.

        Name to screen for this case  # noqa: E501

        :param name: The name of this Case.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if name is not None and len(name) > 1000:
            raise ValueError("Invalid value for `name`, length must be less than or equal to `1000`")  # noqa: E501

        self._name = name

    @property
    def provider_types(self):
        """Gets the provider_types of this Case.  # noqa: E501

        Provider Types required to Screen this case  # noqa: E501

        :return: The provider_types of this Case.  # noqa: E501
        :rtype: list[ProviderType]
        """
        return self._provider_types

    @provider_types.setter
    def provider_types(self, provider_types):
        """Sets the provider_types of this Case.

        Provider Types required to Screen this case  # noqa: E501

        :param provider_types: The provider_types of this Case.  # noqa: E501
        :type: list[ProviderType]
        """
        if provider_types is None:
            raise ValueError("Invalid value for `provider_types`, must not be `None`")  # noqa: E501

        self._provider_types = provider_types

    @property
    def custom_fields(self):
        """Gets the custom_fields of this Case.  # noqa: E501

        Case Custom Fields. Available custom fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :return: The custom_fields of this Case.  # noqa: E501
        :rtype: list[Field]
        """
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, custom_fields):
        """Sets the custom_fields of this Case.

        Case Custom Fields. Available custom fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :param custom_fields: The custom_fields of this Case.  # noqa: E501
        :type: list[Field]
        """

        self._custom_fields = custom_fields

    @property
    def secondary_fields(self):
        """Gets the secondary_fields of this Case.  # noqa: E501

        Case Secondary Fields. Available secondary fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :return: The secondary_fields of this Case.  # noqa: E501
        :rtype: list[Field]
        """
        return self._secondary_fields

    @secondary_fields.setter
    def secondary_fields(self, secondary_fields):
        """Sets the secondary_fields of this Case.

        Case Secondary Fields. Available secondary fields and their definitions can be obtained via `groups/{groupId}/caseTemplate`.   # noqa: E501

        :param secondary_fields: The secondary_fields of this Case.  # noqa: E501
        :type: list[Field]
        """

        self._secondary_fields = secondary_fields

    @property
    def group_id(self):
        """Gets the group_id of this Case.  # noqa: E501

        Group identifier owning this case  # noqa: E501

        :return: The group_id of this Case.  # noqa: E501
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """Sets the group_id of this Case.

        Group identifier owning this case  # noqa: E501

        :param group_id: The group_id of this Case.  # noqa: E501
        :type: str
        """
        if group_id is None:
            raise ValueError("Invalid value for `group_id`, must not be `None`")  # noqa: E501
        if group_id is not None and len(group_id) > 255:
            raise ValueError("Invalid value for `group_id`, length must be less than or equal to `255`")  # noqa: E501

        self._group_id = group_id

    @property
    def entity_type(self):
        """Gets the entity_type of this Case.  # noqa: E501


        :return: The entity_type of this Case.  # noqa: E501
        :rtype: CaseEntityType
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """Sets the entity_type of this Case.


        :param entity_type: The entity_type of this Case.  # noqa: E501
        :type: CaseEntityType
        """
        if entity_type is None:
            raise ValueError("Invalid value for `entity_type`, must not be `None`")  # noqa: E501

        self._entity_type = entity_type

    @property
    def case_system_id(self):
        """Gets the case_system_id of this Case.  # noqa: E501

        System generated ID for the Case  # noqa: E501

        :return: The case_system_id of this Case.  # noqa: E501
        :rtype: str
        """
        return self._case_system_id

    @case_system_id.setter
    def case_system_id(self, case_system_id):
        """Sets the case_system_id of this Case.

        System generated ID for the Case  # noqa: E501

        :param case_system_id: The case_system_id of this Case.  # noqa: E501
        :type: str
        """
        if case_system_id is not None and len(case_system_id) > 1000:
            raise ValueError("Invalid value for `case_system_id`, length must be less than or equal to `1000`")  # noqa: E501

        self._case_system_id = case_system_id

    @property
    def case_screening_state(self):
        """Gets the case_screening_state of this Case.  # noqa: E501


        :return: The case_screening_state of this Case.  # noqa: E501
        :rtype: CaseScreeningState
        """
        return self._case_screening_state

    @case_screening_state.setter
    def case_screening_state(self, case_screening_state):
        """Sets the case_screening_state of this Case.


        :param case_screening_state: The case_screening_state of this Case.  # noqa: E501
        :type: CaseScreeningState
        """

        self._case_screening_state = case_screening_state

    @property
    def lifecycle_state(self):
        """Gets the lifecycle_state of this Case.  # noqa: E501


        :return: The lifecycle_state of this Case.  # noqa: E501
        :rtype: LifecycleState
        """
        return self._lifecycle_state

    @lifecycle_state.setter
    def lifecycle_state(self, lifecycle_state):
        """Sets the lifecycle_state of this Case.


        :param lifecycle_state: The lifecycle_state of this Case.  # noqa: E501
        :type: LifecycleState
        """

        self._lifecycle_state = lifecycle_state

    @property
    def creator(self):
        """Gets the creator of this Case.  # noqa: E501


        :return: The creator of this Case.  # noqa: E501
        :rtype: UserSummary
        """
        return self._creator

    @creator.setter
    def creator(self, creator):
        """Sets the creator of this Case.


        :param creator: The creator of this Case.  # noqa: E501
        :type: UserSummary
        """

        self._creator = creator

    @property
    def modifier(self):
        """Gets the modifier of this Case.  # noqa: E501


        :return: The modifier of this Case.  # noqa: E501
        :rtype: UserSummary
        """
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        """Sets the modifier of this Case.


        :param modifier: The modifier of this Case.  # noqa: E501
        :type: UserSummary
        """

        self._modifier = modifier

    @property
    def creation_date(self):
        """Gets the creation_date of this Case.  # noqa: E501

        Case creation date and time  # noqa: E501

        :return: The creation_date of this Case.  # noqa: E501
        :rtype: datetime
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this Case.

        Case creation date and time  # noqa: E501

        :param creation_date: The creation_date of this Case.  # noqa: E501
        :type: datetime
        """

        self._creation_date = creation_date

    @property
    def modification_date(self):
        """Gets the modification_date of this Case.  # noqa: E501

        Case modification date and time  # noqa: E501

        :return: The modification_date of this Case.  # noqa: E501
        :rtype: datetime
        """
        return self._modification_date

    @modification_date.setter
    def modification_date(self, modification_date):
        """Sets the modification_date of this Case.

        Case modification date and time  # noqa: E501

        :param modification_date: The modification_date of this Case.  # noqa: E501
        :type: datetime
        """

        self._modification_date = modification_date

    @property
    def outstanding_actions(self):
        """Gets the outstanding_actions of this Case.  # noqa: E501

        Flag indicating outstanding actions on a Case  # noqa: E501

        :return: The outstanding_actions of this Case.  # noqa: E501
        :rtype: bool
        """
        return self._outstanding_actions

    @outstanding_actions.setter
    def outstanding_actions(self, outstanding_actions):
        """Sets the outstanding_actions of this Case.

        Flag indicating outstanding actions on a Case  # noqa: E501

        :param outstanding_actions: The outstanding_actions of this Case.  # noqa: E501
        :type: bool
        """

        self._outstanding_actions = outstanding_actions

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
        if not isinstance(other, Case):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
