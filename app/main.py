from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .services.qr import Qr
from .services.employee import EmployeeService
from . import database, models, schemas, crud, auth

class ProxyHeaderFixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        headers = {k.decode(): v.decode() for k, v in headers.items()}

        forwarded_host = headers.get("x-forwarded-host")
        if forwarded_host:
            # Use only the first value if multiple hosts are present
            clean_host = forwarded_host.split(",")[0].strip()
            headers["host"] = clean_host
            scope["headers"] = [(k.encode(), v.encode()) for k, v in headers.items()]
            scope["server"] = (clean_host, 443)
            scope["scheme"] = headers.get("x-forwarded-proto", "https")

        await self.app(scope, receive, send)


app = FastAPI(root_path='/sistema-qr')
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
        response = RedirectResponse(url=request.url_for("dashboard"), status_code=303)
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
    response = RedirectResponse(url=request.url_for("dashboard"), status_code=303)
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
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
    })

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
async def logout(request: Request):
    root_path = request.scope.get("root_path", "")
    response = RedirectResponse(url=root_path )
    response.delete_cookie("access_token")
    response.delete_cookie("remember_me")
    return response

@app.post("/generate-qr")
async def generate_qr(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    scheme = request.url.scheme
    hostname = request.url.hostname
    port = request.url.port
    
    form_data = await request.form()
    document_number = form_data.get("document_number")

    service = EmployeeService()
    cod_emp = service.get_employee_code(document_number)
    
    if not cod_emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")
    
    qr = Qr(str(request.base_url))
    qr_image, qr_path = qr.generate(cod_emp)
    
    return FileResponse(qr_path, media_type="image/png", filename=qr_image)

@app.get("/employee-data/{encoded_emp_codet}")
async def get_employee_data(
    request: Request,
    encoded_emp_codet: str
):
    emp_code = Qr().decode(encoded_emp_codet)
    
    service = EmployeeService()
    employee_data = service.get_employee_data(emp_code)
    
    return templates.TemplateResponse("employee_data.html", {
        "request": request,
        "employee_data": employee_data,
    })

@app.post("/create-admin")
def create_admin(db: Session = Depends(database.get_db)):
    admin = schemas.UserCreate(username="admin", password="contech369*-")
    db_admin = crud.create_user(db, admin)
    db_admin.is_admin = True
    db.commit()
    return {"status": "admin created"}


app = ProxyHeaderFixMiddleware(app)
