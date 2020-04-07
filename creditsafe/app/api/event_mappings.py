from enum import Enum, unique


@unique
class MonitoringConfigType(Enum):
    ASSESS_FINANCIAL_DATA = 'assess_financial_data'
    IDENTIFY_OFFICERS = 'identify_officers'
    VERIFY_COMPANY_DETAILS = 'verify_company_details'


_supported_events = {
    'XX': [
        {
            'creditsafe_event': {
                'ruleCode': 101,
                'param0': '1',
                'param1': 'A'
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 102,
                'param0': 'True'
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 104
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 105
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 107
            },
            'passfort_type': MonitoringConfigType.IDENTIFY_OFFICERS
        }
    ],
    'GB': [
        {
            'creditsafe_event': {
                'ruleCode': 1804
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 1815
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'US': [
        {
            'creditsafe_event': {
                'ruleCode': 1603
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'AT': [
        {
            'creditsafe_event': {
                'ruleCode': 3100
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 3101
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'BE': [
        {
            'creditsafe_event': {
                'ruleCode': 1718
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'DK': [
        {
            'creditsafe_event': {
                'ruleCode': 1010
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 1007
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'FR': [
        {
            'creditsafe_event': {
                'ruleCode': 302
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 704
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 802
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'FI': [
        {
            'creditsafe_event': {
                'ruleCode': 806
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 802
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
     'DE': [
        {
            'creditsafe_event': {
                'ruleCode': 2004
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 2006
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'IE': [
        {
            'creditsafe_event': {
                'ruleCode': 3056
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 2103
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'IT': [
        {
            'creditsafe_event': {
                'ruleCode': 1406
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 1405
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
     'LI': [
        {
            'creditsafe_event': {
                'ruleCode': 2401
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
     'LU': [
        {
            'creditsafe_event': {
                'ruleCode': 1308
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'NL': [
        {
            'creditsafe_event': {
                'ruleCode': 1511
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'NO': [
        {
            'creditsafe_event': {
                'ruleCode': 924
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 925
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'ES': [
        {
            'creditsafe_event': {
                'ruleCode': 2202
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 2201
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ],
    'SE': [
        {
            'creditsafe_event': {
                'ruleCode': 3040
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        },
        {
            'creditsafe_event': {
                'ruleCode': 3043
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        },
        {
            'creditsafe_event': {
                'ruleCode': 3044
            },
            'passfort_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA
        }
    ]
}


def get_rule_code_to_monitoring_config():
    rule_code_to_monitoring_config = {}
    for country_code in _supported_events:
        for country_event in _supported_events[country_code]:
            passfort_type = country_event['passfort_type']
            # Only get financial events for GB and global for now
            if passfort_type != MonitoringConfigType.ASSESS_FINANCIAL_DATA or country_code == 'GB' or country_code == 'XX':
                rule_code_to_monitoring_config[country_event['creditsafe_event']['ruleCode']] = passfort_type
    return rule_code_to_monitoring_config


def get_configure_event_payload():
    """
    Generates the full configure event payload needed to add monitoring events we support to a Creditsafe portfolio.
    The full structure for each country rule:
    {
        'isActive': 1,
        'ruleCode': <ruleCode>,
        'ruleCountryCode': <countryCode>,
        'param0': '1'  # param is optional
    }
    """
    configure_event_payload = {
        country: [
            {
                'isActive': 1,
                'ruleCountryCode': country,
                **event['creditsafe_event']
            }
            for event in event_configs
        ]
        for country, event_configs in _supported_events.items()
    }

    return configure_event_payload
