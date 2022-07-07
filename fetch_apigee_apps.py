import os
import sys
import time

import requests

credentials = tuple(sys.argv[1].split(':'))

apigee_base_url = 'https://api.enterprise.apigee.com/v1/organizations/oregonstateuniversity'
apigee_apps_url = f'{apigee_base_url}/apps?expand=true'
apigee_developer_url = f'{apigee_base_url}/developers'

response = requests.get(apigee_apps_url, auth=credentials)
if response.status_code == 200:
    pending_apps = {}
    for app in response.json()['app']:
        app_id = app['appId']
        app_name = app['name']
        developer_id = app['developerId']
        for credential in app['credentials']:
            if 'apiProducts' in credential:
                for api_product in credential['apiProducts']:
                    product_name = api_product['apiproduct']
                    status = api_product['status']
                    if status == 'pending':
                        if app_id not in pending_apps:
                            dev_response = requests.get(
                                f'{apigee_developer_url}/{app["developerId"]}',
                                auth=credentials
                            ).json()

                            pending_apps[app_id] = {
                                'app_name': app_name,
                                'create_at': time.ctime(app['createdAt']/1000),
                                'pending_products': [product_name],
                                'email': dev_response['email'],
                                'username': dev_response['userName'],
                                'first_name': dev_response["firstName"],
                                'last_name': dev_response["lastName"]
                            }
                        else:
                            pending_apps[app_id]['pending_products'].append(
                                product_name
                            )

    for _, pending_app in pending_apps.items():
        print('-------------------------------------------------------------')
        print(f'App name: {pending_app["app_name"]}')
        print(f'Create at: {pending_app["create_at"]}')
        print(f'Pending products: {pending_app["pending_products"]}')
        print(f'Developer email: {pending_app["email"]}')
        print(f'Developer username: {pending_app["username"]}')
        print('Developer name: ' +
              f'{pending_app["first_name"]} {pending_app["last_name"]}')

else:
    sys.exit('Unable to call Apigee API.')
