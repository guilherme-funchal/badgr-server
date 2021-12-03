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
from django.db.models.query import QuerySet
from django.urls import reverse
from django.core.cache import cache

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


def get_badge_list(recipient_email):
    
    from django.db import connections,transaction
    from badgeuser.models import BadgeUser
    from issuer.models import BadgeInstance
    
    cursor = connections['default'].cursor()  
    
    recipient_email = str(recipient_email)        
    token_issuer = BadgeUser.objects.get(email=recipient_email)  
    token = token_issuer.token
    badges = BadgeInstance.objects.filter(user_id=token_issuer.id).delete()
    credentials = None
    json_model_rest = {}
    
    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/json'}
       
    try:
        response = requests.post(
            endpoint
            + "/credentials/w3c",
            json.dumps(json_model_rest),
            headers=header
        )
        
        response.raise_for_status()
        
        #Get credentials from Hyperledger Aries
        credentials = response.json()
    
        i = 0

        badge = []
        
        for credential in credentials['results']:
            
            created_at=credentials['results'][i]['cred_value']['issuanceDate']
            cred_ex_id=credentials['results'][i]['record_id']
            old_json='NULL'        
            slug='NULL'
            revoked='0'
            revocation_reason='NULL'
            updated_by_id= 'NULL'
            acceptance='Unaccepted'
            
            image=str(credentials['results'][i]['cred_value']['badge']['image'])
            badgeclass_id=str(credentials['results'][i]['cred_value']['badge']['badge'])
            created_by_id=str(credentials['results'][i]['cred_value']['badge']['issuer']['created'])
            issuer_id=str(credentials['results'][i]['cred_value']['badge']['issuer']['id'])
            recipient_identifier=str(credentials['results'][i]['cred_value']['recipient']['identity'])
            
            salt=str(credentials['results'][i]['cred_value']['badge']['salt'])
            narrative=str(credentials['results'][i]['cred_value']['badge']['criteria']['narrative'])           
            entity_id=str(credentials['results'][i]['cred_value']['badge']['identity'])
            entity_version=str(credentials['results'][i]['cred_value']['badge']['version'])
            source=str(credentials['results'][i]['cred_value']['badge']['related'])
            source_url=str(credentials['results'][i]['cred_value']['badge']['url'])
            original_json=str(credentials['results'][i]['cred_value']['badge']['targetCode'])
            issued_on=str(credentials['results'][i]['cred_value']['badge']['issuedOn'])
            recipient_type=str(credentials['results'][i]['cred_value']['badge']['recipient'])
            updated_at=str(credentials['results'][i]['cred_value']['badge']['issuedOn'])
            hashed=str(credentials['results'][i]['cred_value']['badge']['hashed'])
            expires_at=str(credentials['results'][i]['cred_value']['badge']['expires'])
            user_id=str(credentials['results'][i]['cred_value']['recipient']['uid'])
              
            #Insert data inside of table issuer_badgeinstance from Hyperledger Aries           
            query = "INSERT INTO `badgr`.`issuer_badgeinstance` (`created_at`, `old_json`, `image`, `revoked`, `badgeclass_id`, `created_by_id`, `issuer_id`, `recipient_identifier`, `acceptance`, `salt`, `entity_id`, `entity_version`, `source`, `issued_on`, `recipient_type`, `updated_at`, `hashed`, `expires_at`, `user_id`, `cred_ex_id`) VALUES ('"+created_at+"', '\"\"', '"+image+"', '"+revoked+"', '"+badgeclass_id+"', '"+created_by_id+"', '"+issuer_id+"', '"+recipient_identifier+"', '"+acceptance+"', '"+salt+"', '"+entity_id+"', '"+entity_version+"', '"+source+"', '"+issued_on+"', '"+recipient_type+"', '"+updated_at+"', '"+hashed+"', '"+expires_at+"', '"+user_id+"', '"+cred_ex_id+"')"                        
            cursor.execute(query)
            transaction.commit()  
            i += 1              
    except:
        raise    
    finally:
        
        badges = BadgeInstance.objects.filter(user_id=token_issuer.id).update(acceptance="Accepted")
        cache.clear()
        return credentials  
    
    
def remove_badge_recipient(recipient_email, cred_ex_id):
    from django.db import connections,transaction
    from badgeuser.models import BadgeUser
    from issuer.models import BadgeInstance
    
    connection = None
    
    recipient_email = str(recipient_email)        
    token_issuer = BadgeUser.objects.get(email=recipient_email)    
    token = str(token_issuer.token)
    cred_ex_id = str(cred_ex_id)
    
    
    header = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-Type': 'application/ld+json'}
    
    
    try:
        response = requests.delete(
            endpoint
            + "/credential/w3c/" + cred_ex_id,
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
                  
    except:
        raise    
    finally:             
        return

