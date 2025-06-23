from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import database, models, schemas, crud, auth
from .services.qr import Qr

BASE_URL = "127.0.0.1:5000/employee-data/"

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Add current_user to template context for all responses
def add_current_user_to_context(request: Request):
    current_user = None
    try:
        current_user = auth.get_current_user_from_request(request)
    except Exception:
        pass
    return {"current_user": current_user}

templates.env.globals.update(add_current_user_to_context=add_current_user_to_context)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    remember_me = request.cookies.get("remember_me")
    if remember_me == "true":
        response = RedirectResponse(url="/dashboard", status_code=303)
        return response
    
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
    remember_me = form_data.get("remember-me") == "on"
    print(f"this remember me {remember_me}")
    if remember_me:
        response.set_cookie(
            key="remember_me",
            value="true",
            max_age=30*24*60*60,
            httponly=True,
            # secure=True,
            samesite="lax"
        )
    response.set_cookie(key="access_token", 
                        value=f"Bearer {access_token}", 
                        # secure=True,
                        httponly=True)
    
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
        "user": current_user,
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
    response.delete_cookie("remember_me")
    return response

@app.post("/generate-qr")
async def generate_qr(
    request: Request,
    # db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(auth.get_current_user)
):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Forbidden")
    
    form_data = await request.form()
    document_number = form_data.get("document_number")
    
    qr = Qr(BASE_URL)
    qr_image, qr_path = qr.generate(document_number)
    
    return FileResponse(qr_path, media_type="image/png", filename=qr_image)

@app.get("/employee-data/{encoded_document}")
async def get_employee_data(
    request: Request,
    encoded_document: str
):
    qr = Qr(BASE_URL)
    document_number = qr.decode(encoded_document)
    
    # Mock data - replace with your actual database query
    employee_data = {
        "codigo_trabajador": "EMP-12345",
        "nombre_completo": "Juan Pérez",
        "ci": document_number,
        "cargo": "Desarrollador Senior",
        "sede": "Oficina Central",
        "status": "Activo"
    }
    
    return templates.TemplateResponse("employee_data.html", {
        "request": request,
        "employee_data": employee_data,
    })

@app.post("/create-admin")
def create_admin(db: Session = Depends(database.get_db)):
    admin = schemas.UserCreate(username="admin", password="admin123")
    db_admin = crud.create_user(db, admin)
    db_admin.is_admin = True
    db.commit()
    return {"status": "admin created"}
