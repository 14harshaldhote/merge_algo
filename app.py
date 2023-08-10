from roboflow import Roboflow
import json
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from googletrans import Translator
from gunicorn.app.base import BaseApplication
from model_loader import modelClassification, modelIdentification
import os
import uuid

#translator 
def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text


def get_classification_class(model, image_path):
    try:
        # Check if the image file exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        
        # Call the model's predict method and get the output as a dictionary
        output = model.predict(image_path, confidence=40, overlap=30).json()
        print("image path in classification funciton : ", image_path)
        # Get the value of the 'class' field from the output dictionary
        class_value = output['predictions'][-1]['class']

        # Generate a unique filename for saving the visualization image
        filename = str(uuid.uuid4()) + '.jpg'
        visualization_path = os.path.join("visualizations", filename)

        # Visualize the prediction and save the image
        model.predict(image_path, confidence=40, overlap=30).save(visualization_path)

        # Return the classification class and visualization path
        return class_value, visualization_path
    except Exception as e:
        # Handle the exception and return None
        print(f"Exception 1: An error occurred in classifiaction : {str(e)}")
        return None, None


def get_identification_class(model, image_path):
    try:
        # Check if the image file exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Call the model's predict method and get the output as a dictionary
        output = model.predict(image_path, confidence=40, overlap=30).json()

        # Check if predictions array is empty
        if 'predictions' in output and len(output['predictions']) > 0:
            # Get the value of the 'class' field from the output dictionary
            class_value = output['predictions'][-1]['class']
        else:
            # Set class_value as null if predictions array is empty
            class_value = None

        # Generate a unique filename for saving the visualization image
        filename = str(uuid.uuid4()) + '.jpg'
        visualization_path = os.path.join("visualizations", filename)
        
        # Visualize the predictions and save the image
        model.predict(image_path, confidence=40, overlap=30).save(visualization_path)

        # Delete the image files after use
        delete_image_file(image_path)
        
        # Return the value of the 'class' field and visualization path
        return class_value, visualization_path
    except Exception as e:
        # Handle the exception and return None
        print(f"Exception 2: An error occurred in identification : {str(e)}")
        return None, None


def runapp(image_path):
    # Load the models
    model1 = modelClassification
    model2 = modelIdentification

    # Get the predicted class values and visualization paths
    class1_value, visualization_path1 = get_classification_class(model1, image_path)

    if class1_value != 'healthy':
        class2_value, visualization_path2 = get_identification_class(model2, visualization_path1)

        # Print the predicted class values
        print("Classification class:", class1_value)
        print("Identification class:", class2_value)
        if class2_value is None:
            return class1_value, visualization_path1

        return class2_value, visualization_path2
    else:
        # Print the predicted class values
        print("Classification class:", class1_value)
        return class1_value, visualization_path1


def delete_image_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("Deleted image file:", file_path)
        else:
            print("Image file not found:", file_path)
    except Exception as e:
        print(f"Exception 3: An error occurred while deleting image file {file_path}: {str(e)}")




# API starting
app = Flask(__name__)
api = Api(app)


class ImageUpload(Resource):
    def post(self):
        if 'image' not in request.files:
            return jsonify({'result': 'failure', 'message': 'No image provided'})

        image = request.files['image']
        if image.filename == '':
            return jsonify({'result': 'failure', 'message': 'No image selected'})

        try:
            # Code that may raise an exception
            if image and image.filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                # Generate a unique filename for saving the image
                filename = str(uuid.uuid4()) + '.jpg'
                image_path = os.path.join("images", filename)
                print("image_path :: ",image_path)
                image.save(image_path)
                print("image_path :: ",image_path)

                res, visualization_path = runapp(image_path)
                print("visualization_path :: ",visualization_path)

                cause = "NULL"
                prevention = "NULL"
                solution = "NULL"

                # Delete the image files after use
                delete_image_file(image_path)
                delete_image_file(visualization_path)


                if res == "Target spot":
                    cause = "Target spot, or Corynespora leaf spot, is a fungal disease affecting various crops like tomatoes, soybeans, and cotton. It is caused by the fungus Corynespora cassiicola."
                    prevention = "Farmers can prevent target spot by planting resistant cultivars, practicing crop"
                    solution = "Manage target spot disease on tomato leaves by pruning infected foliage, improving air circulation, practicing proper watering at the base, using mulch, implementing crop rotation, considering fungicides if necessary, and monitoring plant health."

                elif res == "Leaf mold":
                    cause = "Leaf mold is primarily caused by a fungus called Fulvia fulva (formerly Cladosporium fulvum). It thrives in warm, humid conditions."
                    prevention = "To prevent leaf mold, farmers can use resistant varieties, practice crop rotation, ensure proper plant spacing for good air circulation, and avoid overhead irrigation."
                    solution = "If leaf mold occurs, farmers should remove and destroy infected plant material. Fungicides can be applied preventatively, but they should be used judiciously and as part of an integrated disease management strategy."

                elif res == "Late blight":
                    cause = "Late blight is a devastating disease affecting several crops, most notably tomatoes and potatoes. It is caused by a fungus-like oomycete pathogen called Phytophthora infestans. It spreads rapidly under cool, wet conditions."
                    prevention = "Farmers can prevent late blight by planting resistant varieties, practicing good sanitation, providing adequate plant spacing for airflow, and avoiding overhead irrigation."
                    solution = " If late blight occurs, farmers should promptly remove and destroy infected plants. Fungicides can be used preventatively, especially during periods of high disease pressure. Early detection and action are critical to managing this disease."

                elif res == "Curl virus":
                    cause = "Curl leaf, also known as leaf curl, is commonly caused by viral infections such as Tomato leaf curl virus or Peach leaf curl virus. It is often spread by insect vectors, particularly whiteflies."
                    prevention = "Farmers can prevent curl leaf by using disease-resistant varieties, controlling insect populations through integrated pest management (IPM) practices, and employing physical barriers such as nets or row covers."
                    solution = "Once curl leaf is established, there are no specific curative treatments. Infected plants should be removed and destroyed to prevent further spread. Future plantings should be carefully monitored for symptoms."

                elif res == "Spider mites":
                    cause = "Spider mites are tiny arachnids that infest a wide range of crops, including fruits, vegetables, and ornamental plants. They pierce plant tissues and feed on sap, causing damage."
                    prevention = "Farmers can prevent spider mite infestations by practicing good crop hygiene, providing adequate moisture levels, promoting beneficial insects that prey on mites, and using reflective mulches."
                    solution = "In case of spider mite infestations, farmers can employ biological controls like predatory mites or insecticidal soaps. If necessary, selective insecticides can be used, following proper application guidelines."

                elif res == "Mosaic virus":
                    cause = "Mosaic viruses are a group of viruses that affect a wide range of crops, including tomatoes, cucumbers, peppers, and many others. They are mainly transmitted through infected plant sap, insects, or contaminated tools."
                    prevention = "Farmers can prevent mosaic virus by using virus-free seeds or transplants, practicing strict sanitation measures, controlling insect vectors, and removing and destroying infected plants."
                    solution = "Unfortunately, there are no effective treatments for mosaic viruses once plants are infected. Therefore, prevention is crucial in managing this disease."

                elif res == "Healthy leaf":
                    return jsonify({'result': res, 'message': 'Your crop leaf is in healthy condition. However, to maintain this, ensure to follow the following practices'})
                                   
                elif res == "disease":
                    return jsonify({'result': res, 'message': 'Your crop leaf is in disease condition.'})
                
                elif res is None:
                    response = jsonify({'result': res, 'message': 'Please try other image'})
                    response.status_code = 400
                    return response

                else:
                    return jsonify({'result': res, 'message': 'Your crop is in healthy condition. However, to maintain this, ensure to follow the following practices'})
                # return jsonify({'result': res, 'cause': cause, 'prevention': prevention, 'solution': solution})
                return jsonify(
                    {
                        "result": res,
                        "message": {
                            "cause": cause,
                            "prevention": prevention,
                            "solution": solution,
                        },
                    }
                )
            else:
                response= jsonify({'result': 'failure', 'message': 'Invalid file format'})
                response.status_code = 400
                return response 
            # ...
        except Exception as e:
            # Code to handle the exception
            error_message = "Exception 4:An exception occurred in Image Upload : " + str(e)
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code = 500
            return response 
       

      
class ImageUploadHindi(Resource):
    def post(self):
        try:
            response = ImageUpload().post()
            if response.status_code == 200:
                response_data = response.get_json()
                translated_response_data = {}
                for key, value in response_data.items():
                    translated_response_data[key] = translate_text(value, 'hi')
                return jsonify(translated_response_data)
            else:
                return response
        except Exception as e:
            error_message = "Exception 5:An exception occurred: " + str(e)
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code == 500
            return response
            
class ImageUploadTamil(Resource):
    def post(self):
        try:
            response = ImageUpload().post()
            if response.status_code == 200:
                response_data = response.get_json()
                translated_response_data = {}
                for key, value in response_data.items():
                    translated_response_data[key] = translate_text(value, 'ta')  # Change 'hi' to 'ta' for Tamil
                return jsonify(translated_response_data)
            else:
                return response
        except Exception as e:
            error_message = "Exception 6:An exception occurred: " + str(e)
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code == 500
            return response

class ImageUploadFrench(Resource):
    def post(self):
        try:
            response = ImageUpload().post()
            if response.status_code == 200:
                response_data = response.get_json()
                translated_response_data = {}
                for key, value in response_data.items():
                    translated_response_data[key] = translate_text(value, 'fr')  # Change 'hi' to 'fr' for French
                return jsonify(translated_response_data)
            else:
                return response
        except Exception as e:
            error_message = "Exception 7:An exception occurred: " + str(e)
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code == 500
            return response


api.add_resource(ImageUploadFrench, '/upload/french')

api.add_resource(ImageUploadTamil, '/upload/tamil') 

api.add_resource(ImageUploadHindi, '/upload/hindi')

api.add_resource(ImageUpload, '/upload')

if __name__ == '__main__':
    
    port = 49999
    app.run(debug=True, port=port)
#     # Set the appropriate host and port for your local server
#     host = '192.168.43.66'  # or '127.0.0.1'
#     port = 8080

#     # Use the production WSGI server (Gunicorn)
#     from gunicorn.app.base import BaseApplication

#     class FlaskApplication(BaseApplication):
#         def __init__(self, app, options=None):
#             self.options = options or {}
#             self.application = app
#             super().__init__()

#         def load_config(self):
#             for key, value in self.options.items():
#                 self.cfg.set(key, value)

#         def load(self):
#             return self.application

#     options = {
#         'bind': f'{host}:{port}',
#         'workers': 4,  # Adjust the number of workers based on your server configuration
#         'threads': 2,  # Adjust the number of threads based on your server configuration
#         'accesslog': '-',  # Print access logs to stdout
#         'errorlog': '-'  # Print error logs to stdout
#     }

#     FlaskApplication(app, options).run()

# # API ending

