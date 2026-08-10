from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import database
import httpx
import io
from pypdf import PdfReader
from docx import Document

app = FastAPI(title="Vertex 4D", description="Private 4D client profile portal")

# Add Session Middleware
SESSION_SECRET = os.getenv("VERTEX4D_SESSION_SECRET", "vertex4d-secret-key-change-me")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Dependency to get current user from session
def get_current_user(request: Request):
    user = request.session.get("user")
    return user

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request, "index.html", {"user": user})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.png")

# --- Authentication Routes ---

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")

@app.post("/register")
async def register(
    request: Request,
    team_name: str = Form(...),
    password: str = Form(...),
    member1_name: str = Form(...),
    member1_email: str = Form(...),
    member2_name: str = Form(None),
    member2_email: str = Form(None),
    member3_name: str = Form(None),
    member3_email: str = Form(None),
    challenge_desc: str = Form(None),
    photo_url: str = Form(None)
):
    # Collect members
    members = [{"name": member1_name, "email": member1_email}]
    if member2_name and member2_email:
        members.append({"name": member2_name, "email": member2_email})
    if member3_name and member3_email:
        members.append({"name": member3_name, "email": member3_email})
    
    success, message, team_id = database.create_team(team_name, password, members, challenge_desc, photo_url)
    
    if success:
        # Auto login after register
        team_data = database.get_team_by_id(team_id)
        request.session["user"] = team_data
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request, "auth/register.html", {"error": message})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    success, message, team_data = database.verify_login(email.strip(), password.strip())
    
    if success:
        request.session["user"] = team_data
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request, "auth/login.html", {"error": message})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# --- Protected Routes ---

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/course_home.html", {"user": user})

@app.get("/dashboard/phases/sketch", response_class=HTMLResponse)
async def sketch_phase(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/phases/sketch.html", {"user": user})

@app.get("/dashboard/roadmap", response_class=HTMLResponse)
async def roadmap(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "dashboard/roadmap.html", {"user": user})


@app.get("/dashboard/lab", response_class=HTMLResponse)
async def lab_home(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "lab/base.html", {"user": user})

@app.get("/dashboard/lab/synapmap", response_class=HTMLResponse)
async def synapmap(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/synapmap.html", {"user": user})

@app.get("/dashboard/lab/synapmap-test", response_class=HTMLResponse)
async def synapmap_test(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/synapmap_simple.html", {"user": user})


@app.get("/dashboard/lab/alex", response_class=HTMLResponse)
async def alex(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/alex.html", {"user": user})

@app.get("/dashboard/lab/billie", response_class=HTMLResponse)
async def billie(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "lab/billie.html", {"user": user})

@app.get("/dashboard/orbit", response_class=HTMLResponse)
async def orbit(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    teams = database.get_all_teams()
    return templates.TemplateResponse(request, "orbit.html", {"user": user, "teams": teams})

@app.get("/dashboard/bookings", response_class=HTMLResponse)
async def bookings(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "bookings.html", {"user": user})

# --- OpenAI API Proxy (Secure) ---

# API keys must come from environment variables.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ALEX_OPENAI_API_KEY = os.getenv("ALEX_OPENAI_API_KEY", "")

@app.post("/api/openai/chat")
async def openai_proxy(
    request: Request,
    payload: dict = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Secure proxy endpoint for OpenAI API calls.
    Requires user authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key is not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
            
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenAI API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alex/chat")
async def alex_proxy(
    request: Request,
    payload: dict = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Secure proxy endpoint for Alex API calls using a specific key.
    Requires user authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not ALEX_OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="Alex API key is not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {ALEX_OPENAI_API_KEY}"
                },
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
            
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenAI API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    content = ""
    filename = file.filename.lower()
    
    try:
        contents = await file.read()
        file_obj = io.BytesIO(contents)
        
        if filename.endswith('.pdf'):
            reader = PdfReader(file_obj)
            for page in reader.pages:
                content += page.extract_text() + "\n"
                
        elif filename.endswith('.docx'):
            doc = Document(file_obj)
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        elif filename.endswith('.txt') or filename.endswith('.md'):
            content = contents.decode('utf-8')
            
        else:
            # Fallback for other text-based files
            try:
                content = contents.decode('utf-8')
            except:
                return JSONResponse(
                    status_code=400, 
                    content={"error": "Unsupported file type. Please upload PDF, DOCX, or TXT."}
                )
                
        return {"filename": file.filename, "content": content.strip()}
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return JSONResponse(status_code=500, content={"error": f"Error processing file: {str(e)}"})


if __name__ == "__main__":
    database.init_database()
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
