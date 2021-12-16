import owncloud


class Storage():
    def __init__(self, host):
        self.oc = owncloud.Client(host)

    def connect(self, user, password):
        return self.oc.login(user, password)

    def disconnect(self):
        return self.oc.logout()

    def file_exist(self, file_path):
        try:
            file = self.oc.file_info(file_path)
            return file.file_type == 'file'

        except owncloud.owncloud.HTTPResponseError:
            return False

    def dir_exist(self, dir_path):
        try:
            dir = self.oc.file_info(dir_path)
            return dir.file_type == 'dir'

        except owncloud.owncloud.HTTPResponseError:
            return False

    def list(self, dir_path, depth=1):
        return self.oc.list(dir_path, depth)

    def get_file(self, file_path):
        try:
            return self.oc.get_file_contents(file_path)
        except owncloud.owncloud.HTTPResponseError:
            return False


    def get_link(self, file_path):
        shares = self.oc.get_shares(file_path)
        if len(shares) > 0:
            return shares[0].get_link()
        else:
            return self.oc.share_file_with_link(file_path).get_link()

    def mkdir(self, dir_path):
        return self.oc.mkdir(dir_path)

    def put_file(self, file_path, file_data):
        return self.oc.put_file_contents(file_path, file_data)

    def delete(self, file_path):
        return self.oc.delete(file_path)

    def __str__(self):
        return str(list(self.oc.get_config()))
