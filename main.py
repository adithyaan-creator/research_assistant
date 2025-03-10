import uuid
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Form, File, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from services.researcher import ResearcherService

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

@app.get("/", response_class=HTMLResponse)
async def get_input_page(request: Request):
    return JSONResponse(content={"message": "Success!"},
                        status_code=200)

@app.post("/research", response_class=HTMLResponse)
async def conduct_research(query: str = Body(None,embed=True)):

    research_id = str(uuid.uuid4())
    print(f"{research_id} generated")

    researcher_service_instance = ResearcherService()
    research_out = researcher_service_instance.research(query)
    lesson_plan_out = researcher_service_instance.generate_lesson_plan(research_id, research_out)
    out_data = {"course_title":query, "description":f"A course on {query}", "modules":lesson_plan_out}
    return JSONResponse(content={"message": "Success!", "research_id":research_id, 
                                "out":out_data},
                        status_code=200)

@app.get("/research", response_class=HTMLResponse)
async def get_research(query: str = Body(None,embed=True)):

    return JSONResponse(content={"message": "Success!"},
                        status_code=200)
