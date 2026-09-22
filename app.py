from flask import Flask, render_template, request, jsonify
import os

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input,
    decode_predictions
)
from tensorflow.keras.utils import load_img, img_to_array


app = Flask(__name__)

# --------------------------------
# Upload folder
# --------------------------------

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------
# Load AI model
# --------------------------------

print("Loading AI model...")

model = MobileNetV2(weights="imagenet")

print("AI model loaded successfully!")


# --------------------------------
# Animal disease data
# --------------------------------

diseases = [

    {
        "animal": "Cow",
        "disease": "Mastitis",
        "symptoms": [
            "swollen udder",
            "milk changes",
            "fever",
            "painful udder"
        ],
        "description": "Inflammation of the udder in cattle.",
        "prevention": "Maintain clean milking equipment and good udder hygiene.",
        "action": "Contact a veterinarian for proper examination and treatment."
    },

    {
        "animal": "Cow",
        "disease": "Foot and Mouth Disease",
        "symptoms": [
            "fever",
            "mouth sores",
            "drooling",
            "lameness"
        ],
        "description": "A highly contagious viral disease affecting cloven-hoofed animals.",
        "prevention": "Maintain good biosecurity and follow veterinary vaccination programs.",
        "action": "Isolate the animal and contact a veterinarian immediately."
    },

    {
        "animal": "Cow",
        "disease": "Lumpy Skin Disease",
        "symptoms": [
            "skin lumps",
            "fever",
            "swollen lymph nodes",
            "skin lesions"
        ],
        "description": "A viral disease of cattle that can cause fever and characteristic skin nodules.",
        "prevention": "Use appropriate vaccination and insect-control measures under veterinary guidance.",
        "action": "Contact a veterinarian for examination and disease-control advice."
    },

    {
        "animal": "Dog",
        "disease": "Canine Parvovirus",
        "symptoms": [
            "vomiting",
            "diarrhea",
            "loss of appetite",
            "weakness"
        ],
        "description": "A serious contagious viral disease in dogs.",
        "prevention": "Keep vaccinations up to date and avoid infected animals.",
        "action": "Seek veterinary care promptly."
    },

    {
        "animal": "Dog",
        "disease": "Kennel Cough",
        "symptoms": [
            "coughing",
            "sneezing",
            "runny nose",
            "fever"
        ],
        "description": "A contagious respiratory illness commonly affecting dogs.",
        "prevention": "Maintain vaccination and reduce exposure to infected dogs.",
        "action": "Consult a veterinarian if symptoms continue."
    },

    {
        "animal": "Cat",
        "disease": "Feline Respiratory Infection",
        "symptoms": [
            "sneezing",
            "coughing",
            "runny nose",
            "watery eyes"
        ],
        "description": "An infection affecting the respiratory system of cats.",
        "prevention": "Maintain vaccination, hygiene and clean living conditions.",
        "action": "Consult a veterinarian if symptoms are severe."
    },

    {
        "animal": "Goat",
        "disease": "Pneumonia",
        "symptoms": [
            "coughing",
            "difficulty breathing",
            "fever",
            "nasal discharge"
        ],
        "description": "Inflammation or infection affecting the lungs.",
        "prevention": "Provide clean housing, good ventilation and avoid overcrowding.",
        "action": "Contact a veterinarian for diagnosis and treatment."
    }
]


# --------------------------------
# Animal profile
# --------------------------------

animal_profiles = {

    "Cow": {
        "breed": "Not determined from photo",
        "age": "Not determined from photo",
        "description": "Cattle/livestock animal."
    },

    "Dog": {
        "breed": "Not determined from photo",
        "age": "Not determined from photo",
        "description": "Domestic dog."
    },

    "Cat": {
        "breed": "Not determined from photo",
        "age": "Not determined from photo",
        "description": "Domestic cat."
    },

    "Goat": {
        "breed": "Not determined from photo",
        "age": "Not determined from photo",
        "description": "Domestic goat."
    }
}


# --------------------------------
# Home
# --------------------------------

@app.route("/")
def home():

    animals = sorted(animal_profiles.keys())

    return render_template(
        "index.html",
        animals=animals
    )


# --------------------------------
# Manual disease search
# --------------------------------

@app.route("/find", methods=["POST"])
def find_disease():

    animal = request.form.get("animal", "")
    symptoms_text = request.form.get("symptoms", "").lower()

    user_symptoms = [
        symptom.strip()
        for symptom in symptoms_text.split(",")
        if symptom.strip()
    ]

    results = []

    for disease in diseases:

        if disease["animal"].lower() != animal.lower():
            continue

        matched_symptoms = []

        for symptom in disease["symptoms"]:

            if symptom.lower() in symptoms_text:
                matched_symptoms.append(symptom)

        if matched_symptoms:

            percentage = round(
                len(matched_symptoms)
                / len(disease["symptoms"])
                * 100
            )

            results.append({
                "disease": disease,
                "matched_symptoms": matched_symptoms,
                "percentage": percentage
            })

    results.sort(
        key=lambda x: x["percentage"],
        reverse=True
    )

    return render_template(
        "result.html",
        animal=animal,
        symptoms=user_symptoms,
        results=results
    )


# --------------------------------
# Camera page
# --------------------------------

@app.route("/camera")
def camera():

    return render_template("camera.html")


# --------------------------------
# AI animal detection
# --------------------------------

def detect_animal(image_path):

    image = load_img(
        image_path,
        target_size=(224, 224)
    )

    image_array = img_to_array(image)

    image_array = image_array.reshape(
        (1, 224, 224, 3)
    )

    image_array = preprocess_input(
        image_array
    )

    predictions = model.predict(
        image_array,
        verbose=0
    )

    decoded = decode_predictions(
        predictions,
        top=10
    )[0]

    print("\nAI predictions:")

    for prediction in decoded:

        print(
            prediction[1],
            round(float(prediction[2]) * 100, 2),
            "%"
        )


    # --------------------------------
    # Animal keywords
    # --------------------------------

    dog_words = [
        "dog",
        "retriever",
        "terrier",
        "shepherd",
        "spaniel",
        "poodle",
        "husky",
        "malamute",
        "chihuahua",
        "pug",
        "beagle",
        "collie",
        "dalmatian",
        "boxer",
        "bulldog",
        "rottweiler",
        "doberman",
        "pinscher"
    ]

    cat_words = [
        "cat",
        "tabby",
        "tiger_cat",
        "egyptian_cat",
        "siamese"
    ]

    cow_words = [
        "ox",
        "cow",
        "water_buffalo",
        "buffalo"
    ]

    goat_words = [
        "goat",
        "ibex",
        "bighorn"
    ]


    # --------------------------------
    # Search predictions
    # --------------------------------

    for prediction in decoded:

        label = prediction[1].lower()
        confidence = float(prediction[2])

        # DOG

        if any(word in label for word in dog_words):

            return "Dog", confidence


        # CAT

        if any(word in label for word in cat_words):

            return "Cat", confidence


        # COW

        if any(word in label for word in cow_words):

            return "Cow", confidence


        # GOAT

        if any(word in label for word in goat_words):

            return "Goat", confidence


    return None, 0


# --------------------------------
# Receive image + AI scan
# --------------------------------

@app.route("/api/scan", methods=["POST"])
def scan_animal():

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message": "No image received."
        }), 400


    image = request.files["image"]


    if image.filename == "":

        return jsonify({
            "success": False,
            "message": "No image selected."
        }), 400


    # --------------------------------
    # Save image
    # --------------------------------

    filename = "animal_scan.jpg"

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    image.save(filepath)


    # --------------------------------
    # AI detection
    # --------------------------------

    try:

        animal, confidence = detect_animal(
            filepath
        )

    except Exception as error:

        print("AI ERROR:", error)

        return jsonify({
            "success": False,
            "message": "AI image analysis failed.",
            "error": str(error)
        }), 500


    # --------------------------------
    # Animal not detected
    # --------------------------------

    if animal is None:

        return jsonify({

            "success": False,

            "message": "The AI could not recognize Cow, Dog, Cat or Goat from this photo.",

            "image_url":
                "/static/uploads/" + filename

        }), 200


    # --------------------------------
    # Animal profile
    # --------------------------------

    profile = animal_profiles[animal]


    # --------------------------------
    # Diseases for detected animal
    # --------------------------------

    animal_diseases = []

    for disease in diseases:

        if disease["animal"] == animal:

            animal_diseases.append({

                "name": disease["disease"],

                "symptoms": disease["symptoms"],

                "description": disease["description"],

                "prevention": disease["prevention"],

                "action": disease["action"]

            })


    # --------------------------------
    # Return result
    # --------------------------------

    return jsonify({

        "success": True,

        "animal": animal,

        "confidence":
            round(confidence * 100, 2),

        "breed": profile["breed"],

        "age": profile["age"],

        "animal_description":
            profile["description"],

        "image_url":
            "/static/uploads/" + filename,

        "diseases":
            animal_diseases,

        "warning":
            "AI animal recognition is an educational feature. Disease information is reference information and is not a veterinary diagnosis."

    })


# --------------------------------
# Run
# --------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )