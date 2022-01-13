import logging
import azure.functions as func

# Imports for image procesing
import io
from PIL import Image
from flask import Flask, jsonify

# Imports for prediction
from .predict import initialize, predict_image

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    results = "{}"
    try:
        # get and load image from POST
        image_bytes = req.get_body()    
        image = Image.open(io.BytesIO(image_bytes))
        
        # Load and intialize the model and the app context
        app = Flask(__name__)
        initialize()

        with app.app_context():        
            # prefict image and process results in json string format
            results = predict_image(image)
            jsonresult = jsonify(results)
            jsonStr = jsonresult.get_data(as_text=True)
            results = jsonStr

    except Exception as e:
        logging.info(f'exception: {e}')
        pass 

    # return results
    logging.info('Image processed. Results: ' + results)
    return func.HttpResponse(results, status_code=200)