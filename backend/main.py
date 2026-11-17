# Imports
import io
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


# Settings 
# Build the path to the model relative to this file
# Current folder.__file__ = backend/main.py, so .parent.parent = project root.
MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
MODEL_PATH =  MODEL_DIR / "potato_cnn_model.keras"

# Must be the same size the model was trained on
IMG_SIZE = (128, 128) 

# Read the class names from notebook saved. the order matters
# the model outputs 3 numbers, and position 0, 1, 2 map to these names in order.
CLASS_NAMES = [
    line.strip()
    for line in (MODEL_DIR / "class_names.txt").read_text(encoding="utf-8")
    if line.strip()
]

# A simple dictionary to hold the model once it is loaded.
state = {}

# Startup / shutdown
@asynccontextmanager
async def lifespane(app: FastAPI):
    # Runs once when the server starts: load the model into memory.
    # Loading once is important, because loading on every request would be very slow.
    state['model'] = tf.keras.models.load_model(MODEL_PATH)
    yield           # the server runs which we are paused here
    state.clear()   # runs on shutdown: free the memory   

# Create  the API app and attach the starup logic above.
app = FastAPI(title='Potato Leaf Desease API')

def pretty(name: str) -> str:
    # Turn "Potato___Early_blight" into "Early Blight" for display
    return name.replace("Potato___", "").replace("_", " ").title()

# Endpoint 1: health check
@app.get("/health")
def health():
    # A quick way to check the server is alive and see which classes it knows.
    return {"status": "ok", "classes": CLASS_NAMES}

# Endpoint 2: prediction
@app.post("/predict")
def predict(file: UploadFile = File(...)):
    # Step 1: reject anything that is not a JPG or PNG.
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Please upload a JPG or PNG image.")

    # Step 2: open the uploaded bytes as a image, forcing 3 colour channels (RGB),
    # because the model expects RBG.
    try:
        img = Image.open(io.BytesIO(file.file.read())).convert("RGB") 
    except UnidentifiedImageError:
        # The file had an image extension but is not actually a valid image
        raise HTTPException(status_code=400, detail="File is not a valid image.")

    # Step 3: preprocess exactly like training.
    # - resize to 128x128
    # - convert to float32 numbers
    # - NO division by 255 here, because the model already had a Rescaling
    #   layer inside it (dividing again would break the predictions)
    x = np.array(img.resize(IMG_SIZE), dtype=np.float32)

    # Step 4: the model expects a batch of images, shape (batch, 128, 128, 3).
    # we have one image, so add a batch dimension: (128, 128, 3) -> (1, 128, 128, 3).
    x = np.expand_dims(x, axis=0)

    # Step 5: predict. The last layer is softmax, so we get 3 probabilities that
    # add up to 1. [0] picks the result for our single image
    probs = state['model'].predict(x, verbose=0)[0]

    # Step 6: the predicted class is the one with the highest probability.
    # That probility is the "model score".
    best = int(np.argmax(probs))

    # Step 7: send the result back as JSON. float() converts numpy numbers into
    # normal Python numbers, which JSON can handle.
    return {
        "predicted_class": CLASS_NAMES[best],
        "label": pretty(CLASS_NAMES[best]),
        "score": float(probs[best]),
        "probabilities": {pretty(n): float(p) for n, p in zip(CLASS_NAMES, probs)},
    }
