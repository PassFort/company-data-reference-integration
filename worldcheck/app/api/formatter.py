from swagger_client.models import Result, Entity, Name, NameType, ProfileActionType, ProfileEntityType


def get_some_name(n: Name):
    if n is None:
        return None

    if n.full_name:
        return n.full_name

    return (n.last_name or "") + ", " + (n.given_name or "")


def result_to_passfort_format(result: Result):

    return {
        "match_id": result.reference_id
    }


def entity_to_passfort_format(entity: Entity):

    aliases = list(set([get_some_name(a) for a in entity.names if a.type != NameType.PRIMARY])) \
        if entity.names is not None else None
    primary_name = next((get_some_name(n) for n in entity.names if n.type == NameType.PRIMARY),
                        None) if entity.names is not None else None

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
        roles = [{"name": role.title} for role in entity.roles] if entity.roles is not None else []

    # Companies can be PEPs in world-check data (if they are State owned entities
    result["pep"] = {"v": {"match": has_pep_source(entity), "roles": roles}}

    return result


def has_pep_source(entity: Entity):
    return len(
        list(filter(
            lambda s: s.type and s.type.category and s.type.category.name == "PEP",
            entity.sources or [])
        )) > 0


def get_sanctions_if_any(entity: Entity):
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


def get_sources(entity: Entity):
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


def get_details(entity: Entity):
    if entity.details is None:
        return []
    return [
        {
            "title": detail.title or detail.detail_type or "?",
            "text": detail.text or "?"
        }
        for detail in entity.details
    ]
