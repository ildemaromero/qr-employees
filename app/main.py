from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import database, models, schemas, crud, auth

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Add current_user to template context for all responses
def add_current_user_to_context(request: Request):
    current_user = None
    try:
        # Try to get current user from cookie
        current_user = auth.get_current_user_from_request(request)
    except Exception:
        pass
    return {"current_user": current_user}

templates.env.globals.update(add_current_user_to_context=add_current_user_to_context)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, db: Session = Depends(database.get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    user = auth.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })
    
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    print("hey here")
    cedulas = crud.get_cedulas(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,  # Keep this for dashboard-specific usage
        "cedulas": cedulas
    })

@app.post("/cedula")
async def create_cedula(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    form_data = await request.form()
    cedula_number = form_data.get("cedula_number")
    crud.create_cedula(db, schemas.CedulaCreate(cedula_number=cedula_number))
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/users", response_class=HTMLResponse)
async def user_management(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = crud.get_users(db)
    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": current_user, 
        "users": users
    })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

@app.post("/create-admin")
def create_admin(db: Session = Depends(database.get_db)):
    admin = schemas.UserCreate(username="admin", password="admin123")
    db_admin = crud.create_user(db, admin)
    db_admin.is_admin = True
    db.commit()
    return {"status": "admin created"}
