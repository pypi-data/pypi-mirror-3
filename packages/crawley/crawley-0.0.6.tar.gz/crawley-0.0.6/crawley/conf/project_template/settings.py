import os 
PATH = os.path.dirname(os.path.abspath(__file__))

#Don't change this if you don't have renamed the project
PROJECT_NAME = "%(project_name)s"
PROJECT_ROOT = os.path.join(PATH, PROJECT_NAME)

DATABASE_ENGINE = 'sqlite'     
DATABASE_NAME = '%(project_name)s'  
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

SHOW_DEBUG_INFO = True
