from app.mock_data.mock_responses import mock_uk_response, mock_one_plus_one, mock_fail


def get_demo_response(name):
    if 'fail' in " ".join(name.given_names).lower() or 'fail' in name.family_name.lower():
        # Return data which will trigger a fail on the stage
        return mock_fail
    elif '1+1' in " ".join(name.given_names).lower() or '1+1' in name.family_name.lower():
        # Return data which will trigger a 1+1 on the stage
        return mock_one_plus_one

    # Return data which will trigger a 2+2 on the stage
    return mock_uk_response
