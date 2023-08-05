import os
import mimetypes
import tempfile
import urllib2

from socialtext import exceptions
from socialtext.resources.base import Manager
from socialtext.urls import make_data_url


class UploadManager(Manager):
    """
    Upload files to the Socialtext Appliance.
    """
    def create(self, filename_or_url):
        """
        Upload a local or remote file to the Socialtext appliance.
        
        :param: filename_or_url: Either the path to a file on the local
                                 file system or a URL that points to the file.
        :rtype: An ID-hash string
        """
        
        file_path = filename_or_url
        
        # really basic check to see if a URL was provided.
        is_url = (filename_or_url.find("http") == 0)
        
        if is_url:
            # get the filename from the end of the URL
            file_name = filename_or_url[filename_or_url.rfind('/') + 1:]
            
            # GET the file at the URL
            file_req = urllib2.Request(filename_or_url)
            file_resp = None
            
            try:
                file_resp = urllib2.urlopen(file_req)
            except urllib2.HTTPError, exc:
                raise exceptions.from_urllib2_exception(exc)
                
            # some URLs might not have an extension
            # so let's use the Content-Type header
            # just to be safe
            file_type = file_resp.info().gettype()
            
            # get the file extension based off mimetype
            # includes the . prefix
            file_ext = mimetypes.guess_extension(file_type)
            
            # create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            temp_file_path = os.path.join(temp_dir, file_name + file_ext)
            
            # create a file in the temporary directory
            temp_file = open(temp_file_path, "wb")
            
            # stream the URL response to the temp file
            chunk_size = 16 * 1024
            while True:
                chunk = file_resp.read(chunk_size)
                if not chunk:
                    break
                temp_file.write(chunk)
            
            # we need to close the file so it can be opened
            # for reading
            temp_file.close()
            
            file_path = temp_file_path
            
        
        file_path = os.path.expanduser(file_path)
        files = { "file": open(file_path, "rb") }
        
        url = make_data_url("uploads")
        resp, content = self.api.client.post(url, files=files)
        
        return content['id']  # the hash-ID
