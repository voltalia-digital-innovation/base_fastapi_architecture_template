from typing import Dict, List
import azure.cosmos.container as ContainerProxy
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
from modules.core.env import (
    COSMOS_CONNECTION_STRING, COSMOS_BASE_FASTAPI_DATABASE, COSMOS_KEY
)


class CosmosDB:
    """
    This class have methods to handle CosmosDB iteractions

    Author: Matheus Henrique (m.araujo)
    """

    def __init__(self) -> None:
        self.HOST = COSMOS_CONNECTION_STRING
        self.MASTER_KEY = COSMOS_KEY
        self.DATABASE_ID = COSMOS_BASE_FASTAPI_DATABASE

    def get_container(self, container_id: str):
        """
        Retrieve the desired CosmosDB container

        Author: Matheus Henrique (m.araujo)
        """
        client = cosmos_client.CosmosClient(
            self.HOST, {'masterKey': self.MASTER_KEY})

        db = client.create_database_if_not_exists(id=self.DATABASE_ID)

        container = db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path='/id', kind='Hash'))

        return container

    def create_items(self, container: ContainerProxy, items: List[Dict]):
        """
        Create CosmosDB items in a container

        Author: Matheus Henrique (m.araujo)
        """
        created_items = []
        for item in items:
            created_items.append(container.create_item(body=item))
        return created_items

    def upsert_items(self, container: ContainerProxy, items: List[Dict]):
        """
        Upsert CosmosDB items to a container

        Author: Matheus Henrique (m.araujo)
        """
        created_items = []
        for item in items:
            created_items.append(container.upsert_item(body=item))
        return created_items

    def read_item(self, container: ContainerProxy, uuid: str):
        """
        Read container CosmosDB item

        Author: Matheus Henrique (m.araujo)
        """
        response = container.read_item(item=uuid, partition_key=uuid)
        return response

    def read_items(self, container, max_item_count: int = 10):
        """
        Read container CosmosDB items

        Author: Matheus Henrique (m.araujo)
        """
        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing generations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(container.read_all_items(
            max_item_count=max_item_count))

        return item_list

    def read_all_items(self, container):
        """
        Read all container CosmosDB items

        Author: Matheus Henrique (m.araujo)
        """
        # enable_cross_partition_query should be set to True as the container is partitioned
        items = list(container.query_items(
            query="SELECT * FROM r",
            parameters=[],
            enable_cross_partition_query=True
        ))

        return items

    def query_items_by_user_id(self, container, user_id):
        """
        query all items from user_id

        Author: Matheus Henrique (m.araujo)

        Args:
            container (str): Azure container name
            user_id (int): auth_user id

        Returns:
            List[any]: list of Azure CosmosDB items
        """
        # enable_cross_partition_query should be set to True as the container is partitioned
        items = list(container.query_items(
            query="SELECT * FROM r WHERE r.user_id=@user_id",
            parameters=[
                {"name": "@user_id", "value": user_id}
            ],
            enable_cross_partition_query=True
        ))

        return items

    def query_items_where_in_id(self, container, uuid_list, is_in: bool = True):
        """
        This method will query all items that is IN or NOT (based on the "is_in" aparameter)
        in the cosmosdb container.

        Author: Matheus Henrique (m.araujo)
        """
        query = "SELECT * FROM c WHERE " +\
            f"{'' if is_in else 'NOT'} ARRAY_CONTAINS(@id, c.id)"

        items = list(container.query_items(
            query=query,
            parameters=[
                {"name": "@id", "value": uuid_list}
            ],
            enable_cross_partition_query=True
        ))

        return items

    def delete_item(self, container, uuid):
        """
        Delete CosmosDB item

        Author: Matheus Henrique (m.araujo)
        """
        response = container.delete_item(item=uuid, partition_key=uuid)

        return response

    def delete_items(self, container, uuids: List[str]):
        """
        Delete CosmosDB items

        Author: Matheus Henrique (m.araujo)
        """
        for id in uuids:
            container.delete_item(item=id, partition_key=id)
