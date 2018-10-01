import logging
import pycountry
import typing

from swagger_client.models import NameType, DetailType, ProfileEntityType, CountryLinkType

if typing.TYPE_CHECKING:
    from swagger_client.models import Address, Associate, Entity, IndividualEntity, Name, Result


def get_some_name(n: 'Name'):
    if n is None:
        return None

    if n.full_name:
        return n.full_name

    return (n.last_name or "") + ", " + (n.given_name or "")


def result_to_passfort_format(result: 'Result'):

    return {
        "match_id": result.reference_id
    }


def entity_to_passfort_format(entity: 'Entity'):

    aliases = list(set([get_some_name(a) for a in entity.names if a.type != NameType.PRIMARY])) \
        if entity.names is not None else None
    primary_name = get_primary_name(entity)

    result = {
        "match_id": entity.entity_id,
        "match_name": {"v": primary_name},
        "aliases": [{"v": a} for a in aliases],
        "sanctions": get_sanctions_if_any(entity),
        "sources": get_sources(entity),
        "details": get_details(entity)
    }

    roles = None
    if entity.entity_type == ProfileEntityType.INDIVIDUAL:
        result["gender"] = {"v": get_gender_if_any(entity)}
        result["deceased"] = {"v": entity.is_deceased}
        roles = [{"name": role.title} for role in entity.roles] if entity.roles is not None else []

        nationalities = get_country_links_by_type(entity, CountryLinkType.NATIONALITY)
        if len(nationalities) > 0:
            result["match_countries"] = nationalities

    if entity.entity_type == ProfileEntityType.ORGANISATION:
        countries_of_inc = get_country_links_by_type(entity, CountryLinkType.REGISTEREDIN)
        if len(countries_of_inc) > 0:
            result["match_countries"] = countries_of_inc

    # Companies can be PEPs in world-check data (if they are State owned entities)
    result["pep"] = {"v": {"match": has_pep_source(entity), "roles": roles}}

    # Add both address locations and country only locations in one place
    all_locations = get_country_locations(entity) + get_address_locations(entity)
    if len(all_locations) > 0:
        result["locations"] = all_locations

    return result


def associated_entity_to_passfort_format(entity: 'Entity', association: 'Associate'):
    return {
        "name": get_primary_name(entity),
        "association": association.type,
        "is_pep": has_pep_source(entity),
        "is_sanction": len(get_sanctions_if_any(entity)) > 0
    }


def get_primary_name(entity: 'Entity'):
    return next((get_some_name(n) for n in entity.names if n.type == NameType.PRIMARY),
                None) if entity.names is not None else None


def has_pep_source(entity: 'Entity'):
    return next((True for s in entity.sources or [] if s.type and s.type.category and s.type.category.name == "PEP"),
                False)


def get_gender_if_any(entity: 'IndividualEntity'):
    from swagger_client.models.gender import Gender
    if entity.gender == Gender.MALE:
        return "M"
    if entity.gender == Gender.FEMALE:
        return "F"
    return None


def get_sanctions_if_any(entity: 'Entity'):
    if entity.actions is None:
        return []

    return [
        {
            "v": {
                "type": a.action_type,
                "list": a.source.name if a.source is not None else None,
                "name": a.text,
                "issuer": a.title,
                "is_current": True  # just assume for now
            }
        }
        for a in entity.actions
    ]


def get_sources(entity: 'Entity'):
    from_weblinks = [
        {
            "v": {
                "name": "Weblink",
                "url": link.uri,
                "description": link.caption
            }
        }
        for link in entity.weblinks
    ] if entity.weblinks is not None else []

    from_sources = [
        {
            "v": {
                "name": source.name,
                "description": source.type and source.type.category and source.type.category.description
            }
        }
        for source in entity.sources
    ] if entity.sources is not None else []

    return from_weblinks + from_sources


def get_details(entity: 'Entity'):
    if entity.details is None:
        return []
    return [
        {
            "title": detail.title or detail.detail_type or "?",
            "text": detail.text or "?"
        }
        for detail in entity.details
        if detail.detail_type != DetailType.SANCTION
    ]


def get_country_links_by_type(entity: 'Entity', country_type: 'CountryLinkType'):
    if entity.country_links is None:
        return []

    return [{"v": get_valid_country_code(country_link.country.code)}
            for country_link in entity.country_links
            if country_link.type == country_type and country_link.country is not None]


def get_country_locations(entity: 'Entity'):
    if entity.country_links is None:
        return []

    return [
        {
            "v": {
                "type": country_link.type,
                "country": get_valid_country_code(country_link.country.code)
            }
            for country_link in entity.country_links
            if country_link.type not in [CountryLinkType.NATIONALITY, CountryLinkType.REGISTEREDIN]
            and country_link.country is not None
        }
    ]


def one_liner_address(address: 'Address'):
    non_null_parts = [part
                      for part in [address.street, address.region, address.post_code]
                      if part is not None]
    if len(non_null_parts) == 0:
        return None

    return ', '.join(non_null_parts)


def get_address_locations(entity: 'Entity'):
    if entity.addresses is None:
        return []

    return [
        {
            "v": {
                "type": "ADDRESS",
                "country": get_valid_country_code(address.country.code) if address.country is not None else None,
                "city": address.city,
                "address": one_liner_address(address)
            }
        }
        for address in entity.addresses
    ]


def get_valid_country_code(code):
    if code is None:
        return None

    try:
        pycountry.countries.get(alpha_3=code)
    except KeyError:
        # WorldCheck returns 'ZZZ' as country code sometimes
        logging.info(f'Unsupported country code: {code}')
        return None

    return code
