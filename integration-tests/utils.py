import random
import univention.testing.strings as uts

from typing import Optional
from datetime import date, datetime, timedelta

COUNTRY_CODES = (
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
)


def random_date(
    start_date: Optional[date] = None, end_date: Optional[date] = None
) -> date:
    end_date = end_date or datetime.now().date()
    start_date = start_date or end_date - timedelta(365 * 20)

    return start_date + (end_date - start_date) * random.random()


def udm_user_args(minimal=True, suffix=""):
    _username = uts.random_username() + suffix
    result = {
        "firstname": f"{uts.random_string()}{suffix}",
        "lastname": f"{uts.random_string()}{suffix}",
        "username": _username,
        "displayName": _username,
        "password": uts.random_string(),
        # 'mailHomeServer': f"{ucr['hostname']}.{ucr['domainname']}",
        # 'mailPrimaryAddress': f"{_username}@{ucr['domainname']}",
    }
    if minimal:
        return result

    result.update(
        {
            "birthday": random_date().strftime("%Y-%m-%d"),
            "city": uts.random_string(),
            "country": random.choice(COUNTRY_CODES),
            "description": uts.random_string(),
            "employeeNumber": f"{3 * uts.random_int()}",
            "employeeType": uts.random_string(),
            "organisation": uts.random_string(),
            "postcode": f"{3 * uts.random_int()}",
            "street": uts.random_string(),
            "title": uts.random_string(),
        }
    )

    result.update(
        {
            "roomNumber": [
                f"{3 * uts.random_int()}",
                f"{3 * uts.random_int()}",
            ],
            "departmentNumber": [
                uts.random_string(),
                uts.random_string(),
            ],
            "homePostalAddress": [
                {
                    "street": uts.random_string(),
                    "zipcode": f"{5 * uts.random_int()}",
                    "city": uts.random_string(),
                    uts.random_string(): uts.random_string(),
                },
            ],
            "homeTelephoneNumber": [uts.random_string(), uts.random_string()],
            # 'mailAlternativeAddress': [
            #     f"{uts.random_username()}@{ucr['domainname']}",
            #     f"{uts.random_username()}@{ucr['domainname']}"
            # ],
            "mobileTelephoneNumber": [uts.random_string(), uts.random_string()],
            "pagerTelephoneNumber": [uts.random_string(), uts.random_string()],
            "phone": [f"{12 * uts.random_int()}", f"{12 * uts.random_int()}"],
            # 'secretary': [
            #     f"uid=Administrator,cn=users,{ucr['ldap/base']}",
            #     f"uid=Guest,cn=users,{ucr['ldap/base']}"
            # ],
            "e-mail": [
                f"{uts.random_username()}@{uts.random_username()}",
                f"{uts.random_username()}@{uts.random_username()}",
            ],
        }
    )

    return result
