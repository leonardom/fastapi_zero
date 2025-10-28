from fastapi import FastAPI

from fastapi_zero.routers import auth, todos, users

app = FastAPI(title='FastAPI Zero', version='0.1.0')
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)
