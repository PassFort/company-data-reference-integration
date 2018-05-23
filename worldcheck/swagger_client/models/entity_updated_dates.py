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


class EntityUpdatedDates(object):
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
        'age_updated': 'datetime',
        'aliases_updated': 'datetime',
        'alternative_spelling_updated': 'datetime',
        'as_of_date_updated': 'datetime',
        'category_updated': 'datetime',
        'citizenships_updated': 'datetime',
        'companies_updated': 'datetime',
        'deceased_updated': 'datetime',
        'dobs_updated': 'datetime',
        'ei_updated': 'datetime',
        'entered_updated': 'datetime',
        'external_sources_updated': 'datetime',
        'first_name_updated': 'datetime',
        'foreign_alias_updated': 'datetime',
        'further_information_updated': 'datetime',
        'id_numbers_updated': 'datetime',
        'keywords_updated': 'datetime',
        'last_name_updated': 'datetime',
        'linked_to_updated': 'datetime',
        'locations_updated': 'datetime',
        'low_quality_aliases_updated': 'datetime',
        'passports_updated': 'datetime',
        'place_of_birth_updated': 'datetime',
        'position_updated': 'datetime',
        'ssn_updated': 'datetime',
        'sub_category_updated': 'datetime',
        'title_updated': 'datetime',
        'updatecategory_updated': 'datetime'
    }

    attribute_map = {
        'age_updated': 'ageUpdated',
        'aliases_updated': 'aliasesUpdated',
        'alternative_spelling_updated': 'alternativeSpellingUpdated',
        'as_of_date_updated': 'asOfDateUpdated',
        'category_updated': 'categoryUpdated',
        'citizenships_updated': 'citizenshipsUpdated',
        'companies_updated': 'companiesUpdated',
        'deceased_updated': 'deceasedUpdated',
        'dobs_updated': 'dobsUpdated',
        'ei_updated': 'eiUpdated',
        'entered_updated': 'enteredUpdated',
        'external_sources_updated': 'externalSourcesUpdated',
        'first_name_updated': 'firstNameUpdated',
        'foreign_alias_updated': 'foreignAliasUpdated',
        'further_information_updated': 'furtherInformationUpdated',
        'id_numbers_updated': 'idNumbersUpdated',
        'keywords_updated': 'keywordsUpdated',
        'last_name_updated': 'lastNameUpdated',
        'linked_to_updated': 'linkedToUpdated',
        'locations_updated': 'locationsUpdated',
        'low_quality_aliases_updated': 'lowQualityAliasesUpdated',
        'passports_updated': 'passportsUpdated',
        'place_of_birth_updated': 'placeOfBirthUpdated',
        'position_updated': 'positionUpdated',
        'ssn_updated': 'ssnUpdated',
        'sub_category_updated': 'subCategoryUpdated',
        'title_updated': 'titleUpdated',
        'updatecategory_updated': 'updatecategoryUpdated'
    }

    def __init__(self, age_updated=None, aliases_updated=None, alternative_spelling_updated=None, as_of_date_updated=None, category_updated=None, citizenships_updated=None, companies_updated=None, deceased_updated=None, dobs_updated=None, ei_updated=None, entered_updated=None, external_sources_updated=None, first_name_updated=None, foreign_alias_updated=None, further_information_updated=None, id_numbers_updated=None, keywords_updated=None, last_name_updated=None, linked_to_updated=None, locations_updated=None, low_quality_aliases_updated=None, passports_updated=None, place_of_birth_updated=None, position_updated=None, ssn_updated=None, sub_category_updated=None, title_updated=None, updatecategory_updated=None):  # noqa: E501
        """EntityUpdatedDates - a model defined in Swagger"""  # noqa: E501

        self._age_updated = None
        self._aliases_updated = None
        self._alternative_spelling_updated = None
        self._as_of_date_updated = None
        self._category_updated = None
        self._citizenships_updated = None
        self._companies_updated = None
        self._deceased_updated = None
        self._dobs_updated = None
        self._ei_updated = None
        self._entered_updated = None
        self._external_sources_updated = None
        self._first_name_updated = None
        self._foreign_alias_updated = None
        self._further_information_updated = None
        self._id_numbers_updated = None
        self._keywords_updated = None
        self._last_name_updated = None
        self._linked_to_updated = None
        self._locations_updated = None
        self._low_quality_aliases_updated = None
        self._passports_updated = None
        self._place_of_birth_updated = None
        self._position_updated = None
        self._ssn_updated = None
        self._sub_category_updated = None
        self._title_updated = None
        self._updatecategory_updated = None
        self.discriminator = None

        if age_updated is not None:
            self.age_updated = age_updated
        if aliases_updated is not None:
            self.aliases_updated = aliases_updated
        if alternative_spelling_updated is not None:
            self.alternative_spelling_updated = alternative_spelling_updated
        if as_of_date_updated is not None:
            self.as_of_date_updated = as_of_date_updated
        if category_updated is not None:
            self.category_updated = category_updated
        if citizenships_updated is not None:
            self.citizenships_updated = citizenships_updated
        if companies_updated is not None:
            self.companies_updated = companies_updated
        if deceased_updated is not None:
            self.deceased_updated = deceased_updated
        if dobs_updated is not None:
            self.dobs_updated = dobs_updated
        if ei_updated is not None:
            self.ei_updated = ei_updated
        if entered_updated is not None:
            self.entered_updated = entered_updated
        if external_sources_updated is not None:
            self.external_sources_updated = external_sources_updated
        if first_name_updated is not None:
            self.first_name_updated = first_name_updated
        if foreign_alias_updated is not None:
            self.foreign_alias_updated = foreign_alias_updated
        if further_information_updated is not None:
            self.further_information_updated = further_information_updated
        if id_numbers_updated is not None:
            self.id_numbers_updated = id_numbers_updated
        if keywords_updated is not None:
            self.keywords_updated = keywords_updated
        if last_name_updated is not None:
            self.last_name_updated = last_name_updated
        if linked_to_updated is not None:
            self.linked_to_updated = linked_to_updated
        if locations_updated is not None:
            self.locations_updated = locations_updated
        if low_quality_aliases_updated is not None:
            self.low_quality_aliases_updated = low_quality_aliases_updated
        if passports_updated is not None:
            self.passports_updated = passports_updated
        if place_of_birth_updated is not None:
            self.place_of_birth_updated = place_of_birth_updated
        if position_updated is not None:
            self.position_updated = position_updated
        if ssn_updated is not None:
            self.ssn_updated = ssn_updated
        if sub_category_updated is not None:
            self.sub_category_updated = sub_category_updated
        if title_updated is not None:
            self.title_updated = title_updated
        if updatecategory_updated is not None:
            self.updatecategory_updated = updatecategory_updated

    @property
    def age_updated(self):
        """Gets the age_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The age_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._age_updated

    @age_updated.setter
    def age_updated(self, age_updated):
        """Sets the age_updated of this EntityUpdatedDates.


        :param age_updated: The age_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._age_updated = age_updated

    @property
    def aliases_updated(self):
        """Gets the aliases_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The aliases_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._aliases_updated

    @aliases_updated.setter
    def aliases_updated(self, aliases_updated):
        """Sets the aliases_updated of this EntityUpdatedDates.


        :param aliases_updated: The aliases_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._aliases_updated = aliases_updated

    @property
    def alternative_spelling_updated(self):
        """Gets the alternative_spelling_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The alternative_spelling_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._alternative_spelling_updated

    @alternative_spelling_updated.setter
    def alternative_spelling_updated(self, alternative_spelling_updated):
        """Sets the alternative_spelling_updated of this EntityUpdatedDates.


        :param alternative_spelling_updated: The alternative_spelling_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._alternative_spelling_updated = alternative_spelling_updated

    @property
    def as_of_date_updated(self):
        """Gets the as_of_date_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The as_of_date_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._as_of_date_updated

    @as_of_date_updated.setter
    def as_of_date_updated(self, as_of_date_updated):
        """Sets the as_of_date_updated of this EntityUpdatedDates.


        :param as_of_date_updated: The as_of_date_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._as_of_date_updated = as_of_date_updated

    @property
    def category_updated(self):
        """Gets the category_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The category_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._category_updated

    @category_updated.setter
    def category_updated(self, category_updated):
        """Sets the category_updated of this EntityUpdatedDates.


        :param category_updated: The category_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._category_updated = category_updated

    @property
    def citizenships_updated(self):
        """Gets the citizenships_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The citizenships_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._citizenships_updated

    @citizenships_updated.setter
    def citizenships_updated(self, citizenships_updated):
        """Sets the citizenships_updated of this EntityUpdatedDates.


        :param citizenships_updated: The citizenships_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._citizenships_updated = citizenships_updated

    @property
    def companies_updated(self):
        """Gets the companies_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The companies_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._companies_updated

    @companies_updated.setter
    def companies_updated(self, companies_updated):
        """Sets the companies_updated of this EntityUpdatedDates.


        :param companies_updated: The companies_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._companies_updated = companies_updated

    @property
    def deceased_updated(self):
        """Gets the deceased_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The deceased_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._deceased_updated

    @deceased_updated.setter
    def deceased_updated(self, deceased_updated):
        """Sets the deceased_updated of this EntityUpdatedDates.


        :param deceased_updated: The deceased_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._deceased_updated = deceased_updated

    @property
    def dobs_updated(self):
        """Gets the dobs_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The dobs_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._dobs_updated

    @dobs_updated.setter
    def dobs_updated(self, dobs_updated):
        """Sets the dobs_updated of this EntityUpdatedDates.


        :param dobs_updated: The dobs_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._dobs_updated = dobs_updated

    @property
    def ei_updated(self):
        """Gets the ei_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The ei_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._ei_updated

    @ei_updated.setter
    def ei_updated(self, ei_updated):
        """Sets the ei_updated of this EntityUpdatedDates.


        :param ei_updated: The ei_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._ei_updated = ei_updated

    @property
    def entered_updated(self):
        """Gets the entered_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The entered_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._entered_updated

    @entered_updated.setter
    def entered_updated(self, entered_updated):
        """Sets the entered_updated of this EntityUpdatedDates.


        :param entered_updated: The entered_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._entered_updated = entered_updated

    @property
    def external_sources_updated(self):
        """Gets the external_sources_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The external_sources_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._external_sources_updated

    @external_sources_updated.setter
    def external_sources_updated(self, external_sources_updated):
        """Sets the external_sources_updated of this EntityUpdatedDates.


        :param external_sources_updated: The external_sources_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._external_sources_updated = external_sources_updated

    @property
    def first_name_updated(self):
        """Gets the first_name_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The first_name_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._first_name_updated

    @first_name_updated.setter
    def first_name_updated(self, first_name_updated):
        """Sets the first_name_updated of this EntityUpdatedDates.


        :param first_name_updated: The first_name_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._first_name_updated = first_name_updated

    @property
    def foreign_alias_updated(self):
        """Gets the foreign_alias_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The foreign_alias_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._foreign_alias_updated

    @foreign_alias_updated.setter
    def foreign_alias_updated(self, foreign_alias_updated):
        """Sets the foreign_alias_updated of this EntityUpdatedDates.


        :param foreign_alias_updated: The foreign_alias_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._foreign_alias_updated = foreign_alias_updated

    @property
    def further_information_updated(self):
        """Gets the further_information_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The further_information_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._further_information_updated

    @further_information_updated.setter
    def further_information_updated(self, further_information_updated):
        """Sets the further_information_updated of this EntityUpdatedDates.


        :param further_information_updated: The further_information_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._further_information_updated = further_information_updated

    @property
    def id_numbers_updated(self):
        """Gets the id_numbers_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The id_numbers_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._id_numbers_updated

    @id_numbers_updated.setter
    def id_numbers_updated(self, id_numbers_updated):
        """Sets the id_numbers_updated of this EntityUpdatedDates.


        :param id_numbers_updated: The id_numbers_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._id_numbers_updated = id_numbers_updated

    @property
    def keywords_updated(self):
        """Gets the keywords_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The keywords_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._keywords_updated

    @keywords_updated.setter
    def keywords_updated(self, keywords_updated):
        """Sets the keywords_updated of this EntityUpdatedDates.


        :param keywords_updated: The keywords_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._keywords_updated = keywords_updated

    @property
    def last_name_updated(self):
        """Gets the last_name_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The last_name_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._last_name_updated

    @last_name_updated.setter
    def last_name_updated(self, last_name_updated):
        """Sets the last_name_updated of this EntityUpdatedDates.


        :param last_name_updated: The last_name_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._last_name_updated = last_name_updated

    @property
    def linked_to_updated(self):
        """Gets the linked_to_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The linked_to_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._linked_to_updated

    @linked_to_updated.setter
    def linked_to_updated(self, linked_to_updated):
        """Sets the linked_to_updated of this EntityUpdatedDates.


        :param linked_to_updated: The linked_to_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._linked_to_updated = linked_to_updated

    @property
    def locations_updated(self):
        """Gets the locations_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The locations_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._locations_updated

    @locations_updated.setter
    def locations_updated(self, locations_updated):
        """Sets the locations_updated of this EntityUpdatedDates.


        :param locations_updated: The locations_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._locations_updated = locations_updated

    @property
    def low_quality_aliases_updated(self):
        """Gets the low_quality_aliases_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The low_quality_aliases_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._low_quality_aliases_updated

    @low_quality_aliases_updated.setter
    def low_quality_aliases_updated(self, low_quality_aliases_updated):
        """Sets the low_quality_aliases_updated of this EntityUpdatedDates.


        :param low_quality_aliases_updated: The low_quality_aliases_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._low_quality_aliases_updated = low_quality_aliases_updated

    @property
    def passports_updated(self):
        """Gets the passports_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The passports_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._passports_updated

    @passports_updated.setter
    def passports_updated(self, passports_updated):
        """Sets the passports_updated of this EntityUpdatedDates.


        :param passports_updated: The passports_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._passports_updated = passports_updated

    @property
    def place_of_birth_updated(self):
        """Gets the place_of_birth_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The place_of_birth_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._place_of_birth_updated

    @place_of_birth_updated.setter
    def place_of_birth_updated(self, place_of_birth_updated):
        """Sets the place_of_birth_updated of this EntityUpdatedDates.


        :param place_of_birth_updated: The place_of_birth_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._place_of_birth_updated = place_of_birth_updated

    @property
    def position_updated(self):
        """Gets the position_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The position_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._position_updated

    @position_updated.setter
    def position_updated(self, position_updated):
        """Sets the position_updated of this EntityUpdatedDates.


        :param position_updated: The position_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._position_updated = position_updated

    @property
    def ssn_updated(self):
        """Gets the ssn_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The ssn_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._ssn_updated

    @ssn_updated.setter
    def ssn_updated(self, ssn_updated):
        """Sets the ssn_updated of this EntityUpdatedDates.


        :param ssn_updated: The ssn_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._ssn_updated = ssn_updated

    @property
    def sub_category_updated(self):
        """Gets the sub_category_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The sub_category_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._sub_category_updated

    @sub_category_updated.setter
    def sub_category_updated(self, sub_category_updated):
        """Sets the sub_category_updated of this EntityUpdatedDates.


        :param sub_category_updated: The sub_category_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._sub_category_updated = sub_category_updated

    @property
    def title_updated(self):
        """Gets the title_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The title_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._title_updated

    @title_updated.setter
    def title_updated(self, title_updated):
        """Sets the title_updated of this EntityUpdatedDates.


        :param title_updated: The title_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._title_updated = title_updated

    @property
    def updatecategory_updated(self):
        """Gets the updatecategory_updated of this EntityUpdatedDates.  # noqa: E501


        :return: The updatecategory_updated of this EntityUpdatedDates.  # noqa: E501
        :rtype: datetime
        """
        return self._updatecategory_updated

    @updatecategory_updated.setter
    def updatecategory_updated(self, updatecategory_updated):
        """Sets the updatecategory_updated of this EntityUpdatedDates.


        :param updatecategory_updated: The updatecategory_updated of this EntityUpdatedDates.  # noqa: E501
        :type: datetime
        """

        self._updatecategory_updated = updatecategory_updated

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
        if not isinstance(other, EntityUpdatedDates):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
