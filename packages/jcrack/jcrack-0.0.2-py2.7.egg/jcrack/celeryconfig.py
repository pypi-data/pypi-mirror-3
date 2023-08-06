
import jconfig
config = jconfig.getConfig()

dburi = 'mysql://'+\
        config.get('db','user')  +':' +\
        config.get('db','passwd')+'@' +\
        config.get('db','host')  +'/' +\
        config.get('db','database')

BROKER_TRANSPORT='sqlalchemy'
BROKER_HOST=dburi
BROKER_URI=dburi

CELERY_RESULT_BACKEND='database'
CELERY_RESULT_DBURI=dburi
