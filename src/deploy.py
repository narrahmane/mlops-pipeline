import logging

from pymongo import MongoClient

from src.connection_info import DefaultConnectionInfo


def is_new_best(connection_info, experiment):
    """
    Check if experiment is the new best.
    Experiment is considered best if it has a better scores during train, val and test.
    """

    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    models_collection = db['models']

    # Find current best model
    current_best_model = models_collection.find_one({'objectiveId': experiment['objectiveId']})

    is_best = False
    if not current_best_model:
        is_best = True

    else:
        if experiment['scores_train']['r_squared'] > current_best_model['scores_train']['r_squared'] and \
            experiment['scores_train']['rmse'] > current_best_model['scores_train']['rmse'] and \
            experiment['scores_val']['r_squared'] > current_best_model['scores_val']['r_squared'] and \
            experiment['scores_val']['rmse'] > current_best_model['scores_val']['rmse'] and \
            experiment['scores_test']['r_squared'] > current_best_model['scores_test']['r_squared'] and \
            experiment['scores_test']['rmse'] > current_best_model['scores_test']['rmse']:
            is_best = True

    # Log
    if is_best:
        logging.info(f"[DEPLOY] New best experiment found `{experiment['experiment_id']}`.\n")
    else:
        logging.info(f"[DEPLOY] Experiment`{experiment['experiment_id']}` not best as current deployed model.\n")


    client.close()

    return is_best


def deploy_experiment(connection_info, experiment):
    """
    Deploy experiment as new model.
    """

    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    models_collection = db['models']

    # Insert experiment to the `experiments` collection
    models_collection.replace_one({'objectiveId': experiment['objectiveId']}, experiment, upsert=True)

    # Log
    logging.info(f"[DEPLOY] Deployed new experiment to production `{experiment['experiment_id']}`.\n")

    client.close()

    return experiment


def main(experiment):
    connection_info = DefaultConnectionInfo()

    is_best = is_new_best(connection_info, experiment)

    if is_best:
        deploy_experiment(connection_info, experiment)

    return is_best

if __name__ == "__main__":
    main()
