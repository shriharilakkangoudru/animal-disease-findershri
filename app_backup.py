from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# --------------------------------
# Upload folder
# --------------------------------

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------
# Animal information
# --------------------------------

animal_profiles = {
    "Cow": {
        "breed": "Gir",
        "age": "4 years",
        "description": "Domestic cattle commonly raised for milk and farming."
    },

    "Dog": {
        "breed": "Labrador",
        "age": "3 years",
        "description": "Domestic dog commonly kept as a companion animal."
    },

    "Cat": {
        "breed": "Domestic Shorthair",
        "age": "2 years",
        "description": "Domestic cat commonly kept as a companion animal."
    },

    "Goat": {
        "breed": "Jamunapari",
        "age": "3 years",
        "description": "Domestic goat commonly raised for milk and meat."
    }
}


# --------------------------------
# Animal disease data
# --------------------------------

diseases = [

    # ==============================
    # COW
    # ==============================

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


    # ==============================
    # DOG
    # ==============================

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


    # ==============================
    # CAT
    # ==============================

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


    # ==============================
    # GOAT
    # ==============================

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
# Home page
# --------------------------------

@app.route("/")
def home():

    animals = sorted(animal_profiles.keys())

    return render_template(
        "index.html",
        animals=animals
    )


# --------------------------------
# Find disease using symptoms
# --------------------------------

@app.route("/find", methods=["POST"])
def find_disease():

    animal = request.form.get("animal", "")
    symptoms_text = request.form.get(
        "symptoms",
        ""
    ).lower()

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

    return render_template(
        "camera.html"
    )


# --------------------------------
# Receive camera image
# --------------------------------

@app.route("/api/scan", methods=["POST"])
def scan_animal():

    # Check image
    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message": "No image received"
        }), 400

    image = request.files["image"]

    # Check filename
    if image.filename == "":

        return jsonify({
            "success": False,
            "message": "No image selected"
        }), 400

    # --------------------------------
    # Get animal selected on camera page
    # --------------------------------

    animal = request.form.get(
        "animal",
        "Cow"
    )

    # Make sure animal exists
    if animal not in animal_profiles:
        animal = "Cow"

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
    # Animal information
    # --------------------------------

    profile = animal_profiles[animal]

    # --------------------------------
    # Find diseases for selected animal
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
    # Send result
    # --------------------------------

    return jsonify({

        "success": True,

        "message": "Animal image received successfully",

        "filename": filename,

        "image_url": "/static/uploads/" + filename,

        "animal": animal,

        "breed": profile["breed"],

        "age": profile["age"],

        "animal_description": profile["description"],

        "diseases": animal_diseases,

        "warning": "This is an educational project. Disease information is not a veterinary diagnosis."

    })


# --------------------------------
# Run Flask
# --------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )