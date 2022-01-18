import json
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from src.connection_info import DefaultConnectionInfo


def fetch_data_from_database(connection_info: DefaultConnectionInfo):
    """
    Fetch all enriched data from compounds collection.
    It returns pandas dataframe containing following fields:
        - molecular_weight
        - num_atoms
        _ _ids
    """

    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    compounds_collection = db['compounds']
    data = compounds_collection.find({}, projection=['_id', 'molecular_weight', 'num_atoms'])

    # Transform to pandas dataframe
    df = pd.DataFrame(data)

    # Extract useful features, metadata and target for training
    X = df[['molecular_weight']]
    y = df['num_atoms']
    metadata = df[['_id']]

    return X, y, metadata, X.describe()


def create_train_val_test_sets(X, y, metadata):
    """
    Create train, validation and test sets.
    For each set, it returns:
        - X:        (n_observations, n_features)    => data
        - y:        (n_observations, 1)             => target
        - metadata: (n_observations)                => database ids for retrieval purpose
    """

    X = X.to_numpy().reshape(-1, 1)
    y = y.to_numpy().reshape(-1, 1)
    metadata = metadata.to_numpy().reshape(-1)

    # Create TEST set
    X_train_val, X_test, y_train_val, y_test, idx_train_val, idx_test = train_test_split(X, y,
        np.arange(y.shape[0]),
        test_size=0.33, random_state=42, shuffle=True)
    
    metadata_train_val = metadata[idx_train_val]

    # Create TRAIN and VALIDATION set
    X_train, X_val, y_train, y_val, idx_train, idx_val = train_test_split(X_train_val, y_train_val,
        np.arange(y_train_val.shape[0]),
        test_size=0.33, random_state=42, shuffle=True)

    # Metadata splitting
    meta_train = metadata_train_val[idx_train]
    meta_val = metadata_train_val[idx_val]
    meta_test = metadata[idx_test]

    return X_train, y_train, meta_train, \
         X_val, y_val, meta_val, \
         X_test, y_test, meta_test


def evaluate(X, y, model, mode : str ='train'):
    """
    Evaluate Linear Regression scores:
        - R^2
        - Root Mean Square Error
    """

    # Prediction
    y_pred = model.predict(X)

    # R^2 metric
    r_squared = model.score(X, y)
    
    # Root Mean Squared Error metric
    rmse = mean_squared_error(y, y_pred, squared=False)

    logging.info(f"[{mode.upper()}] Model evaluation\n\tR^2 score: {r_squared}\n\tRMSE score: {rmse}")

    return r_squared, rmse


def train(X, y):
    """
    Train and evaluate using Linear Regression.
    The model uses the compound molecular weight to predict the number of atoms it contains.
    Those two are higly linearly correlated so we can expect a high score with this simple baseline model.
    """

    # Train a Linear Regression model
    model = LinearRegression().fit(X, y)
    scores = evaluate(X, y, model, mode='train')

    return model, scores


def push_experiment_to_database(
    connection_info,
    model,
    meta_train, meta_val, meta_test,
    statistics,
    train_r_squared, train_rmse,
    val_r_squared, val_rmse,
    test_r_squared, test_rmse
    ):
    """
    Create experiment tracking object. It encapsulates:
        - experiment objective
        - train, val and test scores
        - train, val and test set data ids
        - full dataset descriptive statistics ('count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max')
        - model type, bias and weights
    """

    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    experiments_collection = db['experiments']

    # Experiment object creation
    experiment_id = f"exp_{datetime.today().strftime('%Y%m%d_%H%M%S')}_{test_r_squared}_{test_rmse}"

    experiment = {
        'experiment_id': experiment_id,

        'objectiveId': 'OBJ-1234',
        'objective': 'Predict number of atoms from compound molecular weight.',
        
        # TRAIN + VAL + TEST descriptive statisticss
        'descriptive_statistics': json.loads(statistics.to_json()),

        # TRAIN
        "scores_train": {
            'r_squared': train_r_squared,
            'rmse': train_rmse
        },
        'compound_ids_train': [str(_id) for _id in meta_train.tolist()],

        # VAL
        'scores_val': {
            'r_squared': val_r_squared,
            'rmse': val_rmse
        },
        'compound_ids_val': [str(_id) for _id in meta_val.tolist()],

        # TEST
        'scores_test': {
            'r_squared': test_r_squared,
            'rmse': test_rmse
        },
        'compound_ids_test': [str(_id) for _id in meta_test.tolist()],

        # MODEL
        'model': {
            'type': model.__class__.__name__,
            'bias': model.intercept_.reshape(-1)[0],
            'weights': model.coef_.reshape(-1).tolist(),
        }
    }

    # Insert experiment to the `experiments` collection
    experiments_collection.insert_one(experiment)

    # Log
    logging.info(f"[TRAINING] Added a new experiment `{experiment_id}` into {experiments_collection.name} collection.\n {experiment}")

    client.close()

    return experiment


def main():
    connection_info = DefaultConnectionInfo()

    # Fetch data from mongo db `compounds` collection
    X, y, metadata, statistics = fetch_data_from_database(connection_info)

    # Split train, val and test set
    X_train, y_train, meta_train, \
        X_val, y_val, meta_val, \
         X_test, y_test, meta_test = create_train_val_test_sets(X, y, metadata)


    # Training
    model, scores_train = train(X_train, y_train)

    # Test on val set
    scores_val = evaluate(X_val, y_val, model, mode='val')

    # Test on test set
    scores_test = evaluate(X_test, y_test, model, mode='test')

    print(statistics)
    # Save experiment to database
    experiment = push_experiment_to_database(
        connection_info,
        model,
        meta_train, meta_val, meta_test,
        statistics,
        *scores_train,
        *scores_val,
        *scores_test
    )

    return experiment

if __name__ == "__main__":
    main()
