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


# load parameters from ./.docker/etc/settings_local.dev.py

host = settings.REST_ARIES['HOST']
port = settings.REST_ARIES['PORT']
wallet_prefix = settings.REST_ARIES['WALLET_PREFIX']
wallet_webhook_urls = settings.REST_ARIES['WALLET_WEBHOOK_URLS']
wallet_pass = settings.REST_ARIES['WALLET_PASS']
service_endpoint = settings.REST_ARIES['SERVICEENDPOINT']
endpoint = host + ":" + port



def create_connection(recipient_identifier, created_by): 
#   This function create connecions in Hyperledger Aries between  users

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
#   This function check connecions in Hyperledger Aries between  users
    
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
#   This function create invitation in Hyperledger Aries between to connect users
   
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
#   This function create connections in Hyperledger Aries between users from invites 

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
#   This function create issuer_did in Hyperledger Aries from token_user 
       
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
#   This function get connection_id from Hyperledger Aries to Badge server
    
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
            + "/connections?alias=" + email,
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
#   This function get credential in Json-ld format in Hyperledger Aries from Badge server
    teste = None
    connection = None
    
    created_by = self.created_by.email
    
    from badgeuser.models import BadgeUser
    issuer_user = BadgeUser.objects.get(email=created_by)
    
    issuancedate = str(self.issued_on)
    badge_name = str(self.badgeclass.name)
    badge_class = str(self.badgeclass.entity_id)
    badge_class_id = str(self.badgeclass.id)
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
    created_by_id = str(self.created_by_id)
    issuer_id = str(self.issuer_id)
    salt = str(self.salt)
    entity_id = str(self.entity_id)
    entity_version = str(self.entity_version)
    original_json = str(self.original_json)
    issued_on = str(issuancedate)
    recipient_type = str(self.recipient_type)
    hashed = str(self.hashed)
    old_json = None
    slug = None
    source_url = str(self.source_url)
    user_id = self.user_id
    expires_at = str(self.expires_at)
    source = str(self.source)
    expires_at = str(self.expires_at)
    issuancedate = issuancedate.replace('+00:00', 'Z')
    
    json_model_rest = {
       "connection_id":"2c05893e-c110-43bf-a3de-d510292b36bf",
   "filter":{
      "ld_proof":{
				 "options":{
            "proofType":"BbsBlsSignature2020"
         },
         "credential":{
            "@context":["https://www.w3.org/2018/credentials/v1","https://w3id.org/openbadges/v2" ], 
            "@protected": False,
					 "issuanceDate":"2021-11-30T13:59:47.491Z",
           "type": ["VerifiableCredential","PermanentResident", "Assertion"],
            "issuer":"did:key:" + issuer_did,
					  "credentialSubject":{
					  },
            "badge":{           
               "id":badge_id,
               "type":"BadgeClass",
               "name":badge_name,
               "image":badge_image,
               "description": description,
               "salt":salt,
               "expires":expires_at,
               "BadgeClass": badge_class,
               "issuedOn":issuancedate,
               "hashed":hashed,
               "badge": badge_class_id,
               "url":source_url,
               "recipient": recipient_type,
               "version":entity_version,
               "identity": entity_id,
               "badge": badge_class_id,                             
            #  "old_json":old_json,
            #  "slug":slug,
               "related": source,
               "targetCode":original_json,

               "criteria":{
                  "narrative":narrative
               },
               
               "issuer":{
                  "url":issuer_url,
                  "type":"Profile",
                  "id":issuer_id,
                  "name":issuer_name,
                  "email":issuer_email,
                  "image":issuer_image,
                  "created":created_by_id,
                  "creator":creator
               }
            },
            "recipient":{
               "hashed":False,
               "identity":recipient_email,
               "type":"email",
               "uid": user_id
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
#   This function get credential from Hyperledger Aries

    
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
    

def get_badge_list(issuer_email, badgeclass, badgeclass_id):
#   This function create data in table issuer_badgeinstance in auxiliary database sqlite from Hyperledger Aries

    from django.db import connections,transaction
    from badgeuser.models import BadgeUser
    from issuer.models import BadgeInstance
    
    id = str(badgeclass_id)
    
#   Create cursos to database sqlite
    cursor = connections['default'].cursor()  
    connection = None
    badges = None
    
#   Check if connection exist betweeen issuer and recipient   
    issuer_email = str(issuer_email)        
    token_issuer = BadgeUser.objects.get(email=issuer_email)  
    
    # badges = BadgeInstance.objects.filter(badgeclass_id=badgeclass_id).delete()
      
#   Clean data in table issuer_badgeinstance in database
    query_delete = "DELETE FROM issuer_badgeinstanceextension WHERE name='extensions:recipientProfile';"
    
    cursor.execute(query_delete)
    transaction.commit()

#   Clean data in table issuer_badgeinstance in database
    query_delete = "DELETE FROM issuer_badgeinstance WHERE badgeclass_id=badgeclass_id;"
    cursor.execute(query_delete)
    transaction.commit()

    
#   Get data from Hyperledger Aries    
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
        
        i = 0

#   Include data in table issuer_badgeinstance in auxiliary database sqlite       
        for conn in connection['results']:
            created_at=connection['results'][i]['cred_ex_record']['created_at'] 
            old_json='NULL'        
            slug='NULL'
            image=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['image'])
            revoked='0'
            revocation_reason='NULL'
            badgeclass_id=str(connection['results'][i]['cred_ex_record']['by_format']['cred_proposal']['ld_proof']['credential']['badge']['badge'])
            created_by_id=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['issuer']['created'])
            issuer_id=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['issuer']['id'])
            recipient_identifier=connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['recipient']['identity']
            acceptance='Unaccepted'
            salt=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['salt'])
            narrative=connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['criteria']['narrative']
            entity_id=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['identity'])
            entity_version=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['version'])
            source=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['related'])
            source_url=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['url'])
            original_json=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['targetCode'])
            issued_on=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['issuedOn'])
            recipient_type=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['recipient'])
            updated_at=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['issuedOn'])
            updated_by_id= 'NULL'
            hashed=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['hashed'])
            expires_at=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['badge']['expires'])
            user_id=str(connection['results'][i]['cred_ex_record']['by_format']['cred_offer']['ld_proof']['credential']['recipient']['uid'])
            cred_ex_id=connection['results'][i]['cred_ex_record']['cred_ex_id']
        
        #Insert data inside of table issuer_badgeinstance from Hyperledger Aries
            query = "INSERT INTO `badgr`.`issuer_badgeinstance` (`created_at`, `old_json`, `image`, `revoked`, `badgeclass_id`, `created_by_id`, `issuer_id`, `recipient_identifier`, `acceptance`, `salt`, `entity_id`, `entity_version`, `source`, `issued_on`, `recipient_type`, `updated_at`, `hashed`, `expires_at`, `user_id`, `cred_ex_id`) VALUES ('"+created_at+"', '\"\"', '"+image+"', '"+revoked+"', '"+badgeclass_id+"', '"+created_by_id+"', '"+issuer_id+"', '"+recipient_identifier+"', '"+acceptance+"', '"+salt+"', '"+entity_id+"', '"+entity_version+"', '"+source+"', '"+issued_on+"', '"+recipient_type+"', '"+updated_at+"', '"+hashed+"', '"+expires_at+"', '"+user_id+"', '"+cred_ex_id+"')"                        
            cursor.execute(query)
            transaction.commit()
            i += 1   
            
    except:
        raise    
    finally:             
        return badges
    
    
    
def remove_badge(entity_id, issuer_email):
    from django.db import connections,transaction
    from badgeuser.models import BadgeUser
    from issuer.models import BadgeInstance
    
    connection = None
    
    issuer_email = str(issuer_email)        
    token_issuer = BadgeUser.objects.get(email=issuer_email)
    cred = BadgeInstance.objects.get(entity_id=entity_id)
    cred_ex_id = str(cred.cred_ex_id)
    
    token = str(token_issuer.token)
    
    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/ld+json'}
    
    
    try:
        response = requests.delete(
            endpoint
            + "/issue-credential-2.0/records/" + cred_ex_id,
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                  
    except:
        raise    
    finally:             
        return
                  
    