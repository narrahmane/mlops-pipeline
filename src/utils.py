import os

def get_bucket_url():
    return os.getenv('EXSCIENTIA_ASSESMENT_BUCKET_URL', None)