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

app = FastAPI()

origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = methods,
    allow_headers = headers    
)

model_dir = "model_v2.h5"
model = load_model(model_dir)

classes = np.array(['alang_alang', 'andong', 'jambu_biji', 'jarong', 'kumis_kucing',
'kunyit', 'lengkuas', 'lidah_buaya', 'mengkudu', 'pacar_air',
'saga', 'sambiloto', 'seledri', 'serai', 'sirih'
])

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

    return {
        "Prediction": predicted_class,
        "Score": f"{model_score:0.2f} %"
    }
    
if _name_ == "_main_":
    port = int(os.environ.get('PORT', 8080))
    run(app, host="0.0.0.0", port=port)