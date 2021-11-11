import owncloud


class Storage():
    def __init__(self, host):
        self.oc = owncloud.Client(host)

    def connect(self, user, password):
        return self.oc.login(user, password)

    def disconnect(self):
        return self.oc.logout()

    def list(self, dir_path: str, depth: int = 1):
        return self.oc.list(dir_path, depth)

    def get_file(self, file_path):
        return self.oc.get_file_contents(file_path)

    def get_link(self, path: str):
        if self.oc.is_shared(path):
            return self.oc.get_shares(path)[0].get_link()
        else:
            return self.oc.share_file_with_link(path).get_link()

    def mkdir(self, dir_path: str):
        return self.oc.mkdir(dir_path)


    def put_file(self, file_path: str, data: str):
        return self.oc.put_file_contents(file_path, data)

    def delete(self, path):
        return self.oc.delete(path)

    def __str__(self):
        return str(list(self.oc.get_config()))



