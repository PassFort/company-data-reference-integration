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
        "sanctions": get_sanctions_if_any(entity)
    }

    if entity.entity_type == ProfileEntityType.INDIVIDUAL:
        roles = [{"name": role.title} for role in entity.roles] if entity.roles is not None else []
        result["pep"] = {"v": {"match": bool(len(roles)), "roles": roles}}

    return result


def get_sanctions_if_any(entity: Entity):
    if entity.actions is None:
        return []

    return [
        {
            "v": {
                "type": ProfileActionType.SANCTION,
                "list": a.source.name if a.source is not None else None,
                "name": a.text,
                "issuer": a.title,
                "is_current": True  # just assume for now
            }
        }
        for a in entity.actions if a.action_type == ProfileActionType.SANCTION
    ]
