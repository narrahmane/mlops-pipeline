from pymongo import MongoClient

class BestModel():
    def __init__(self, connection_info, objectiveId) -> None:
        self.connection_info = connection_info
        self.objectiveId = objectiveId


        self.best_model, self.bias, self.weights = self.download_best_model()


    def download_best_model(self):
        """
        Download bias and weights for targeted objective from database.
        If no model exists for this objective, set bias and weights to None.
        """
        client = MongoClient(f"mongodb://{self.connection_info.db_url}:{self.connection_info.db_port}")

        db = client['exscientia']
        models_collection = db['models']

        # Get best model for this objective from database `models` collection
        best_model = models_collection.find_one({'objectiveId': self.objectiveId})

        # Store bias and weights
        bias, weights = None, None
        if best_model:
            bias = best_model['model']['bias']
            weights = best_model['model']['weights']

        return best_model, bias, weights


    def is_ready(self):
        """
        Check if model is ready to make predictions
        """
        return self.bias and self.weights


    def predict(self, X):
        """
        Predict estimated number of atoms in compound molecule.
        By definition, compound molecule has at least 2 atoms.
        """
        y_pred = 0.0;
        
        if self.is_ready():
            for x, w in zip(X, self.weights):
                y_pred += x * w
            y_pred += self.bias
        
        y_pred = max(2, round(y_pred))
        return y_pred
