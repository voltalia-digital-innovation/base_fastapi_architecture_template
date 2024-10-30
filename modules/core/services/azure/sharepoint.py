import io
from office365.runtime.http.http_method import HttpMethod
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from modules.core.env import (
    SHAREPOINT_DOMAIN, SHAREPOINT_PASSWORD, SHAREPOINT_USERNAME
)


class SharepointFile:
    """
    This class represents and have methods for a Azure Sharepoint

    Author: Matheus Henrique (m.araujo)

    Date: 9th October 2024
    """
    @staticmethod
    def get_binary(context, url: str):
        """
        Download binary file from Sharepoint

        Parameters:
            url: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        request = context.pending_request().execute_request_direct(request)

        file = None
        if request.status_code == 200:
            file = io.BytesIO(request.content)

        return file


class SharepointService:
    """
    This class have methods for a Azure Sharepoint interactions like
    list files, download and upload.

    Author: Matheus Henrique (m.araujo)

    Date: 9th October 2024
    """

    def _auth(
        self, url_path: str,
        sharepoint_username: str = SHAREPOINT_USERNAME,
        sharepoint_password: str = SHAREPOINT_PASSWORD
    ):
        """
        Azure Sharepoint Tenant authentication

        Parameters:
            url_path: str
            sharepoint_username: str
            sharepoint_password: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        # Initialize the client credentials
        user_credentials = UserCredential(
            sharepoint_username, sharepoint_password
        )

        # create client context object
        ctx = ClientContext(url_path).with_credentials(
            user_credentials)

        return ctx

    def create_sharepoint_folder(self, path: str, ctx: ClientContext):
        """
        Creates a folder in the sharepoint directory.

        Parameters:
            path: str
            ctx: ClientContext

        OBS: Sharepoint API accept to create only 1 level of folder by time (e.g: existante_path/new_folder is ok
        but existante_path/new_folder/other_new_folder fails)

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        if path:
            result = ctx.web.folders.add(path).execute_query()

            if result:
                return path

    def create_sharepoint_directory_with_subfolders(
            self, path: str, ctx, sharepoint_root_path: str):
        """
        Create folder and sub folders on a specific Azure Sharepoint Tenant

        Parameters:
            path: str
            ctx: ClientContext
            sharepoint_root_path: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        folders = path.split('/')
        full_path = f'{sharepoint_root_path}/{path}'

        if not self.__directory_exists_sharepoint(ctx, full_path):
            full_path = sharepoint_root_path
            for folder in folders:
                full_path = f'{full_path}/{folder}'
                self.create_sharepoint_folder(full_path, ctx)

        return full_path

    def __directory_exists_sharepoint(self, ctx: ClientContext, path: str):
        """
        Check if a directory exists

        Parameters:
            ctx: ClientContext
            path: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        try:
            folder = ctx.web.get_folder_by_server_relative_url(path)
            ctx.load(folder)
            ctx.execute_query()
            return True
        except Exception as e:
            return False

    def upload_to_sharepoint(
            self, folder_name: str, dir_file: str, file_name: str, url_path: str,
            sharepoint_username: str = None, sharepoint_password: str = None
    ):
        """
        Upload a single file on a specific Azure Sharepoint Tenant

        Parameters:
            folder_name: str
            dir_file: str
            file_name: str
            url_path: str
            sharepoint_username: str
            sharepoint_password: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024
        """
        ctx = self._auth(url_path, sharepoint_username, sharepoint_password)
        sp_relative_url = self.create_sharepoint_folder(folder_name, ctx)

        target_folder = ctx.web.get_folder_by_server_relative_url(
            sp_relative_url)

        with open(dir_file, 'rb') as content_file:
            file_content = content_file.read()
            target_folder.upload_file(file_name, file_content).execute_query()

    def download_file(self, file_path: str, url_path: str):
        """
        Download a single file from a specific Azure Sharepoint Tenant

        Parameters:
            file_path: str
            url_path: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024

        Returns: 
            BytesIO or None if file doesn't exists
        """
        ctx = self._auth(url_path)
        file = SharepointFile.get_binary(ctx, file_path)

        return file

    def __list_files_and_folders_in_directory(self, ctx: ClientContext, target_folder_url: str):
        """
        List files and folders on a specific Azure Sharepoint Tenant

        Parameters:
            ctx: ClientContext
            target_folder_url: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024

        Returns
            sh_files: FileCollection
        """
        root_folder = ctx.web.get_folder_by_server_relative_path(
            target_folder_url)

        sh_files = root_folder.get_files(True).execute_query()
        return sh_files

    def list_files_and_folders_in_directory(
            self, url_path: str, target_folder_url: str = None, search: str = None
    ):
        """
        List files and folders on a specific Azure Sharepoint Tenant

        Parameters:
            url_path: str
            target_folder_url: str
            search: str

        Author: Matheus Henrique (m.araujo)

        Date: 9th October 2024

        Returns
            sh_files: FileCollection
        """
        ctx = self._auth(url_path)

        sh_files = self.__list_files_and_folders_in_directory(
            ctx,
            target_folder_url
        )

        files = []
        for file in sh_files:
            path = file.serverRelativeUrl
            name = file.name
            file_obj = {
                'file_path': SHAREPOINT_DOMAIN + path,
                'file_relative_path': path,
                'file_name': name
            }

            if search and search not in path:
                continue

            files.append(file_obj)

        return files
