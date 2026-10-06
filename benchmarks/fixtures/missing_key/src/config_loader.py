def get_database_url(config: dict) -> str:
    # Bug: raises KeyError if host or port missing
    host = config['host']
    port = config['port']
    user = config.get('user', 'root')
    return f'postgres://{user}@{host}:{port}/db'
