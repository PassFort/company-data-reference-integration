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
        }
    ],
    # 'BE': [],  # Uncomment when we figured out what rules to apply for this country
    'DK': [
        {
            'creditsafe_event': {
                'ruleCode': 1010
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'FR': [
        {
            'creditsafe_event': {
                'ruleCode': 302
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'FI': [
        {
            'creditsafe_event': {
                'ruleCode': 806
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    # 'DE': [],
    'IE': [
        {
            'creditsafe_event': {
                'ruleCode': 3056
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'IT': [
        {
            'creditsafe_event': {
                'ruleCode': 1406
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    # 'LI': [],  # Uncomment when we figured out what rules to apply for this country
    # 'LU': [],  # Uncomment when we figured out what rules to apply for this country
    # 'NL': [],  # Uncomment when we figured out what rules to apply for this country
    'NO': [
        {
            'creditsafe_event': {
                'ruleCode': 924
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'ES': [
        {
            'creditsafe_event': {
                'ruleCode': 2202
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ],
    'SE': [
        {
            'creditsafe_event': {
                'ruleCode': 3040
            },
            'passfort_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS
        }
    ]
}


def get_rule_code_to_monitoring_config():
    rule_code_to_monitoring_config = {}
    for event_configs in _supported_events.values():
        for event in event_configs:
            rule_code_to_monitoring_config[event['creditsafe_event']['ruleCode']] = event['passfort_type']
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
