
import codecs
import json
import logging
from datetime import datetime

from pymongo import MongoClient

from src.connection_info import DefaultConnectionInfo
from src.utils import *


def ingest(connection_info: DefaultConnectionInfo, bucket_url: str, ) -> None:
    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    compounds_raw_collection = db['compounds_raw']

    today = datetime.today().strftime('%Y%m%d')
    with codecs.open(f"{bucket_url}/compounds.json", 'r', 'utf-8-sig') as f:
        data = json.load(f)

        # Add processed_date field
        for compound in data:
            compound['processed_date'] = today
        
        # Insert to "compounds_raw" collection
        res = compounds_raw_collection.insert_many(data)

        # Log
        logging.info(f"[INGEST] Ingested {len(res.inserted_ids)} documents into `{compounds_raw_collection.name}` collection.")
        logging.info(f"[INGEST] Collection `{compounds_raw_collection.name}` contains {compounds_raw_collection.estimated_document_count()} docs.")

    client.close()

def main():
    # Connection information to Mongo DB database
    connection_info = DefaultConnectionInfo()

    # Bucket storing raw data files
    bucket_url = get_bucket_url()

    ingest(connection_info, bucket_url)

if __name__ == "__main__":
    main()
