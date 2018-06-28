from app.mock_data.mock_responses import mock_uk_response, mock_uk_response_fail, mock_uk_response_one_plus_one, \
    mock_watchlist_consider, mock_watchlist_pass


def get_demo_ekyc_response(name):
    if 'fail' in " ".join(name['given_names']).lower() or 'fail' in name['family_name'].lower():
        # Return data which will trigger a fail on the stage
        return mock_uk_response_fail
    elif '1+1' in " ".join(name['given_names']).lower() or '1+1' in name['family_name'].lower():
        # Return data which will trigger a 1+1 on the stage
        return mock_uk_response_one_plus_one

    # Return data which will trigger a 2+2 on the stage
    return mock_uk_response


def get_demo_watchlist_response(name):
    joined_name = (' '.join(name['given_names']) + name['family_name']).lower()

    if 'pep' in joined_name or 'sanction' in joined_name:
        return mock_watchlist_consider

    return mock_watchlist_pass
