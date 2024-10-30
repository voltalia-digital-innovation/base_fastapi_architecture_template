import io
import os
import uuid
from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient
from modules.core.services.email.email import Email
from modules.core.services.utils.methods import string_to_hash256
from modules.core.models.AzureBlobStorage import AzureBlobStorageFile
from modules.core.env import (
    AZURE_VLTSTORAGESERVICE1_CONNECTION_STRING,
    AZURE_VLTSTORAGESERVICE1_DOMAIN, DJANGO_CONTENT_TYPE_ID_BASE_FASTAPI_API
)


class AzureBlobStorageService:
    """
    This class provide integration with Azure Blob Storage SDK
    Author: Matheus Henrique (m.araujo)
    """

    def create_blob_service_client(self) -> BlobServiceClient:
        """
        Create authenticated connection with Azure service
        Author: Matheus Henrique (m.araujo)
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_VLTSTORAGESERVICE1_CONNECTION_STRING)

        return blob_service_client

    def list_blob_containers(self, blob_service_client: BlobServiceClient):
        """
        List Azure Blob Storage Containers
        Author: Matheus Henrique (m.araujo)
        """
        containers = blob_service_client.list_containers(include_metadata=True)
        return containers

    def create_blob_container(
        self,
        blob_service_client: BlobServiceClient,
        container_name: str
    ) -> ContainerClient:
        """
        Create Azure Blob Storage Container
        Author: Matheus Henrique (m.araujo)
        """
        container_client = blob_service_client.create_container(
            name=container_name)
        return container_client

    def upload_blob_stream(
        self,
        blob_service_client: BlobServiceClient,
        container_name: str,
        file_name: str,
        file_content: io.BytesIO
    ):
        """
        Upload file to Azure Blob Storage Container
        Author: Matheus Henrique (m.araujo)
        """
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=file_name
        )

        blob_client_response = blob_client.upload_blob(
            file_content, blob_type="BlockBlob")

        return blob_client_response

    def get_or_create_azure_container(
            self, blob_service_client: BlobServiceClient, container_name: str
    ):
        """
        Will get or create Azure Blob Storage Container if it doesn't exist
        Author: Matheus Henrique (m.araujo)
        """
        containers = self.list_blob_containers(blob_service_client)

        containers_names = []
        for container in containers:
            containers_names.append(container['name'])

        if container_name not in containers_names:
            container = self.create_blob_container(
                blob_service_client, container_name)
            container_name = container.container_name

        return container_name

    def upload_files_to_azure_blob_storage(
            self,
            db: Session,
            blob_info: Dict,
            files: List[io.BytesIO]) -> List[str]:
        """
        Uploads each file in "files" to Azure Blob Storage.

        This method takes a dictionary 'blob_info' with 'user_id' and 'container_name' parameters
        to specify the user and container, and a list of uploaded files to be stored in Azure Blob Storage.
        It performs the upload and save the files informations in AzureBlobStorageFile.

        Author: Matheus Henrique (m.araujo)

        Args:
            - db: Session
            - blob_info (Dict): A dictionary containing the following parameters:
                - user_id (int): The user ID associated with the uploaded files.
                - container_name (str): The name of the Azure Blob Storage container.
                ## IMPORTANT ##: io.BytesIO have no "name" and "content_type" attributes by default.
                You must set it in the "io.BytesIO" object before calling this method!

            - files (List[io.BytesIO]): A list of io.BytesIO objects representing the files
                to be uploaded to Azure Blob Storage.

        Returns:
            uploaded_files_objs: List[dict]
        """
        blob_service_client = self.create_blob_service_client()

        # Get or create the azure blob storage container
        container_name = self.get_or_create_azure_container(
            blob_service_client, blob_info['container_name'])

        uploaded_files_objs = []
        # For each file...
        for file in files:
            if isinstance(file, io.BytesIO):
                try:
                    # Upload file to azure blob storage
                    file_name = file.name
                    file_extension = file_name.split('.')[-1]
                    hash256_filename = f"{string_to_hash256(file_name, random=True)}.{
                        file_extension}"
                    file_size = len(file.getvalue())
                    file_content_type = file.content_type
                    file_content = file.read()

                    response = self.upload_blob_stream(
                        blob_service_client,
                        container_name,
                        hash256_filename,
                        file_content
                    )

                    file_path = os.path.join(
                        AZURE_VLTSTORAGESERVICE1_DOMAIN,
                        container_name,
                        hash256_filename
                    )

                    # Save it's meta informations in the AzureBlobStorageFile
                    data = {
                        'date_update': datetime.now(),
                        'date_create': datetime.now(),
                        'is_active': True,
                        'uuid': str(uuid.uuid4()).replace('-', ''),
                        'original_file_name': file_name,
                        'name': hash256_filename,
                        'file_extension': file_extension,
                        'user_id': blob_info['user_id'],
                        'container_name': container_name,
                        'path': file_path.replace('\\', '/'),
                        'size': file_size,
                        'content_type': file_content_type,
                        'etag': response['etag'],
                        'request_id': response['request_id'],
                        'version': response['version'],
                    }

                    # Create the AzureBlobStorageFile on DB
                    azure_file = AzureBlobStorageFile(**data)
                    db.add(azure_file)
                    db.commit()

                    file.seek(0)
                    data['file'] = file
                    data['id'] = azure_file.id
                    uploaded_files_objs.append(data)
                except Exception as error:
                    print(
                        f"Error occurred when creating engine in Database class: {error}")
                    continue
        return uploaded_files_objs

    def notify_uploader_user(
        self,
        uploaded_files_names: List,
        files: List,
        uploader_user_email: str,
        error: bool = False
    ):
        """
        Will notify by e-mail the user who uploaded something to Azure Blob Storage Containers
        Author: Matheus Henrique (m.araujo)
        """
        template_name = 'azure_integration_files_upload_error.html' if error else 'azure_integration_files_uploaded.html'
        subject = 'The files upload has failed!' if error else 'The files have been uploaded!'
        render_vars = {
            'partial_or_all': 'All' if len(uploaded_files_names) == len(files) else 'Some of',
            'file_names': uploaded_files_names,
            'upload_date': datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

        Email().send_email(
            users=[uploader_user_email],
            template=template_name,
            system='base_api',
            subject=subject,
            render_vars=render_vars,
            django_content_type_id=DJANGO_CONTENT_TYPE_ID_BASE_FASTAPI_API
        )
