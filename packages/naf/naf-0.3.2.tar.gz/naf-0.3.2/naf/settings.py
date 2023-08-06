import ConfigParser


class Settings(object):

    config = ConfigParser.ConfigParser()

    class ReturnType(object):
        key = None

        boolean_fields = ['show',]
        int_fields = ['timeout',]
        string_fields = ['timeout',]

        def __init__(self, key):
            self.key = key

        def __getattr__(self, name):
            if name in self.boolean_fields:
                return Settings.config.getboolean(self.key, name);
            elif name in self.int_fields:
                return Settings.config.getint(self.key, name);
            else:
                return Settings.config.get(self.key, name);
    
    success = ReturnType('Success')
    aborted = ReturnType('Aborted')
    failed  = ReturnType('Failed')

    def __init__(self, config_files):
        self.config.read(config_files)
