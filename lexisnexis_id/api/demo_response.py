def create_demo_response(passfort_data):
    demo_response = {
        "entity_type": "INDIVIDUAL",
        "electronic_id_check": {
            "matches": [

            ]
        }
    }

    matched_fields = [
        "FORENAME",
        "SURNAME",
        "DOB",
        "IDENTITY_NUMBER"
    ]

    # Get complete name to check what kind of demo response will be returned
    names = passfort_data['input_data']['personal_details']['name']['given_names']
    if passfort_data['input_data']['personal_details']['name'].get('family_name'):
        names.append(passfort_data['input_data']['personal_details']['name']['family_name'])

    # Convert all names in lower case to compare
    names = list(map(lambda x: x.lower(), names))

    if 'fail' in names:
        # all response will fail
        demo_response = {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": []
            }
        }
    else:
        matched_fields = ["FORENAME", "SURNAME"]
        if 'partial' in names:
            # Partial match criteria changes based on check config.
            if passfort_data['config']['use_dob']:
                # Matching the unrequired one of SSN/DOB results in a partial
                matched_fields.append("IDENTITY_NUMBER")
            else:
                matched_fields.append("DOB")

        else:
            # Regardless of config, First + Last + DOB + SSN is always a match
            matched_fields.append("DOB")
            matched_fields.append("IDENTITY_NUMBER")

        demo_response['electronic_id_check']['matches'].append(
            {
                "database_name": "LexisNexis DB",
                "database_type": "CIVIL",
                "matched_fields": matched_fields,
                "count": 1
            }
        )

    response = {
        "output_data": demo_response,
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    return response
