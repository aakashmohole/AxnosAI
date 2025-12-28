from psycopg2 import pool

connection_pools = {}

def get_connection_pool(chat_id, db_url):
    if chat_id in connection_pools:
        return connection_pools[chat_id]
    
    new_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=3,
        dsn=db_url
    )
    connection_pools[chat_id] = new_pool
    return new_pool

