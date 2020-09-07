from app.api.models import CheckInput, LoqateAddress, PassFortAddress

mock_input = {
    "address": {
        "type": "STRUCTURED",
        "country": "GBR",
        "county": "Aberdeen City",
        "locality": "Aberdeen",
        "original_freeform_address": "2, Imperial House 12-14, , Exchange Street, Aberdeen, , Aberdeen City, , AB11 6PH",
        "original_structured_address": {
            "country": "GBR",
            "county": "Aberdeen City",
            "locality": "Aberdeen",
            "postal_code": "AB11 6PH",
            "postal_town": "",
            "premise": "Imperial House 12-14",
            "route": "Exchange Street",
            "state_province": "",
            "street_number": "50",
            "subpremise": "2"
        },
        "postal_code": "AB11 6PH",
        "postal_town": "",
        "premise": "Imperial House 12-14",
        "route": "Exchange Street",
        "state_province": "",
        "street_number": "50",
        "subpremise": "2"
    }
}

loqate_address = {
    "Address":"",
    "Address1":"Schubartstr. 111",
    "Address2":"Bietigheim-Bissingen",
    "Address3":"74321",
    "Address4":"",
    "Address5":"",
    "Address6":"",
    "Address7":"",
    "Address8":"",
    "Country":"DEU",
    "SuperAdministrativeArea":"",
    "AdministrativeArea":"Baden-Württemberg",
    "SubAdministrativeArea":"",
    "Locality":"Koln",
    "ISO3166-3": "DEU",
    "DependentLocality":"",
    "DoubleDependentLocality":"",
    "Thoroughfare":"",
    "DependentThoroughfare":"",
    "Building":"",
    "Premise":"Hertscher 25",
    "SubBuilding":"",
    "PostalCode":"74321",
    "Organization":"",
    "PostBox":"",
    "Latitude": "50.940529",
    "Longitude": "6.959910",
}


def test_passfort_to_loqate():
    input = CheckInput().import_data(mock_input)
    expected = {
        "Locality": "Aberdeen",
        "Premise": "Imperial House 12-14",
        "PostalCode": "AB11 6PH",
        "ISO3166-3": "GBR",
        "Country": "GBR",
        "SubAdministrativeArea": "Aberdeen City",
        "Thoroughfare": "50 Exchange Street"
    }
    actual = LoqateAddress.from_passfort(input.address)

    assert expected == actual.to_primitive()

def test_loqate_to_passfort():
    address = LoqateAddress().from_raw(loqate_address)
    expected = {
        "type": "STRUCTURED",
        "country": "DEU",
        "locality": "Koln",
        "postal_code": "74321",
        "premise": "Hertscher 25",
        "longitude": 6.959910,
        "latitude": 50.940529,
    }
    actual = PassFortAddress.from_loqate(address)

    assert expected == actual.to_primitive()

def test_minimal_passfort_to_loqate():
    input = CheckInput().import_data({
        "address": {
            "type": "STRUCTURED",
            "country": "GBR",
            "locality": "London",
        }
    })

    expected = {
        "Country": "GBR",
        "ISO3166-3": "GBR",
        "Locality": "London",
    }

    actual = LoqateAddress.from_passfort(input.address)

    assert expected == actual.to_primitive()

def test_minimal_loqate_to_passfort():
    address = LoqateAddress().from_raw({"Country": "DEU", "ISO3166-3": "DEU", "Locality": 'Koln'})
    expected = {
        "type": "STRUCTURED",
        "country": "DEU",
        "locality": "Koln",
    }
    actual = PassFortAddress.from_loqate(address)

    assert expected == actual.to_primitive()


