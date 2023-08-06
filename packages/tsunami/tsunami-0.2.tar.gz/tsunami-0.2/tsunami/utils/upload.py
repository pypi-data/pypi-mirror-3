import os
import uuid
import datetime





class UploadMinxin(object):

    def save_upload_file(self, name, path, prefix=None, ext=''):
        dir = datetime.datetime.now().strftime('%Y/%m/%d')
        if prefix:
            dir = prefix + '/' + dir
        file = datetime.datetime.now().strftime('%Y%m%d%H%M%S-') + uuid.uuid4().hex + ext

        pdir = os.path.join(path, dir)
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        pfile = os.path.join(pdir, file)

        data = self.request.files[name][0]['body']
        with open(pfile, 'wb') as f:
            f.write(data)

        return os.path.join(dir, file), len(data)

