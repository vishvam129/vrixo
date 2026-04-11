# Vrixo AI

This folder contains all the AI models and inference pipelines that power Vrixo's photo magic features.

## Structure

```
ai/
├── models/           # Individual AI feature implementations
│   ├── background_removal.py
│   ├── upscaler.py         (coming soon)
│   ├── face_enhance.py     (coming soon)
│   ├── colorizer.py        (coming soon)
│   └── object_remove.py    (coming soon)
├── utils/            # Shared image processing utilities
│   └── image_utils.py
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup

```bash
# From the vrixo/ root
python3 -m venv venv
source venv/bin/activate
pip install -r ai/requirements.txt
```

## Running a Model

```bash
# Background removal example
python ai/models/background_removal.py --input path/to/photo.jpg --output path/to/result.png
```

## Free AI Models Used

| Feature | Model | License |
|---------|-------|---------|
| Background removal | RemBG / BiRefNet | MIT |
| Image upscaling | Real-ESRGAN | BSD-3 |
| Face enhancement | GFPGAN | Apache 2.0 |
| Colorization | DeOldify | MIT |
| Object removal | LaMa | Apache 2.0 |

All models are free and open-source.
