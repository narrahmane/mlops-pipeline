import os

from flask import Flask, request
from pymongo import MongoClient

from src.bestmodel import BestModel
from src.connection_info import DefaultConnectionInfo

app = Flask(__name__)

# Load best model for objective OBJ-1234 in-memory
global model
model = BestModel(DefaultConnectionInfo(), objectiveId="OBJ-1234")


@app.route('/')
def index():
  return "Hi Sash! Welcome to ml-serving project 😄"


@app.route('/predict')
def predict():
    """
    Predict number of atoms knowing molecular weight.
    Call in-memory best trained model form our database.

    Usage eg: curl -X GET "http://localhost:4049/predict?molecular_weight=330.445"
    """
    global model

    # Check if model is loaded. If not, try to dl it again.
    if not model.is_ready():
        model = BestModel(DefaultConnectionInfo(), objectiveId="OBJ-1234")
        if not model.is_ready():
            return "Sorry, this usecase model is not ready. The research team is working on a new model.", 404

    # Get input parameter from HTTP header
    molecular_weight = request.args.get('molecular_weight', default = None, type = float)
    if not molecular_weight:
        return "Argument `molecular_weight` required.", 400

    # Predict
    y_pred = model.predict([molecular_weight])

    return f"Predicted number of atoms: {y_pred}" 


@app.route('/bestmodel')
def bestmodel():
    """
    Get best model experiment

    Usage eg: curl -X GET "http://localhost:4049/bestmodel?objectiveId=OBJ-1234"
    """    

    global model

    # Check if model is loaded. If not, try to dl it again.
    if not model.is_ready():
         model = BestModel(DefaultConnectionInfo(), objectiveId="OBJ-1234")
         if not model.is_ready():
            return "Sorry, this usecase model is not ready. The research team is working on a new model.", 404
    
    return str(model.best_model), 200


@app.route('/compound')
def compound():
    """
    Get enriched compound by id.
    It removes the database id for security purpose.

    Usage eg: curl -X GET "http://localhost:4049/compound?id=1117973"
    """

    # Get compound id parameter from HTTP header
    compound_id = request.args.get('id', default = None, type = int)
    if not compound_id:
        return "Argument `id` required.", 400
    
    connection_info = DefaultConnectionInfo()
    client = MongoClient(f"mongodb://{connection_info.db_url}:{connection_info.db_port}")

    db = client['exscientia']
    compounds_collection = db['compounds']
    
    # Get enriched compound from `compounds` collection
    compound = compounds_collection.find_one({'compound_id': compound_id})
    
    # Compound not found
    if not compound:
        return f"Compound `{compound_id}` not found.", 404
    
    # Remove database id for security purpose
    del compound['_id']

    return str(compound), 200


if __name__ == '__main__':
    PORT = os.getenv("EXSCIENTIA_ASSESMENT_WEBAPP_SERVER_PORT", 4049)

    app.run(host="0.0.0.0", port=PORT, debug=True)
