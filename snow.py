import json, requests, logging, _snowflake

logger = logging.getLogger('sedona_api_logger')
logger.setLevel(logging.DEBUG)
url = "https://testsedonaapi.guardiansecurity.com/"

def call_api(env, method, endpoint, payload):
    try:
        logger.info(f"calling api endpoint {endpoint} in env {env} with payload {json.dumps(payload)}")
        token = refresh_token()
        logger.info(f"token refreshed successfully: {token}")
        api_url = f"{url}{env}/api/{endpoint}"
        res = None
        if (method == 'POST'):
            res = requests.post(api_url, data=payload, headers={'Authorization': f'Bearer {token}'})
        elif (method == 'PUT'):
            res = requests.put(api_url, data=payload, headers={'Authorization': f'Bearer {token}'})
        elif (method == 'GET'):
            res = requests.get(api_url, headers={'Authorization': f'Bearer {token}'})
        else:
            raise ValueError(f"unsupported HTTP method: {method}")
        if res.status_code != 200:
            logger.error(f"failed to call api endpoint {endpoint}: {res.status_code} {res.text}")
            return {"ok": False, "message": res.text}
        return res.json()
    except Exception as e:
        logger.exception(f"exception while calling api endpoint {endpoint} in env {env}: {e}")
        raise

def refresh_token():
    user_auth = _snowflake.get_username_password('user_auth')
    client_auth = _snowflake.get_username_password('client_auth')
    body = {
        'grant_type': 'password',
        'username': user_auth.username,
        'password': user_auth.password,
        'scope': 'sedonacloudapi sedonacloudscope openid offline_access',
    }
    logger.info(f"refreshing token for user {user_auth.username} {json.dumps(body)} client: {client_auth.username}")
    res = requests.post(url + 'connect/token', data=body, auth=(client_auth.username, client_auth.password))

    if res.status_code != 200:
        logger.error(f"failed to refresh token: {res.status_code} {res.text}")
        raise Exception(f"failed to refresh token: {res.status_code} {res.text}")
    token = res.json()['access_token']
    
    return token