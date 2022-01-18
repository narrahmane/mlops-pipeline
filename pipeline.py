import logging
from argparse import ArgumentParser

from src import deploy, ingest, train, transform


logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    # Parse required argument
    parser = ArgumentParser(description='Exscientia assesment ML ops pipelines.')

    # --steps required argument
    parser.add_argument(
        '--steps',
        required=True,
        type=str,
        choices=['INGEST+TRANSFORM', 'TRAIN+DEPLOY'],
        help='pipeline steps to trigger'
    )

    # Parse args
    args = parser.parse_args()

    # 1 - Ingest raw data from $EXSCIENTIA_ASSESMENT_BUCKET_URL/compounds.json to mongo db collection `compounds_raw`
    # 2 - Transform and enriched raw data from collection `compounds_raw` to `compounds` collection
    if args.steps == 'INGEST+TRANSFORM':
        ingest.main()
        transform.main()
    
    # 3 - Train model to predict atoms number using molecular weight from `compounds` enriched collection. Save experiment to `experiments` collection
    # 4 - Deploy model to `models` collection (if the model is best than current production model)
    elif args.steps == 'TRAIN+DEPLOY':
        experiment = train.main()
        deploy.main(experiment)
