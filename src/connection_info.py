import os

class DefaultConnectionInfo:
    def __init__(self) -> None:
        self.db_url = self.get_default_mongodb_url()
        self.db_port = self.get_mongodb_port()

    def get_default_mongodb_url(self) -> None:
        # Retrieve url from env var
        return os.getenv('EXSCIENTIA_ASSESMENT_DB_URL', None)

    def get_mongodb_port(self) -> None:
        # Retrieve port from env var
        return os.getenv('EXSCIENTIA_ASSESMENT_DB_PORT', None)