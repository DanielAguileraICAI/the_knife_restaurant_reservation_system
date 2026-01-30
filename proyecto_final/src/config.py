class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'
    MYSQL_DB='theknife_db'
    MYSQL_CHARSET = 'utf8mb4'


config = {
    'development': DevelopmentConfig
}

