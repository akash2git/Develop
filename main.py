from scripts.constant.app_configuration import app
from scripts.service.insta_wish_service import router as login

app.include_router(login)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000)
