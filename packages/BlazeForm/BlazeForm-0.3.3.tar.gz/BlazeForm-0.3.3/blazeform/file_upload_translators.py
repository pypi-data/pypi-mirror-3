    
class BaseTranslator(object):
    
    def __init__(self, file_name, content_type, content_length):
        self.file_name = file_name
        self.content_type = content_type
        self.content_length = content_length
    
    @property
    def is_uploaded(self):
        return self.file_name is not None

class WerkzeugTranslator(BaseTranslator):
    
    def __init__(self, value):
        BaseTranslator.__init__(self, value.filename, value.content_type, value.content_length)
