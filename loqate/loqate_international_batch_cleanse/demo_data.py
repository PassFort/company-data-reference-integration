from app.api.models import GeoCodingCheck, LoqateAddress

def get_demo_result(data: GeoCodingCheck):
    output_address = LoqateAddress.from_passfort(data.input_data.address).to_primitive()

    if (getattr(data.input_data.address, 'county', None) or '').upper() == 'FAIL':
        return {
            "output_data": {
                "address": {
                    **data.input_data.address.to_primitive(),
                },
                "metadata": {
                    "geocode_accuracy": {
                        "status": "FAILED",
                    }
                },
            },
            "raw": [{
                'Input': output_address,
                'Matches': [{**output_address}],
            }],

        }
    return {
        "output_data": {
            "address": {
                **data.input_data.address.to_primitive(),
                "latitude": 57.145618,
                "longitude": -2.096897,
            },
            "metadata": {
                "geocode_accuracy": {
                    "status": "POINT",
                    "level": "DELIVERY_POINT",
                }
            },
        },

        "raw": [{
            'Input': output_address,
            'Matches': [{**output_address, "GeoAccuracy": 'P1'}],
        }]
    }

