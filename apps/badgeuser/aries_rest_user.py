import os
import re
import urllib
import json
import threading
import subprocess
import time
from django.db import connection
import requests
import os.path
from django.conf import settings


host = settings.REST_ARIES['HOST']
port = settings.REST_ARIES['PORT']
wallet_prefix = settings.REST_ARIES['WALLET_PREFIX']
wallet_webhook_urls = settings.REST_ARIES['WALLET_WEBHOOK_URLS']
wallet_pass = settings.REST_ARIES['WALLET_PASS']
serviceEndpoint = settings.REST_ARIES['SERVICEENDPOINT']
endpoint = host + ":" + port

def create_subwallet(first_name, last_name, email_user):
    
#Create subwallet in Hyperledger Aries with email adress   
    json_model = {
    "key_management_mode": "managed",
    "label": email_user,
    "wallet_dispatch_type": "default",
    "wallet_key": wallet_pass,
    "wallet_name": wallet_prefix + "." + first_name + last_name,
    "wallet_type": "indy",
    "wallet_webhook_urls": [wallet_webhook_urls]
    }
    
    token = None
    connection = None    
    endpoint = host + ":" + port
    
    try:
        response = requests.post(
            endpoint
            + "/multitenancy/wallet",
            json.dumps(json_model)
        )
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection

def delete_subwallet(wallet_id):
    
#Delete subwallet in Hyperledger Aries with email adress   
    json_model = {
        "wallet_key": "MySecretKey123"
    }
    
    wallet_id = str(wallet_id)
    
    connection = None    
    endpoint = host + ":" + port
    
    try:
        response = requests.post(
            endpoint
            + "/multitenancy/wallet/" + wallet_id + "/remove",
            json.dumps(json_model)
        )
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection

def create_local_did(token_user):
        
    json_model = {
    "method": "key",
    "options": {
        "key_type": "bls12381g2"
        }
    }
    token_user = str(token_user)
    
    header = {'Authorization': 'Bearer ' + token_user}
    
    did = None
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/wallet/did/create",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
        
        did = connection["result"]["did"]
                    
    except:
        raise    
    finally:             
        return did
    
def create_issuer_did(token_user):
        
    json_model = {
        "method": "key",
        "options": {
        "key_type": "bls12381g2"
    }

    }
    
    token_user = str(token_user)
    
    header = {'Authorization': 'Bearer ' + token_user}
    
    did = None
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/wallet/did/create",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
        
        did = connection["result"]["did"]
                    
    except:
        raise    
    finally:             
        return did