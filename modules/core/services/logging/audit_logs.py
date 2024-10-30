import json
import copy
from uuid import uuid4
from typing import List
from datetime import datetime
from modules.core.choices import AUDIT_LOGS_ACTIONS
from modules.core.services.azure.cosmosdb import CosmosDB
from modules.core.env import COSMOS_BASE_FASTAPI_AUDIT_LOG_CONTAINER



def generate_audit_log(objects: List[any], trigger_action: str):
    """
    This method will generate logs in the CosmosDB NoSQL
    for the given object.

    Log example:
        data = {
            'id': str(uuid4()),
            'date_create': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': AUDIT_LOGS_ACTIONS[trigger_action],
            'source': obj.__class__.__name__,
            'object_uuid': dict_obj['uuid'],
            'object_version': dict_obj['version'],
            'json_object': json.dumps(dict_obj, default=str, indent=4),
            'auth_user_id': user.id
        }

    Args:
        objects: List[any]: Any objects to be logged

    Author: Matheus Henrique (m.araujo)

    Date: 11th September of 2024

    Returns:
        None
    """
    items = []
    for obj in objects:
        dict_obj = obj
        if not isinstance(obj, dict):
            dict_obj = copy.deepcopy(obj).__dict__
            del dict_obj['_sa_instance_state']

        items.append({
            'id': str(uuid4()),
            'date_create': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': AUDIT_LOGS_ACTIONS[trigger_action],
            'source': obj.__class__.__name__,
            'object_uuid': dict_obj['uuid'],
            'object_version': dict_obj['version'],
            'json_object': json.dumps(dict_obj, default=str, indent=4),
            'auth_user_id': 'Must implement authentication in the application first'
        })

    client = CosmosDB()
    container = client.get_container(COSMOS_BASE_FASTAPI_AUDIT_LOG_CONTAINER)
    client.create_items(container=container, items=items)
