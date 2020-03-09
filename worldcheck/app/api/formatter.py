import logging
import pycountry
from typing import List, TYPE_CHECKING
from .types import MatchEvent, PEPMatchEvent, SanctionsMatchEvent, ReferMatchEvent

from swagger_client.models import NameType, DetailType, ProfileEntityType, CountryLinkType, EventType

if TYPE_CHECKING:
    from swagger_client.models import Address, Associate, Entity, IndividualEntity, Name, Result, Event


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


def tagged_list(results):
    return [{'v': r} for r in results]


def entity_to_passfort_format(entity: 'Entity'):
    aliases = list(set([get_some_name(a) for a in entity.names if a.type != NameType.PRIMARY])) \
        if entity.names is not None else None
    primary_name = get_primary_name(entity)

    result = {
        "match_id": entity.entity_id,
        "match_name": {"v": primary_name},
        "aliases": tagged_list(aliases),
        "sanctions": tagged_list(get_actions_if_any(entity)),
        "sources": tagged_list(get_sources(entity)),
        "details": get_details(entity)
    }

    roles = None
    if entity.entity_type == ProfileEntityType.INDIVIDUAL:
        result["gender"] = {"v": get_gender_if_any(entity)}
        result["deceased"] = {"v": entity.is_deceased}
        roles = [{"name": role.title} for role in entity.roles] if entity.roles is not None else []

        nationalities = get_country_links_by_type(entity, CountryLinkType.NATIONALITY)
        if len(nationalities) > 0:
            result["match_countries"] = tagged_list(nationalities)

    if entity.entity_type == ProfileEntityType.ORGANISATION:
        countries_of_inc = get_country_links_by_type(entity, CountryLinkType.REGISTEREDIN)
        if len(countries_of_inc) > 0:
            result["match_countries"] = tagged_list(countries_of_inc)

    # Companies can be PEPs in world-check data (if they are State owned entities)
    result["pep"] = {"v": {"match": has_pep_source(entity), "roles": roles}}

    # Add both address locations and country only locations in one place
    all_locations = get_country_locations(entity) + get_address_locations(entity)
    if len(all_locations) > 0:
        result["locations"] = tagged_list(all_locations)

    return result


def entity_to_events(entity: 'Entity')-> List[MatchEvent]:
    events = []
    aliases = list(set([get_some_name(a) for a in entity.names if a.type != NameType.PRIMARY])) \
        if entity.names is not None else None
    primary_name = get_primary_name(entity)

    base_event_data = {
        "match_id": entity.entity_id,
        "match_name": primary_name,
        "match_dates": get_dobs(entity),
        "aliases": aliases,
        "sources": get_sources(entity),
        "details": get_details(entity)
    }

    roles = None
    if entity.entity_type == ProfileEntityType.INDIVIDUAL:
        base_event_data["gender"] = get_gender_if_any(entity)
        base_event_data["deceased"] = entity.is_deceased
        roles = [{"name": role.title} for role in entity.roles] if entity.roles is not None else []

        nationalities = get_country_links_by_type(entity, CountryLinkType.NATIONALITY)
        if len(nationalities) > 0:
            base_event_data["match_countries"] = nationalities

    if entity.entity_type == ProfileEntityType.ORGANISATION:
        countries_of_inc = get_country_links_by_type(entity, CountryLinkType.REGISTEREDIN)
        if len(countries_of_inc) > 0:
            base_event_data["match_countries"] = countries_of_inc

    # Add both address locations and country only locations in one place
    all_locations = get_country_locations(entity) + get_address_locations(entity)
    if len(all_locations) > 0:
        base_event_data["locations"] = all_locations

    # Companies can be PEPs in world-check data (if they are State owned entities)
    is_pep = has_pep_source(entity)
    sanctions_or_other_actions = get_actions_if_any(entity)

    if is_pep:
        pep_event = PEPMatchEvent().import_data({
            "pep": {
                "match": True,
                "roles": roles
            },
            **base_event_data
        })
        events.append(pep_event)

    if sanctions_or_other_actions:
        sanctions_event = SanctionsMatchEvent().import_data({
            "sanctions": sanctions_or_other_actions,
            **base_event_data
        })
        events.append(sanctions_event)

    if len(events) == 0:
        events.append(ReferMatchEvent().import_data(base_event_data))

    return [e.as_validated_json() for e in events]


def associated_entity_to_passfort_format(entity: 'Entity', association: 'Associate'):
    return {
        "name": get_primary_name(entity),
        "association": association,
        "is_pep": has_pep_source(entity),
        "is_sanction": len(get_actions_if_any(entity)) > 0
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


def get_actions_if_any(entity: 'Entity'):
    if entity.actions is None:
        return []

    return [
        {
            "type": a.action_type,
            "list": a.source.name if a.source is not None else None,
            "name": a.text,
            "issuer": a.title,
            "is_current": True  # just assume for now
        }
        for a in entity.actions
    ]


def get_sources(entity: 'Entity'):
    from_weblinks = [
        {
            "name": "Weblink",
            "url": link.uri,
            "description": link.caption
        }
        for link in entity.weblinks
    ] if entity.weblinks is not None else []

    from_sources = [
        {
            "name": source.name,
            "description": source.type and source.type.category and source.type.category.description
        }
        for source in entity.sources
    ] if entity.sources is not None else []

    return from_weblinks + from_sources


def format_date(event: 'Event'):
    format_str = '%Y'
    date_str = f'{event.year:04}'
    if event.month:
        format_str += '-%m'
        date_str += f'-{event.month:02}'
        if event.day:
            format_str += '-%d'
            date_str += f'-{event.day:02}'
    return {
        'date': date_str,
        'format': format_str,
    }


def get_dobs(entity: 'Entity'):
    return [
        format_date(event)
        for event in (entity.events or [])
        if event.type == EventType.BIRTH
    ]


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
    result = []
    for country_link in entity.country_links:
        if country_link.type == country_type and country_link.country is not None:
            country_code = get_valid_country_code(country_link.country.code)
            if country_code is not None:
                result.append(country_code)
    return result


def get_country_locations(entity: 'Entity'):
    if entity.country_links is None:
        return []

    return [
        {
            "type": country_link.type,
            "country": get_valid_country_code(country_link.country.code)
        }
        for country_link in entity.country_links
        if country_link.type not in [CountryLinkType.NATIONALITY, CountryLinkType.REGISTEREDIN]
        and country_link.country is not None
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
            "type": "ADDRESS",
            "country": get_valid_country_code(address.country.code) if address.country is not None else None,
            "city": address.city,
            "address": one_liner_address(address)
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
