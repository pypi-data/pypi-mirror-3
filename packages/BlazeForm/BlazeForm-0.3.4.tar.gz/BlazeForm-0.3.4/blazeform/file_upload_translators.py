
class BaseTranslator(object):

    def __init__(self, file_name, content_type, content_length):
        self.file_name = file_name
        self.content_type = content_type
        self.content_length = content_length

    @property
    def is_uploaded(self):
        # if something is there for the filename, assume the file is uploaded.
        # If its None, empty string, False, etc., the file was not uploaded.
        return bool(self.file_name)

class WerkzeugTranslator(BaseTranslator):

    def __init__(self, value):
        BaseTranslator.__init__(self, value.filename, value.content_type, value.content_length)
