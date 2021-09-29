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

def create_subwallet(email_wallet):
        
    json_model = {
    "key_management_mode": "managed",
    "label": email_wallet,
    "wallet_dispatch_type": "default",
    "wallet_key": wallet_pass,
    "wallet_name": wallet_prefix + "." + email_wallet,
    "wallet_type": "indy",
    "wallet_webhook_urls": [wallet_webhook_urls]
    }
    
    
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
        token = connection["token"]
                
    except:
        raise    
    finally:             
        return token


def create_local_did(token):
        
    json_model = {
    "method": "key",
    "options": {
        "key_type": "bls12381g2"
        }
    }
    header = {'Authorization': 'Bearer ' + token}
    
    print(header)
    
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
        
        print('did->', connection["result"]["did"])
        print('verkey->', connection["result"]["verkey"])
                        
    except:
        raise    
    finally:             
        return connection


def create_invite(token):
            
    header = {'Authorization': 'Bearer ' + token}
    
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/connections/create-invitation",
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection


def accept_invite(token_org, id, recipientKeys):
    
    json_model = {
    "@id": id, 
	"recipientKeys": [recipientKeys], 
	"serviceEndpoint": serviceEndpoint
    }
       
    header = {'Authorization': 'Bearer ' + token_org}
    
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/connections/receive-invitation",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection

def create_did_issuer(token):
    
    json_model = {
        "method": "key",
        "options": {
        "key_type": "bls12381g2"
        }
    }
       
    header = {'Authorization': 'Bearer ' + token}
    
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
        print(connection)
                        
    except:
        raise    
    finally:             
        return connection

def create_credendencial(token, connection_id, issuer_id, recipient):
    
    json_model = {
        "connection_id": connection_id,
        "filter":{
            "ld_proof":{
                "options":{"proofType":"BbsBlsSignature2020"},
                "credential":{
                    "@context":["https://www.w3.org/2018/credentials/v1","https://w3id.org/openbadges/v2"], 
                    "@protected": False,
                    "issuanceDate":"{% now 'iso-8601', '' %}",
                    "type": ["VerifiableCredential","PermanentResident", "Assertion"],
                    "issuer":"issuer_id",
                            "credentialSubject":{
                            },
                    "badge":{
                        "id":"urn:uuid:82a4c9f2-3588-457b-80ea-da695571b8fc",
                        "type":"BadgeClass",
                        "name":"Certificate of Accomplishment",
                        "image":"data:image/png;base64,...",
                        "description":"Primeiro teste de Badge no Hyperledger Indy.",
                        "criteria":{
                         "narrative":"Objetivo 1 ."
                        },
                        "issuer":{
                            "id":"https://www.blockcerts.org/samples/2.0/issuer-testnet.json",
                            "type":"Profile",
                            "name":"University of Learning",
                            "url":"https://www.issuer.org",
                            "email":"admin@serpro.gov.br",
                            "revocationList":"https://www.blockcerts.org/samples/2.0/revocation-list-testnet.json",
                            "image":"data:image/png;..."
                        }
                    },
                    "recipient":{
                    "hashed": False,
                    "identity": recipient,
                    "type":"email"
                    }
                }
            }
        }
    }
    
    
    header = {'Authorization': 'Bearer ' + token}
    
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/issue-credential-2.0/send-offer",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection

