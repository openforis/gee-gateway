import ee
from ee.ee_exception import EEException
import argparse

try:
    ee.Initialize()
except EEException:

    from oauth2client.service_account import ServiceAccountCredentials

    parser = argparse.ArgumentParser()
    parser.add_argument('--ee_account', action='store', default='', help='Google Earth Engine account')
    parser.add_argument('--ee_key_path', action='store', default='', help='Google Earth Engine key path')
    args, unknown = parser.parse_known_args()

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email=args.ee_account,
        filename=args.ee_key_path,
        private_key_password='notasecret',
        scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive ')

    ee.Initialize(credentials)

import utils