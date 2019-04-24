from datetime import datetime

def get_demo_work_visa(visa_holder, expiry_date):
    return {
        "output": {
            "id": "123456",
            "Time of Check": "Tuesday August 15, 2017 20:32:48 (EST) Canberra, Australia (GMT +1000)",
            "Person Checked": {
                "Name": f'{visa_holder.given_names} {visa_holder.family_name}',
                "DOB": convert_date(visa_holder.date_of_birth),
                "Passport ID": visa_holder.passport_id,
                "Nationality": visa_holder.country
            },
            "status": "",
            "result": "OK",
            "Visa Details": {
                "Visa Applicant": "Primary",
                "Visa Class": "SI",
                "Visa Type": "820",
                "Visa Type Name": "Partner",
                "Grant Date": "14 Mar 2000",
                "Expiry Date": expiry_date,
                "Visa Type Details": "For partners of Australian citizens and permanent residents"
            },
            "Work Entitlement": "The visa holder has unlimited right to work in Australia.",
            "Visa Conditions": "",
            "conditions": "",
            "token": "demoworkvisa",
            "haspdf": 1
        },
        "error": ""
    }

def get_demo_study_visa(visa_holder, expiry_date):
    return {
        "output": {
            "id": "245645",
            "Time of Check": "Wednesday August 16, 2017 14:41:02 (EST) Canberra, Australia (GMT +1000)",
            "Person Checked": {
                "Name": f'{visa_holder.given_names} {visa_holder.family_name}',
                "DOB": convert_date(visa_holder.date_of_birth),
                "Passport ID": visa_holder.passport_id,
                "Nationality": visa_holder.country
            },
            "status": "",
            "result": "OK",
            "Visa Details": {
                "Visa Applicant": "Primary",
                "Visa Class": "SI",
                "Visa Type": "457",
                "Visa Type Name": "Temporary Work (Skilled)",
                "Grant Date": "22 Oct 2000",
                "Expiry Date": expiry_date,
                "Visa Type Details": "For people sponsored by an employer previously named Business (Long Stay)"
            },
            "Study Condition": "No limitations on study.",
            "Visa Conditions": "",
            "conditions": "",
            "token": "demostudyvisa",
            "haspdf": 1
        },
        "error": ""
    }


def get_demo_no_visa_response(visa_holder):
    return {
        "output": {
            "id": "345345",
            "Time of Check": "Tue Aug 15 21:02:38 EST 2017",
            "Person Checked": {
                "Name": f'{visa_holder.given_names} {visa_holder.family_name}',
                "DOB": convert_date(visa_holder.date_of_birth),
                "Passport ID": visa_holder.passport_id,
                "Nationality": visa_holder.country
            },
            "status": "",
            "result": "OK",
            "Visa Details": {
                "Visa Type": 0,
                "Grant Date": "N/A",
                "Expiry Date": "N/A",
                "Visa Type Details": ""
            },
            "Work Entitlement": "",
            "Visa Conditions": "",
            "conditions": "",
            "token": "testnovisa",
            "haspdf": 0
        },
        "error": "Error: Does not hold a valid visa"
    }

def get_demo_not_found_response(visa_holder):
    return {
        "output": {
            "id": "1198",
            "Time of Check": "Tue Aug 15 19:52:16 EST 2017",
            "Person Checked": {
                "Name": f'{visa_holder.given_names} {visa_holder.family_name}',
                "DOB": convert_date(visa_holder.date_of_birth),
                "Passport ID": visa_holder.passport_id,
                "Nationality": visa_holder.country
            },
            "status": "Could not complete visa check - The Department has not been able to identify the person. Please check that the details you entered in are correct.",
            "result": "Error",
            "token": "testunidentifiedperson",
            "haspdf": 0
        },
        "error": ""
    }

def convert_date(value):
    try:
        if not value or value == 'N/A':
            return None
        date = datetime.strptime(value, '%Y-%m-%d')
        return date.strftime('%d %b %Y')
    except (ValueError, TypeError):
        raise ValidationError(f'Input is not valid date: {value}')