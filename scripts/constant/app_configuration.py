import yaml
import os
from fastapi import FastAPI, APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


def load_yaml_file(file_path):
    data = None
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print("Exception while reading data from config file: {}".format(e))
    return data


config = load_yaml_file(os.path.join(os.getcwd(), 'conf/conf.yaml'))