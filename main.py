from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
from tensorflow import expand_dims
from tensorflow.nn import softmax
from io import BytesIO
from PIL import Image
import numpy as np
from json import dumps
from uvicorn import run
import firebase_admin
from firebase_admin import credentials, firestore
from collections import OrderedDict

app = FastAPI()

origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers
)

model_dir = "model_v2.h5"
model = load_model(model_dir)

classes = np.array(['alang_alang', 'andong', 'jambu_biji', 'jarong', 'kumis_kucing',
                    'kunyit', 'lengkuas', 'lidah_buaya', 'mengkudu', 'pacar_air',
                    'saga', 'sambiloto', 'seledri', 'serai', 'sirih'])

# Initialize Firebase Admin SDK with service account
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.get("/")
async def root():
    return {"message": "Herbal Plants API"}

@app.post("/predict/image")
async def create_upload_file(file: bytes = File(...)):
    image = Image.open(BytesIO(file))
    
    img = np.asarray(image.resize((224, 224)))[..., :3]

    x = img_to_array(img)
    x /= 255
    x = np.expand_dims(x, axis=0)

    images = np.vstack([x])

    predictions = model.predict(images, batch_size=1)
    score = softmax(predictions[0])

    predicted_class = classes[np.argmax(score)]
    model_score = np.max(score) * 100

    if model_score < 10.0:  # Threshold for confidence level
        return {
            "Prediction": "Tumbuhan tidak cocok",
            "Score": f"{model_score:0.2f} %"
        }

    # Get plant information from Firestore based on predicted class
    doc_ref = db.collection("Tanaman").document(predicted_class)
    doc = doc_ref.get()
    if doc.exists:
        plant_data = doc.to_dict()
        ordered_plant_data = OrderedDict([
            ("namaTumbuhan", plant_data.get("informasi").get("namaTumbuhan")),
            ("deskripsi", plant_data.get("informasi").get("deskripsi")),
            ("caraPengobatan", plant_data.get("informasi").get("caraPengobatan")),
            ("caraPengobatan2", plant_data.get("informasi").get("caraPengobatan2")),
            ("caraPengobatan3", plant_data.get("informasi").get("caraPengobatan3")),
            ("caraPengobatan4", plant_data.get("informasi").get("caraPengobatan4"))
        ])
        # Menghapus kunci yang memiliki nilai None
        ordered_plant_data = {k: v for k, v in ordered_plant_data.items() if v is not None}
        return {
            "Prediction": predicted_class,
            "Score": f"{model_score:0.2f} %",
            "PlantInfo": {
                "informasi": ordered_plant_data
            }
        }
    else:
        return {
            "Prediction": predicted_class,
            "Score": f"{model_score:0.2f} %",
            "PlantInfo": "Plant information not found"
        }
