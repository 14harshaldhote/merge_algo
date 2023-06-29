from roboflow import Roboflow
import json
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from googletrans import Translator


# Loading models
rf1 = Roboflow(api_key="OMK13lODzeEz6X1NFfoF")
project1 = rf1.workspace().project("leaf-classification-0gekz")
modelClassification = project1.version(1).model

rf2 = Roboflow(api_key="kVjiNm6VQczdBaSdhwOg")
project2 = rf2.workspace().project("healthy_pest_disease")
modelIdentification = project2.version(4).model

#translator 
def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text


def get_classification_class(model, image_path):
    # Call the model's predict method and get the output as a dictionary
    output = model.predict(image_path, confidence=40, overlap=30).json()

    # Get the value of the 'class' field from the output dictionary
    class_value = output['predictions'][-1]['class']

    # Visualize your prediction
    model.predict(image_path, confidence=40, overlap=30).save("x.jpg")

    # Return the value of the 'class' field
    return class_value


def get_identification_class(model, image_path):
    # Call the model's predict method and get the output as a dictionary
    output = model.predict(image_path, confidence=40, overlap=30).json()
    print("output", output)
    # Get the value of the 'class' field from the output dictionary
    class_value = output['predictions'][-1]['class']

    # Visualize your predictions
    model.predict(image_path, confidence=40, overlap=30).save("z.jpg")

    # Return the value of the 'class' field
    return class_value


def runapp(image_path):
    # Load the models
    model1 = modelClassification
    model2 = modelIdentification

    # Get the predicted class values
    image_path2 = "x.jpg"

    class1_value = get_classification_class(model1, image_path)

    if class1_value != 'healthy':
        class2_value = get_identification_class(model2, image_path2)

        # Print the predicted class values
        print("Classification class:", class1_value)
        print("Identification class:", class2_value)
        return class2_value
    else:
        # Print the predicted class values
        print("Classification class:", class1_value)
        return class1_value


# Image_path = "6.jpg"
# runapp(image_path)

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
            if image and image.filename.lower().endswith('.jpg'):
                image.save("image.jpg")
                image_path = "image.jpg"
                res = runapp(image_path)
                cause = "NULL"
                prevention = "NULL"
                solution = "NULL"

                if res == "target spot":
                    cause = "Target spot, or Corynespora leaf spot, is a fungal disease affecting various crops like tomatoes, soybeans, and cotton. It is caused by the fungus Corynespora cassiicola."
                    prevention = "Farmers can prevent target spot by planting resistant cultivars, practicing crop"
                    solution = "Manage target spot disease on tomato leaves by pruning infected foliage, improving air circulation, practicing proper watering at the base, using mulch, implementing crop rotation, considering fungicides if necessary, and monitoring plant health."

                elif res == "Leaf mold":
                    cause = "Leaf mold is primarily caused by a fungus called Fulvia fulva (formerly Cladosporium fulvum). It thrives in warm, humid conditions."
                    prevention = "To prevent leaf mold, farmers can use resistant varieties, practice crop rotation, ensure proper plant spacing for good air circulation, and avoid overhead irrigation."
                    solution = "If leaf mold occurs, farmers should remove and destroy infected plant material. Fungicides can be applied preventatively, but they should be used judiciously and as part of an integrated disease management strategy."

                elif res == "late blight":
                    cause = "Late blight is a devastating disease affecting several crops, most notably tomatoes and potatoes. It is caused by a fungus-like oomycete pathogen called Phytophthora infestans. It spreads rapidly under cool, wet conditions."
                    prevention = "Farmers can prevent late blight by planting resistant varieties, practicing good sanitation, providing adequate plant spacing for airflow, and avoiding overhead irrigation."
                    solution = " If late blight occurs, farmers should promptly remove and destroy infected plants. Fungicides can be used preventatively, especially during periods of high disease pressure. Early detection and action are critical to managing this disease."

                elif res == "curl leaf":
                    cause = "Curl leaf, also known as leaf curl, is commonly caused by viral infections such as Tomato leaf curl virus or Peach leaf curl virus. It is often spread by insect vectors, particularly whiteflies."
                    prevention = "Farmers can prevent curl leaf by using disease-resistant varieties, controlling insect populations through integrated pest management (IPM) practices, and employing physical barriers such as nets or row covers."
                    solution = "Once curl leaf is established, there are no specific curative treatments. Infected plants should be removed and destroyed to prevent further spread. Future plantings should be carefully monitored for symptoms."

                elif res == "spider mite":
                    cause = "Spider mites are tiny arachnids that infest a wide range of crops, including fruits, vegetables, and ornamental plants. They pierce plant tissues and feed on sap, causing damage."
                    prevention = "Farmers can prevent spider mite infestations by practicing good crop hygiene, providing adequate moisture levels, promoting beneficial insects that prey on mites, and using reflective mulches."
                    solution = "In case of spider mite infestations, farmers can employ biological controls like predatory mites or insecticidal soaps. If necessary, selective insecticides can be used, following proper application guidelines."

                elif res == "Mosaic virus":
                    cause = "Mosaic viruses are a group of viruses that affect a wide range of crops, including tomatoes, cucumbers, peppers, and many others. They are mainly transmitted through infected plant sap, insects, or contaminated tools."
                    prevention = "Farmers can prevent mosaic virus by using virus-free seeds or transplants, practicing strict sanitation measures, controlling insect vectors, and removing and destroying infected plants."
                    solution = "Unfortunately, there are no effective treatments for mosaic viruses once plants are infected. Therefore, prevention is crucial in managing this disease."

                elif res == "healthy leaf":
                    return jsonify({'result': res, 'message': 'Your crop leaf is in healthy condition. However, to maintain this, ensure to follow the following practices'})
                else:
                    return jsonify({'result': res, 'message': 'Your crop is in healthy condition. However, to maintain this, ensure to follow the following practices'})
                return jsonify({'result': res, 'cause': cause, 'prevention': prevention, 'solution': solution})
            else:
                return jsonify({'result': 'failure', 'message': 'Invalid file format'})
            # ...
        except ExceptionType as e:
            # Code to handle the exception
            e="An exception occurred"
            print(e)

      
class ImageUploadHindi(Resource):
    def post(self):
        response = ImageUpload().post()
        if response.status_code == 200:
            response_data = response.get_json()
            translated_response_data = {}
            for key, value in response_data.items():
                translated_response_data[key] = translate_text(value, 'hi')
            return jsonify(translated_response_data)
        else:
            return response

class ImageUploadTamil(Resource):
    def post(self):
        response = ImageUpload().post()
        if response.status_code == 200:
            response_data = response.get_json()
            translated_response_data = {}
            for key, value in response_data.items():
                translated_response_data[key] = translate_text(value, 'ta')  # Change 'hi' to 'ta' for Tamil
            return jsonify(translated_response_data)
        else:
            return response

class ImageUploadFrench(Resource):
    def post(self):
        response = ImageUpload().post()
        if response.status_code == 200:
            response_data = response.get_json()
            translated_response_data = {}
            for key, value in response_data.items():
                translated_response_data[key] = translate_text(value, 'fr')  # Change 'hi' to 'fr' for French
            return jsonify(translated_response_data)
        else:
            return response

api.add_resource(ImageUploadFrench, '/upload/french')

api.add_resource(ImageUploadTamil, '/upload/tamil') 

api.add_resource(ImageUploadHindi, '/upload/hindi')

api.add_resource(ImageUpload, '/upload')

if __name__ == '__main__':
    port = 49999
    app.run(debug=True, port=port)
# API ending
