import ConfigParser

config = None

def getConfig():
    global config
    if not config:
        config = ConfigParser.RawConfigParser()
        config.read('/etc/jcrack.conf')
    return config
