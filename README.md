# Potato Leaf Disease Classification

This project trains a CNN to classify potato leaf images into:
- Early blight
- Late blight
- Healthy

It includes:
- a training notebook for model development
- a FastAPI backend for predictions
- a Streamlit frontend for uploading images and viewing results

## Project structure

```text
potato_leaf/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI prediction API
│   └── requirements.txt         # Backend dependencies
├── data/                        # Training dataset (local, not committed)
│   ├── Potato___Early_blight/
│   ├── Potato___Late_blight/
│   └── Potato___healthy/
├── frontend/
│   ├── app.py                   # Streamlit UI
│   └── requirements.txt         # Frontend dependencies
├── model/
│   ├── class_names.txt          # Class order used by the trained model
│   └── potato_cnn_model.keras   # Trained CNN (created locally)
├── notebook/
│   └── pd_cnn.ipynb             # Training and evaluation notebook
├── sample_images/
│   ├── image.png                # Example test image
│   └── leaf.jpg                 # Example test image for quick preview                     # optional zipped dataset
├── .gitignore
├── README.md
└── venv/                        # local virtual environment (optional)
```

## Prerequisites

- Python 3.10+ recommended
- A working internet connection to install packages
- Git and a terminal or VS Code terminal

## 1) Set up the environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required Python packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
python -m pip install -r frontend/requirements.txt
```

If you want to run the notebook locally as well, also install Jupyter support:

```bash
python -m pip install jupyter ipykernel matplotlib numpy pillow tensorflow scikit-learn
```

## 2) Prepare the dataset

The dataset is not included in the repository. Download it from the Google Drive link below and extract it into the `data/` folder:

https://drive.google.com/file/d/1cxO1fh14c3fURg6407PX7Th14uVFYxxr/view?usp=drive_link

Expected structure:

```text
data/
├── Potato___Early_blight/
├── Potato___Late_blight/
└── Potato___healthy/
```

Important:
- Keep the folder names exactly as shown.
- Do not put the images inside an extra parent folder.
- Keep the dataset in `data/` so the notebook can read it correctly.

## 3) Train the model

Open `notebook/pd_cnn.ipynb` in VS Code or Jupyter.

Run the notebook cells in order. The notebook:
- loads the images from `data/`
- resizes them to 128 x 128
- performs an 80/20 train-validation split
- trains a CNN with augmentation, class weighting, early stopping, and learning rate reduction
- saves the model as `model/potato_cnn_model.keras`
- saves class labels to `model/class_names.txt`

After training, verify the model files exist:

```bash
ls model/
```

You should see:
- `potato_cnn_model.keras`
- `class_names.txt`

## 4) Start the backend API

From the project root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend exposes:
- `GET /health` to check service status
- `POST /predict` to classify a JPG or PNG image

Test the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

## 5) Start the Streamlit frontend

Open a second terminal and run:

```bash
streamlit run frontend/app.py --server.port 8501
```

Then open:

http://localhost:8501

Upload a potato leaf image and the app will call the backend and show the predicted class, confidence score, probability bars, and agronomy guidance.

If the frontend says it cannot reach the backend, confirm that the `uvicorn` process is still running on port 8000.

## 6) Quick notebook image check

The notebook includes a quick prediction cell that tries to load an example image. You can use either of these sample files:

```text
sample_images/image.png
sample_images/leaf.jpg
```

If you want to use your own single test image, update the notebook cell to point to it, for example:

```python
image_path = Path("sample_images") / "leaf.jpg"
```

The notebook also contains a fallback message that says to place an image named `leaf.jpg` next to the notebook; in this project, the sample images are kept under `sample_images/`, so that is the correct place to test images without changing the project layout.

## Troubleshooting

### Model not found
If `model/potato_cnn_model.keras` is missing, run the notebook again to train the model.

### Backend errors
If `/predict` returns an error:
- confirm that the model exists
- confirm that `uvicorn` is running
- check that the uploaded file is a valid JPG or PNG

### Frontend connection issue
If the Streamlit app cannot connect to the backend:
- make sure the backend is running on port 8000
- set `API_URL` if needed, for example:

```bash
API_URL=http://127.0.0.1:8000 streamlit run frontend/app.py --server.port 8501
```

## Notes

- The model file and dataset are created locally and are not meant to be committed to Git.
- The folder names in `data/` must exactly match the class names used during training.
- The notebook and the API both expect the model class output order to match `model/class_names.txt`.
