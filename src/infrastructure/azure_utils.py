from azure.storage.blob import BlobServiceClient
import os

class AzureStorage:
    def __init__(self, connection_string):
        self.client = BlobServiceClient.from_connection_string(connection_string)
    
    def upload_file(self, file_path, container_name, blob_name=None):
        """Upload a file to Azure Blob Storage"""
        if not blob_name:
            blob_name = os.path.basename(file_path)
            
        blob_client = self.client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        return f"https://{self.client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    
    def download_file(self, blob_name, container_name, download_path):
        """Download a file from Azure Blob Storage"""
        blob_client = self.client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
            
    def list_containers(self):
        """List all containers in the storage account"""
        return [container.name for container in self.client.list_containers()]