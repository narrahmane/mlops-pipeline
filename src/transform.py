
import logging
import os
from datetime import datetime

from pymongo import MongoClient
from rdkit import Chem

from src.connection_info import DefaultConnectionInfo
from src.utils import *


def transform(connection_info: DefaultConnectionInfo, bucket_url: str, date_to_process: str) -> None:
    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    compounds_raw_collection = db['compounds_raw']
    compounds_collection = db['compounds']

    today = datetime.today().strftime('%Y%m%d')
    success, error = 0, 0

    # Upsert compounds to golden "compounds" collection
    for compound in compounds_raw_collection.find({'processed_date': date_to_process}):
        # Dummy transformation 1 - Absolute image path
        compound['image'] = os.path.join(bucket_url, compound['image'])

        # Dummy transformation 3 - Update "processed_date"
        compound['processed_date'] = today

        # Enrichment 1 - Add number of atoms
        molecule = Chem.MolFromSmiles(compound['smiles'])
        compound['num_atoms'] = molecule.GetNumAtoms()

        res = compounds_collection.replace_one(
            {'_id': compound['_id']},
            compound,
            upsert=True
        )
        if res.acknowledged:
            success += 1
        else:
            error += 1

    # Log
    logging.info(f"[TRANSFORM] Transformed {success} documents successfully and {error} failed into {compounds_collection.name} collection.")
    logging.info(f"[TRANSFORM] Collection `{compounds_collection.name}` contains {compounds_collection.estimated_document_count()} docs.")

    client.close()


def main(date_to_process=datetime.today().strftime('%Y%m%d')):
    # Connection information to Mongo DB database
    connection_info = DefaultConnectionInfo()

    # Bucket storing raw data files
    bucket_url = get_bucket_url()

    transform(connection_info, bucket_url, date_to_process)

if __name__ == "__main__":
    main()
