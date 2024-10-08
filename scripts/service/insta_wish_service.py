from scripts.constant.app_configuration import app, APIRouter, File, UploadFile, Form
from scripts.models.insta_wish_model import LoginModel
from scripts.handler.insta_wish_handler import login_handler, upload_data, send_email_data
from typing import List, Optional
from scripts.wish_logger import get_logger

logger = get_logger()
router = APIRouter()


@router.post('/')
def home(login_payload: LoginModel):
    response = {"status": False, "message": "Error while running service"}
    try:
        response = login_handler(login_payload)
    except Exception as e:
        logger.exception("Exception while running service: {}".format(e))
    return response


@router.post('/upload')
def upload(users: Optional[str] = Form(None),  # Accepting a list of users directly from form data
            text: Optional[str] = Form(None),  # Accepting text from form data
            image: UploadFile = File(...),  # Accepting image file
            video: UploadFile = File(...)   # Accepting video file
           ):
    response = {"status": False, "message": "Error while running service"}
    try:
        response = upload_data(users, text, image, video)
    except Exception as e:
        logger.exception("Exception while running service: {}".format(e))
    return response


@router.post('/send-email')
def send_email(photo: UploadFile = File(...),
                recipientEmail: Optional[str] = Form(None),
                message: Optional[str] = Form(None)
                ):
    response = {"status": False, "message": "Error while running service"}
    try:
        response = send_email_data(photo, recipientEmail, message)
    except Exception as e:
        logger.exception("Exception while running service: {}".format(e))
    return response
