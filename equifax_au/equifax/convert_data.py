import uuid
from collections import OrderedDict

from lxml.builder import E
import xmltodict
from equifax.soap_builder import EnvelopeBuilder


DATASOUCES = {
    'AEC-ER-0049':'Australian Electoral Roll (v3)',
    'MIRUS-HER-0057':'Australian Electoral Roll Historical (v3)',
    'BDM-BCVS-0003':'BDM - Birth Certificate (v1)',
    'BDM-BCVS-129':'BDM - Birth Certificate (DVS)',
    'BDM-MCVS-0004':'BDM - Marriage Certificate (v1)',
    'BDM-MCVS-0130':'BDM - Marriage Certificate (DVS)',
    'BDM-CON-0128':'BDM - Change of Name Certificate (DVS)',
    'CITIZEN-DOC-0082 ':'Citizenship Certificate (DVS)',
    'DIAC-RBD-0127':'Registration by Descent Certificate (DVS)',
    'VEDA-CBCOMM-0051':'Credit Bureau Commercial (v3)',
    'VEDA-CBCOMM-0059':'Credit Bureau Commercial (v3.1)',
    'VEDA-CBCOMM-0067':'Credit Bureau Commercial (v3.2)',
    'VEDA-CBCONS-0050':'Credit Bureau Consumer (v3)',
    'VEDA-CBCONS-0058':'Credit Bureau Consumer (v3.1)',
    'VEDA-CBCONS-0066':'Credit Bureau Consumer (v3.2)',
    'VEDA-CBPR-0052':'Credit Bureau Public (v3)',
    'VEDA-CBPR-0060':'Credit Bureau Public (v3.1)',
    'VEDA-CBPR-0068':'Credit Bureau Public (v3.2)',
    'ACT-DL-0072':'Drivers Licence - ACT (DVS)',
    'ACT-DL-0001':'Drivers Licence - ACT (v1)',
    'NSW-DL-0071':'Drivers Licence - NSW (DVS)',
    'NSW-DL-0008':'Drivers Licence - NSW (v1)',
    'NT-DL-0077':'Drivers Licence - NT (v1)',
    'QLD-DL-0075':'Drivers Licence - QLT (DVS)',
    'QLD-DL-0010':'Drivers Licence - QLT (v1)',
    'SA-DL-0076':'Drivers Licence - SA (DVS)',
    'TAS-DL-0074':'Drivers Licence - TAS (DVS)',
    'VIC-DL-0073':'Drivers Licence - VIC (DVS)',
    'VIC-DL-0020':'Drivers Licence - VIC (v1)',
    'WA-DL-0078':'Drivers Licence - WA(DVS)',
    'WA-DL-0039':'Drivers Licence - WA(v1)',
    'ACC-PEPS-0124':'GlobalScreening - PEPs (Custom)',
    'ACC-PEPS-0048':'GlobalScreening - PEPs (Domestic)',
    'ACC-PEPS-0098':'GlobalScreening - PEPs (International)',
    'ACC-COMPLINK-0125':'GlobalScreening - Sanctions (Custom) ',
    'ACC-COMPLINK-0062':'GlobalScreening - Sanctions (Domestic)',
    'ACC-COMPLINK-0085':'GlobalScreening - Sanctions (International)',
    'ACC-COMPLINK-0021':'GlobalScreening - Sanctions (International) (v2)',
    'IMMICARD-DOC-0083':'Immigration Card Verification (DVS)',
    'MEDICARE-CARD-0081':'Medicare (DVS)',
    'VEDA-NTD-0054':'National Tenancy (v3)',
    'VEDA-NTD-0061':'National Tenancy (v3.1)',
    'VEDA-NTD-0069':'National Tenancy (v3.2)',
    'DFAT-AP-0079':'Passport - Australian (DVS)',
    'DFAT-AP-0005':'Passport - Australian (v1)',
    'DIAC-VEVO-0080':'Passport - International with Visa (DVS)',
    'DIAC-VEVO-0006':'Passport - International with Visa (v1)',
    'NSW-POAC-0009':'Proof of Age Card – NSW (v1)',
    'MIRUS-SPD-0056':'Scanned Phone Directory (v3)',
    'VEDA-PND-0043':'Equifax Phone Number Directory (v3)',
    'VEDA-EVVELOCITY-0026':'Velocity Search',
    'VEDA-SFDPASSPORT-0025':'Fraud Lookup - Passport',
    'VEDA-SFDPHONE-0022':'Fraud Lookup - Phone',
    'VEDA-SFDADDR-0023':'Fraud Lookup - Address',
    'VEDA-SFDDL-0024':'Fraud Lookup - Driver Licence',
    'All Images Sources':'Upload Document Images',
    'SFA':'Second Factor Verification',
    'PNV':'Phone Number Verification',
    'DVI':'Device Intelligence',
    'KBA':'Knowledge Based Authentication'
}

def xml_to_dict_response(response_xml):
    response_dict = xmltodict.parse(response_xml)
    return response_dict['soapenv:Envelope']['soapenv:Body']

def passfort_to_equifax_ping(passfort_data):
    namespaces = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'wsse':'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
        'wsa': 'http://www.w3.org/2005/08/addressing',
        'ping': 'http://vedaxml.com/vxml2/ping-v1-0.xsd'

    }
    lxml_env = EnvelopeBuilder(namespaces)

    request_xml = lxml_env.soap.Envelope(
        lxml_env.soap.Header(
            lxml_env.build_security(passfort_data['username'], passfort_data['password']),
            lxml_env.ns.wsa.To("https://vedaxml.com/sys2/ping-v1"),
            lxml_env.ns.wsa.Action("https://vedaxml.com/mode/test"),
            lxml_env.ns.wsa.MessageID("Test_Ping")
        ),
        lxml_env.soap.Body(
            lxml_env.ns.ping.request({"client-reference":"Customer Test Ping"})
        )
    )
    return lxml_env.print(request_xml)

def passfort_to_equifax_data(passfort_data):
    namespaces = {
            'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
            'wsse':'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
            'wsa': 'http://www.w3.org/2005/08/addressing',
            'ping': 'http://vedaxml.com/vxml2/ping-v1-0.xsd',
            'idm': 'http://vedaxml.com/vxml2/idmatrix-v4-0.xsd'
        }
    lxml_env = EnvelopeBuilder(namespaces)

    credentials = passfort_data['credentials']

    request_xml = lxml_env.soap.Envelope(
        lxml_env.soap.Header(
            lxml_env.build_security(credentials['username'], credentials['password']),
            lxml_env.ns.wsa.ReplyTo(
                lxml_env.ns.wsa.Address('http://www.w3.org/2005/08/addressing/anonymous')
            ),
            lxml_env.ns.wsa.To('http://vedaxml.com/sys2/idmatrix-v4'),
            lxml_env.ns.wsa.Action('http://vedaxml.com/idmatrix/VerifyIdentity'),
            lxml_env.ns.wsa.MessageID(f's{uuid.uuid4()}')
        )
    )
    idm_request = lxml_env.ns.idm.request(
        lxml_env.build_consents(),{
            'client-reference': 'Quick Connect Ref',
            'reason-for-enquiry': 'Quick Connect'})
    body = lxml_env.soap.Body(
        idm_request
    )

    if passfort_data.get('input_data'):
        #Check Personal details 
        if passfort_data['input_data'].get('personal_details'):
            #Check name
            if passfort_data['input_data']['personal_details'].get('name'):
                idm_individual_name = lxml_env.ns.idm('individual-name')
                idm_request.append(idm_individual_name)
                
                if passfort_data['input_data']['personal_details']['name'].get('family_name'):
                    idm_individual_name.append(
                        lxml_env.ns.idm('family-name', 
                            passfort_data['input_data']['personal_details']['name']['family_name'])
                    )

                if passfort_data['input_data']['personal_details']['name'].get('given_names'):
                    given_names = passfort_data['input_data']['personal_details']['name']['given_names']
                    if given_names:
                        idm_individual_name.append(
                            lxml_env.ns.idm("first-given-name", given_names[0])
                        )
                        if given_names[1:]:
                            idm_individual_name.append(
                                lxml_env.ns.idm('other-given-name', ' '.join(given_names[1:]))
                            )
                    
            #Check date of birthday
            if passfort_data['input_data']['personal_details'].get('dob'):
                idm_request.append(
                    lxml_env.ns.idm('date-of-birth',
                        passfort_data['input_data']['personal_details']['dob'])
                )
                
            #Check gender
            if passfort_data['input_data']['personal_details'].get('gender'):
                equifax_gender = "male" if passfort_data['input_data']['personal_details']['gender'] == 'M' else 'female'
                idm_request.append(
                    lxml_env.ns.idm.gender(equifax_gender)
                )


        #Check address
        if passfort_data['input_data'].get('address_history'):
            for idx, address in enumerate(passfort_data['input_data']['address_history'][:2]):
                
                if idx == 0:
                    idm_current_address = lxml_env.ns.idm('current-address')
                else:
                    idm_current_address = lxml_env.ns.idm('previous-address')
                    
                idm_request.append(idm_current_address)

                address_to_check = address['address']

                if address_to_check.get('premise'):
                    idm_current_address.append(
                        lxml_env.ns.idm.property(address_to_check['premise'])
                    )
                if address_to_check.get('subpremise'):
                    idm_current_address.append(
                        lxml_env.ns.idm('unit-number', str(address_to_check['subpremise']))
                    )
                if address_to_check.get('street_number'):
                    idm_current_address.append(
                        lxml_env.ns.idm('street-number', str(address_to_check['street_number']))
                    )
                if address_to_check.get('route'):
                    idm_current_address.append(
                        lxml_env.ns.idm('street-name', address_to_check['route'])
                    )

                if address_to_check.get('locality'):
                    idm_current_address.append(
                        lxml_env.ns.idm.suburb(address_to_check['locality'])
                    )
                if address_to_check.get('state_province'):
                    idm_current_address.append(
                        lxml_env.ns.idm.state(address_to_check['state_province'])
                    )
                if address_to_check.get('postal_code'):
                    idm_current_address.append(
                        lxml_env.ns.idm.postcode(address_to_check['postal_code'])
                    )
                if address_to_check.get('country'):
                    idm_current_address.append(
                        lxml_env.ns.idm.country(address_to_check['country'])
                    )

            
        #Check Communication
        if passfort_data['input_data'].get('contact_details'):
            if passfort_data['input_data']['contact_details'].get('email'):
                idm_request.append(
                    lxml_env.ns.idm('email-address', passfort_data['input_data']['contact_details']['email'])
                )

            if passfort_data['input_data']['contact_details'].get('phone_number'):
                idm_phone = lxml_env.ns.idm.phone()
                idm_numbers = lxml_env.ns.idm.numbers()
                idm_phone.append(idm_numbers)
                idm_request.append(idm_phone)

                phone_number = passfort_data['input_data']['contact_details']['phone_number']
                idm_numbers.append(
                    lxml_env.ns.idm('mobile-phone-number', phone_number, {'verify': "1"})
                )
                idm_numbers.append(
                    lxml_env.ns.idm('home-phone-number', phone_number, {'verify': "1"})
                )
                idm_numbers.append(
                    lxml_env.ns.idm('work-phone-number', phone_number, {'verify': "1"})
                )

    request_xml.append(body)
    
    return lxml_env.print(request_xml)


def equifax_to_passfort_data(equifax_raw_data):
    #base response
    response_body = {
        "output_data": {
            'decision': 'ERROR'
        },
        "raw": equifax_raw_data,
        "errors": []
    }

    equifax_data = xml_to_dict_response(equifax_raw_data)

    if equifax_data:
        #Check errors:
        if 'soapenv:Fault' in equifax_data.keys():
            if equifax_data['soapenv:Fault'].get('detail'):
                server_fault = equifax_data['soapenv:Fault']['detail']['l7:policyResult']['@status']
            else:
                server_fault = equifax_data['soapenv:Fault']['faultstring']

            if (server_fault.strip() == 'Authentication Failed') or ('Service Not Found' in server_fault):
                response_body['errors'].append({
                    'code': 205, 
                    'message': f'Provider Error: {server_fault.strip()}'})
            elif server_fault.strip() == 'Service Temporarily Unavailable':
                response_body['errors'].append({
                    'code': 302, 
                    'message': f'Provider Error: {server_fault.strip()}'})
            elif server_fault.strip() in [
                'Error in Assertion Processing',
                'Error in Assertion Processing',
                'An error occurred when processing idMatixOperation']:
                response_body['errors'].append({
                    'code': 303, 
                    'message': f'Provider Error: {server_fault.strip()}'
                })
            elif server_fault.strip() == 'Bad Request':
                response_body['errors'].append({
                    'code': 201, 
                    'message': f'Provider Error: {server_fault.strip()}'})
        else:
        
            ns = [tag for tag in equifax_data.keys() if tag[0] not in ['@', "#"]][0].split(':')[0]

            indicator = equifax_data[f'{ns}:response']\
                [f'{ns}:response-outcome']\
                [f'{ns}:overall-outcome']

            #Possible Values: ACCEPT, REJECT,TIMEOUT, ERROR]
            if indicator == 'TIMEOUT':
                response_body['errors'].append({
                    'code': 403, 
                    'message': 'Provider Error: TIMEOUT'})
            elif indicator in ['REJECT', 'REJECT_ON_EXCLUSION']:
                response_body['output_data']['decision'] = 'FAIL'
            elif indicator == 'ERROR':
                response_body['errors'].append({
                    'code': 303, 
                    'message': 'Provider Error: UNKNOW ERROR'})
            if indicator in 'ACCEPT':
                response_body['output_data']['decision'] = 'PASS'

            if indicator in ['ACCEPT', 'REJECT', 'REJECT_ON_EXCLUSION']:
                search_results = equifax_data[f'{ns}:response']\
                    [f'{ns}:component-responses']\
                    [f'{ns}:verification-response']\
                    [f'{ns}:search-results'].get(f'{ns}:search-result')
                
                if search_results:
                    matches = []

                    #Normalize output, if is only one element didn't return a list
                    if type(search_results) == OrderedDict:
                        search_results = [search_results]

                    for search_result in search_results:

                        datasource_name  = DATASOUCES.get(search_result["@search-name"], search_result["@search-name"] + ' - (Unknown Datasource)')
                        match = {
                            'database_name': datasource_name,
                            'database_type': 'CREDIT' if 'credit' in datasource_name.lower() else 'CIVIL',
                            'matched_fields': [],
                            'count': 0
                        }
                        matches.append(match)

                        if search_result['@match-indicator'] == 'PASS':
                            match['count'] = 1
                        
                            #check names
                            individual_name = search_result.get(f'{ns}:individual-name')
                            if individual_name:
                                #check forename
                                if f'{ns}:first-given-name' in individual_name.keys():
                                    if '@match-score-weight' in individual_name[f'{ns}:first-given-name'] and\
                                        int(individual_name[f'{ns}:first-given-name']['@match-score-weight']) > 0 and \
                                        int(individual_name[f'{ns}:first-given-name'].get('@match-score', 1)) > 0:
                                        match['matched_fields'].append('FORENAME')

                                #check surname
                                if f'{ns}:family-name' in individual_name.keys():
                                    if '@match-score-weight' in individual_name[f'{ns}:family-name'] and\
                                        int(individual_name[f'{ns}:family-name']['@match-score-weight']) > 0 and \
                                        int(individual_name[f'{ns}:family-name'].get('@match-score', 1)) > 0:
                                        match['matched_fields'].append('SURNAME')

                            #check date of birthday (DOB)
                            if f'{ns}:date-of-birth' in search_result.keys():
                                if '@match-score-weight' in search_result[f'{ns}:date-of-birth'] and\
                                    int(search_result[f'{ns}:date-of-birth']['@match-score-weight']) > 0 and \
                                    int(search_result[f'{ns}:date-of-birth'].get('@match-score', 1)) > 0:
                                    match['matched_fields'].append('DOB')

                            # Check Equifax interpretation of address match, giving precedence to current-address
                            if f'{ns}:current-address' in search_result.keys() and\
                                int(search_result[f'{ns}:current-address'].get('@match-score-weight',0)) > 0 and\
                                    int(search_result[f'{ns}:current-address'].get('@match-score', 0)) > 0:
                                match['matched_fields'].append('ADDRESS')

                            elif f'{ns}:previous-address' in search_result.keys() and\
                                int(search_result[f'{ns}:previous-address'].get('@match-score-weight',0)) > 0 and\
                                    int(search_result[f'{ns}:previous-address'].get('@match-score', 0)) > 0:
                                match['matched_fields'].append('ADDRESS')


                    if matches:
                        response_body['output_data']["entity_type"] = "INDIVIDUAL"
                        response_body['output_data']["electronic_id_check"] = {"matches": matches}

    return response_body
