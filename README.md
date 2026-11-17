# Potato Leaf Disease Classification

This project uses a convolutional neural network (CNN) to classify potato leaf
images as early blight, late blight, or healthy. The model is trained in a
Jupyter notebook and can be used by the backend prediction API.

## Project structure

```text
potato_leaf/
├── backend/
│   ├── main.py                 # FastAPI prediction API
│   └── requirements.txt        # Backend dependencies
├── data/                       # Local training images (not included in Git)
│   ├── Potato___Early_blight/
│   ├── Potato___Late_blight/
│   └── Potato___healthy/
├── frontend/
│   └── requirements.txt        # Streamlit and frontend client dependencies
├── model/
│   └── class_names.txt         # Class labels in model output order
├── notebook/
│   └── pd_cnn.ipynb            # Data exploration, training, evaluation
└── sample_images/
    └── image.png               # Sample image used by the notebook
```

Training creates `model/potato_cnn_model.keras`. The model file is excluded from
Git, so it is created locally by training the notebook or must be obtained
separately before using the prediction API. The frontend folder currently
contains its dependency list.

## Dataset

The dataset is not stored in this repository. Download it from Google Drive
**https://drive.google.com/file/d/1cxO1fh14c3fURg6407PX7Th14uVFYxxr/view?usp=drive_link**, extract it, and place the
three class folders directly inside the project's `data/` directory. Do not
leave the images inside an extra enclosing folder or leave the dataset as a
compressed archive.

The expected layout is:

```text
data/
├── Potato___Early_blight/
│   └── image files...
├── Potato___Late_blight/
│   └── image files...
└── Potato___healthy/
    └── image files...
```

Keep the folder names exactly as shown. The notebook reads the class labels
from these folder names, and the resulting label order is saved to
`model/class_names.txt`. The `data/` directory is ignored by Git; each person
who wants to train the model must download and add the dataset locally.

## Train the model

1. Download and extract the dataset into `data/` as described above.
2. From the project root, create and activate a Python virtual environment:

   ```bash
   python -m venv .venv
   ```

   Activate it on macOS/Linux with `source .venv/bin/activate`, or on Windows
   with `.venv\Scripts\activate`.

3. Install the notebook's Python dependencies:

   ```bash
   python -m pip install tensorflow numpy matplotlib pillow ipykernel
   ```

4. Open `notebook/pd_cnn.ipynb` in VS Code or Jupyter and select the environment
   you configured above. The notebook expects its working directory to be the
   project's `notebook/` folder; this lets it locate `data/`, `model/`, and
   `sample_images/` relative to the project root.
5. Run the notebook cells in order. It loads RGB images, resizes them to
   128 × 128, and creates an 80/20 training/validation split. Training uses
   image augmentation, class weights, early stopping, and learning-rate
   reduction. It can run for up to 60 epochs.

When training finishes, the notebook saves the trained model to
`model/potato_cnn_model.keras` and its output class order to
`model/class_names.txt`. The notebook includes evaluation on the validation
split; this is not a separate test set and does not guarantee performance on
new images.

## Backend

`backend/main.py` defines a FastAPI health check and image prediction endpoint.
Predictions require `model/potato_cnn_model.keras`; train the notebook first if
the file is not available. Install backend dependencies from the project root
with:

```bash
python -m pip install -r backend/requirements.txt
```

The prediction route is intended for JPG and PNG images and returns the
predicted class and class scores. The current backend startup code does not
connect its model-loading hook to the FastAPI application, so the API needs
that wiring corrected before predictions will work.
