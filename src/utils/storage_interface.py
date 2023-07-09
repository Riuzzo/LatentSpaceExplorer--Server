from storage import Storage
from storage_minIO import Storage_minio

class Storage_interface():
    storage_type = ""
    
    def __init__(self, host, access_key="", secret_key=""):
        if access_key == "" and secret_key == "":
            self.storage_type = "owncloud"
            self.storage = Storage(host)
        else:
            self.storage_type = "minio"
            self.storage = Storage_minio(host, access_key, secret_key)

    def connect(self, user, password):
        return self.storage.connect(user, password) if self.storage_type == "owncloud" else None
    
    def disconnect(self):
        return self.storage.disconnect() if self.storage_type == "owncloud" else None
    
    def file_exist(self, file_path, bucket_name=""):
        return self.storage.file_exist(file_path) if self.storage_type == "owncloud" else self.storage.file_exist(bucket_name=bucket_name, file_path=file_path)
    
    def dir_exist(self, dir_path="", bucket_name=""):
        return self.storage.dir_exist(dir_path=dir_path) if self.storage_type == "owncloud" else self.storage.dir_exist(bucket_name=bucket_name)
    
    def list(self, dir_path, bucket_name="", depth=1, prefix=None, recursive=False):
        return self.storage.list(dir_path=dir_path, depth=depth) if self.storage_type == "owncloud" else self.storage.list(bucket_name=bucket_name, prefix=prefix, recursive=recursive)
    
    def get_file(self, file_path, bucket_name=""):
        return self.storage.get_file(file_path) if self.storage_type == "owncloud" else self.storage.get_file(bucket_name=bucket_name, file_path=file_path)
    
    def get_link(self, file_path, bucket_name=""):
        return self.storage.get_link(file_path) if self.storage_type == "owncloud" else self.storage.get_link(bucket_name=bucket_name, file_path=file_path)
    
    def mkdir(self, dir_path="", bucket_name=""):
        return self.storage.mkdir(dir_path=dir_path) if self.storage_type == "owncloud" else self.storage.mkdir(bucket_name=bucket_name)
    
    def copy(self, source_path="", target_path="", bucket_name="", file_name="", new_bucket_name="", new_file_name=""):
        return self.storage.copy(source_path=source_path, target_path=target_path) if self.storage_type == "owncloud" else self.storage.copy(bucket_name=bucket_name, file_name=file_name, new_bucket_name=new_bucket_name, new_file_name=new_file_name)
    
    def put_file(self, file_path, file_data, bucket_name="", length=-1):
        return self.storage.put_file(file_path, file_data) if self.storage_type == "owncloud" else self.storage.put_file(bucket_name=bucket_name, file_name=file_path, file_data=file_data, length=length)
    
    def delete(self, file_path, bucket_name=""):
        return self.storage.delete(file_path) if self.storage_type == "owncloud" else self.storage.delete(bucket_name=bucket_name, file_name=file_path)