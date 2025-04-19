import json
from difflib import SequenceMatcher

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS (required if using with frontend like Streamlit or React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load assessment data
try:
    with open("shl_assessments.json") as f:
        assessments_data = json.load(f)
except Exception as e:
    print(f"Error loading assessment data: {e}")
    assessments_data = []

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def recommend_assessments(query, max_results=10):
    keywords = ["python", "sql", "java", "cognitive", "personality", "communication", "reasoning", "analyst"]
    durations = {"short": 20, "medium": 40, "long": 60}
    preferred_duration = None

    for d in durations:
        if d in query.lower():
            preferred_duration = durations[d]
            break
    for num in [15, 20, 25, 30, 35, 40, 45, 50, 60]:
        if str(num) in query:
            preferred_duration = num
            break

    results = []
    for assessment in assessments_data:
        score = 0
        for kw in keywords:
            if kw in query.lower() or similar(query, kw) > 0.5:
                if kw in assessment["type"].lower() or kw in assessment["name"].lower():
                    score += 1
        if preferred_duration:
            duration_value = int(assessment["duration"].split()[0])
            if duration_value <= preferred_duration:
                score += 1
        if score > 0:
            results.append((score, assessment))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return [res[1] for res in results[:max_results]]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.api_route("/recommend", methods=["GET", "POST"])
async def recommend_endpoint(request: Request, query: str = Query(default="")):
    try:
        if request.method == "GET":
            if not query:
                return JSONResponse(content={"error": "Query parameter is missing"}, status_code=400)
        else:
            data = await request.json()
            query = data.get("query", "")
            if not query:
                return JSONResponse(content={"error": "No query provided"}, status_code=400)

        recommendations = recommend_assessments(query)

        return {
            "recommendations": [
                {
                    "name": a["name"],
                    "url": a["url"],
                    "remote": a["remote"],
                    "adaptive": a["adaptive"],
                    "duration": a["duration"],
                    "type": a["type"]
                }
                for a in recommendations
            ]
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
