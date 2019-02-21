from app.mock_data.mock_responses import mock_uk_matches, mock_uk_matches_fail, mock_uk_matches_one_plus_one, \
    mock_watchlist_consider, mock_watchlist_pass


def get_demo_ekyc_response(name):
    matches = mock_uk_matches
    if 'fail' in " ".join(name['given_names']).lower() or 'fail' in name['family_name'].lower():
        # Return data which will trigger a fail on the stage
        matches = mock_uk_matches_fail
    elif '1+1' in " ".join(name['given_names']).lower() or '1+1' in name['family_name'].lower():
        # Return data which will trigger a 1+1 on the stage
        matches = mock_uk_matches_one_plus_one

    # Return data which will trigger a 2+2 on the stage
    return {
        'output_data': {
            'matches': matches
        }
    }


def get_demo_watchlist_response(name):
    joined_name = (' '.join(name['given_names']) + name['family_name']).lower()

    if 'pep' in joined_name or 'sanction' in joined_name:
        return mock_watchlist_consider

    return mock_watchlist_pass
