def create_demo_response(passfort_data):
    databases = [
        {'name': 'Credit (source #1)', 'type': 'CREDIT'},
        {'name': 'Telco (source #1)', 'type': 'CIVIL'}]

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
        "ADDRESS",
        "DOB",
        "IDENTITY_NUMBER"
    ]
         
    #Get complete name to check what kind of demo response will be returned
    names = passfort_data['input_data']['personal_details']['name']['given_names']
    if passfort_data['input_data']['personal_details']['name'].get('family_name'):
        names.append(passfort_data['input_data']['personal_details']['name']['family_name'])

    #Convert all names in lower case to compare
    names = list(map(lambda x: x.lower(), names))

    if 'fail' in names:
        #all response will fail
        demo_response = {}

    elif '1+1' in names:
        #Mach with one database
        demo_response['electronic_id_check']['matches'].append(
            {
                "database_name": databases[0]['name'],
                "database_type": databases[0]['type'],
                "matched_fields": matched_fields,
                "count": 1
            }
        )

    else:
        #Mach all databases
        for database in databases:
            demo_response['electronic_id_check']['matches'].append(
                {
                    "database_name": database['name'],
                    "database_type": database['type'],
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
        
