from fastapi import FastAPI

from fastapi_zero.routers import auth, users

app = FastAPI(title='FastAPI Zero', version='0.1.0')
app.include_router(users.router)
app.include_router(auth.router)
