import json
import logging
 
from django.contrib.auth.models import User
from django.db import connection, models
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse


import requests
#import os.path
from django.conf import settings


#From ./.docker/etc/settings_local.dev.py
host = settings.REST_ARIES['HOST']
port = settings.REST_ARIES['PORT']
wallet_prefix = settings.REST_ARIES['WALLET_PREFIX']
wallet_webhook_urls = settings.REST_ARIES['WALLET_WEBHOOK_URLS']
wallet_pass = settings.REST_ARIES['WALLET_PASS']
service_endpoint = settings.REST_ARIES['SERVICEENDPOINT']
endpoint = host + ":" + port



def create_connection(recipient_identifier, created_by): 
    #Create connection betweeen issuer and recipient
    from badgeuser.models import BadgeUser
    token_recipient = BadgeUser.objects.get(email=recipient_identifier)
    token_creator = BadgeUser.objects.get(email=created_by)
    
    token_recipient = token_recipient.token   
    token_creator = token_creator.token
    connection_exist = None

    connection_exist = check_connection(created_by, token_recipient)
    
    if  connection_exist == False:       
        connection = create_invite(created_by, token_creator) 
        id = connection["invitation"]["@id"]
        recipientKeys = connection["invitation"]["recipientKeys"]
        connection = accept_invite(created_by, token_recipient, id, recipientKeys)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.info("User exist")      
    

def check_connection(created_by, token_recipient):
    #Check if connection exist betweeen issuer and recipient    
    created_by = str(created_by)
    
    token_user = token_recipient
    header = {'Authorization': 'Bearer ' + token_user}
       
    try:
        response = requests.get(
            endpoint
            + "/connections?alias=" + created_by + "&state=active",
            headers=header
        )
        
        response.raise_for_status()
        
        #Check if Connection exist in Hyperledger Aries
        test = response.json()["results"]
        if len(test) == 0:
            connection = False
        else:
            connection = True
           
    except:
        raise    
    finally:             
        return connection


def create_invite(created_by, token_creator):
    #Issuer create invite to connection    
    json_model = {
        "my_label": created_by
    }
    
    token_user = token_creator
    header = {'Authorization': 'Bearer ' + token_user}
    did = None
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/connections/create-invitation",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
        
        id = connection["invitation"]["@id"]
        
        recipientKeys = connection["invitation"]["recipientKeys"] 
                   
    except:
        raise    
    finally:             
        return connection


def accept_invite(created_by, token_recipient, id, recipientKeys):
    #Accept invite from issuer to recipient
    service_endpoint = settings.REST_ARIES['SERVICEENDPOINT']
    created_by = str(created_by)
     
    json_model = {
            "@id": id,
            "recipientKeys": recipientKeys, 
            "serviceEndpoint": service_endpoint             
    }
    
    token_user = token_recipient
    
    header = {'Authorization': 'Bearer ' + token_user}
    
    did = None
    connection = None    
    
    alias = created_by
      
    try:
        response = requests.post(
            endpoint
            + "/connections/receive-invitation?alias=" + alias,
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                    
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
    

def get_connection_id(recipient_identifier, email_issuer):
    #Check if connection exist betweeen issuer and recipient
    
    email = str(recipient_identifier)
    created_by = str(email_issuer)
    
    from badgeuser.models import BadgeUser
    token_issuer = BadgeUser.objects.get(email=created_by)  
    
    connection_id = None
    
    token = token_issuer.token
    header = {'Authorization': 'Bearer ' + token}
       
    try:
        response = requests.get(
            endpoint
            + "/connections?their_label=" + email,
            headers=header
        )
        
        response.raise_for_status()
        
        #Check if Connection exist in Hyperledger Aries
        connection = response.json()
        connection_id = connection['results'][0]['connection_id']
                  
    except:
        raise    
    finally:             
        return connection_id    
    

def create_credential(conn_id, self):
    
    created_by = self.created_by.email
    
    from badgeuser.models import BadgeUser
    issuer_user = BadgeUser.objects.get(email=created_by)
    
    issuancedate = str(self.issued_on)
    badge_name = str(self.badgeclass.name)
    badge_class = str(self.badgeclass.entity_id)
    issuer_email = str(issuer_user.email)
    issuer_url = str(self.issuer.url)
    recipient_email = str(self.recipient_identifier)
    issuer_name = str(self.issuer.name)
    issuer_image = str(self.issuer.image_preview.path)
    narrative = str(self.narrative)
    description = str(self.issuer.description)
    issuer_did  = str(self.issuer.issuer_did)
    issuer_id = str(self.issuer.entity_id)
    badge_id =  str(self.entity_id)
    badge_image = str(self.image.name)
    recipient_name = str(self.recipient_user.first_name + " " + self.recipient_user.last_name)
    token = str(issuer_user.token) 
    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/json'}
    creator = str(self.created_by)
    connection = None

    
    json_model_rest = {
        
   "connection_id":conn_id,
   "filter":{
        "ld_proof":{
			"options":{
                "proofType":"BbsBlsSignature2020"
            },
        "credential":{
            "@context":["https://www.w3.org/2018/credentials/v1","https://w3id.org/openbadges/v2" ], 
            "@protected":False,
            "issuanceDate":issuancedate,
            "type": ["VerifiableCredential","PermanentResident", "Assertion"],
            "issuer":issuer_did,
			"credentialSubject":{},
            "badge":{
               "id":badge_id,
               "type":"BadgeClass",
               "BadgeClass": badge_class,
               "name":badge_name,
               "image":badge_image,
               "description":description,
               "criteria":{
                  "narrative":narrative
                },
               "issuer":{
                "type":"Profile",
                "id": issuer_id,
                "name":issuer_name,
                "creator":creator,
                "url":issuer_url,
                "email":issuer_email,
                "image":issuer_image
               }
            },
            "recipient":{
                "name": recipient_name,
                "hashed":False,
                "identity":recipient_email,
                "type":"email"
            }
         }
      }
   }
} 
    
        
    
    try:
        response = requests.post(
            endpoint
            + "/issue-credential-2.0/send-offer",
            json.dumps(json_model_rest),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                    
    except:
        raise    
    finally:             
        return connection
    

def get_record(recipient_identifier, cred_ex_id):
    #Check if connection exist betweeen issuer and recipient
    
    recipient_identifier = str(recipient_identifier)
    
    from badgeuser.models import BadgeUser
    token_issuer = BadgeUser.objects.get(email=recipient_identifier)  
    
    token = token_issuer.token
    
    connection=None

    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/json'}
       
    try:
        response = requests.get(
            endpoint
            + "/issue-credential-2.0/records/" + cred_ex_id,
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                  
    except:
        raise    
    finally:             
        return connection   
    

def get_badge_list(issuer_email, badgeclass):
    
    from django.db import connections,transaction
    
    cursor = connections['sqlite'].cursor()
    
    #Check if connection exist betweeen issuer and recipient
    connection = None
    badges = None
    
    issuer_email = str(issuer_email)
    
    from badgeuser.models import BadgeUser
    from issuer.models import BadgeInstance
    
       
    token_issuer = BadgeUser.objects.get(email=issuer_email)  
    
    teste = BadgeInstance.objects.using('sqlite').all().count()
    
    token = token_issuer.token
    
    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/ld+json'}
    

    try:
        response = requests.get(
            endpoint
            + "/issue-credential-2.0/records",
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
        
        created_at=connection['results'][0]['cred_ex_record']['created_at'] 
        old_json=''
        slug=''
        image=connection['results'][0]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['image']
        revoked='False'
        revocation_reason='None'
        created_by_id='1'
        issuer_id='1'
        recipient_identifier=connection['results'][0]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['recipient']['identity']
        acceptance=''
        salt=''
        narrative=connection['results'][0]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['criteria']['narrative']
        entity_id='1'
        entity_version='1.0'
        source=''
        source_url=''
        original_json=''
        issued_on='None'
        recipient_type='email'
        updated_at='None'
        updated_by_id= 'None'
        hashed='False'
        expires_at='None'
        user_id='None'
        cred_ex_id=connection['results'][0]['cred_ex_record']['cred_ex_id']

        
        query = "INSERT INTO issuer_badgeinstance (created_at, old_json, slug, image, revoked, revocation_reason, badgeclass_id, created_by_id, issuer_id, recipient_identifier, acceptance, salt, narrative, entity_id, entity_version, source, source_url, original_json, issued_on, recipient_type, updated_at, updated_by_id, hashed, expires_at, user_id, cred_ex_id) values('"+created_at+"','"+old_json+"','"+slug+"','"+image+"','"+revoked+"','"+revocation_reason+"','"+badgeclass+"','"+created_by_id+"','"+issuer_id+"','"+recipient_identifier+"','"+acceptance+"','"+salt+"','"+narrative+"','"+entity_id+"','"+entity_version+"','"+source+"','"+source_url+"','"+original_json+"','"+issued_on+"','"+recipient_type+"','"+updated_at+"','"+updated_by_id+"','"+hashed+"','"+expires_at+"','"+user_id+"','"+cred_ex_id+"')"
        
        cursor.execute(query)
        transaction.commit()
        
        # teste = BadgeInstance.objects.using('sqlite').raw(query)
        
    except:
        raise    
    finally:             
        return badges
    
    
    
