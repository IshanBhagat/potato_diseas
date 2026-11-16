# Potato Leaf Disease Classification

This project trains a convolutional neural network (CNN) to classify potato leaf
images into three categories: early blight, late blight, and healthy.

## Project contents

- `pd_cnn.ipynb` — notebook for inspecting the data, training and evaluating the
  model, and trying a prediction.
- `data/` — local labeled images arranged in one folder per class (excluded
  from Git).
- `potato_cnn_model.keras` — generated Keras model (excluded from Git).
- `classification_report.txt` — class names in the model's output order (despite
  the filename, this file does not contain evaluation metrics).
- `image.png` and `leaf.jpg` — sample images.
- `requirements.txt` — Python package dependencies.

## Dataset

Place images in class-named subfolders under `data/`:

```text
data/
├── Potato___Early_blight/
├── Potato___Late_blight/
└── Potato___healthy/
```

The dataset is not included in Git; provide the image folders locally before
running the notebook.

The current dataset contains 2,152 images:

| Class | Images |
| --- | ---: |
| Early blight | 1,000 |
| Late blight | 1,000 |
| Healthy | 152 |

The healthy class is underrepresented. The notebook applies class weights during
training to reduce the effect of this imbalance.

## Setup and training

From the project directory, install the packages listed in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Open `pd_cnn.ipynb` in VS Code, select a Python environment with those packages
installed, and run the cells from top to bottom. The notebook loads images as
RGB, resizes them to 128 × 128, and uses an 80/20 training/validation split.
Training includes random image augmentation and may use a GPU when one is
available to TensorFlow.

The CNN uses four convolutional blocks and produces probabilities for the three
classes. The notebook can train for up to 50 epochs, with early stopping and
learning-rate reduction based on validation loss. The final model is saved as
`potato_cnn_model.keras`.

## Recorded evaluation

The saved notebook output reports approximately **91% validation accuracy**.
This is measured on the validation split, not on a separate test set, so it
should not be interpreted as test performance or as a guarantee for new images.

## Predict with the saved model

After installing the requirements, run this from the project directory to
classify an image such as `leaf.jpg`:

If `potato_cnn_model.keras` is not present, run the notebook's training cells
first to create it.

```python
from pathlib import Path 

import numpy as np
import tensorflow as tf
from PIL import Image

model = tf.keras.models.load_model("potato_cnn_model.keras")
class_names = Path("classification_report.txt").read_text(
    encoding="utf-8"
).splitlines()

with Image.open("leaf.jpg") as image:
    image = image.convert("RGB").resize((128, 128))

batch = np.expand_dims(np.asarray(image, dtype=np.float32), axis=0)
probabilities = model.predict(batch, verbose=0)[0]
predicted_index = int(np.argmax(probabilities))

print(
    f"{class_names[predicted_index]} "
    f"({probabilities[predicted_index]:.1%})"
)
```

The notebook's final cell also demonstrates prediction with `image.png`.