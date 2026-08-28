from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.agents.omniclaim_agent import OmniClaimAgent
from src.agents.safecode_agent import SafeCodeAgent
from src.serverless.jobs_runner import NebiusServerlessJobRunner
from src.config import settings

app = FastAPI(
    title="Nebius x NVIDIA Global AI Hackathon Showcase",
    description="Multi-Agent AI Platform running NVIDIA Nemotron models on Nebius Token Factory & Serverless Infrastructure.",
    version="1.0.0"
)

omni_agent = OmniClaimAgent()
safe_agent = SafeCodeAgent()
job_runner = NebiusServerlessJobRunner()

class ClaimRequest(BaseModel):
    claim_id: str
    policy_holder: str
    amount: float
    description: str

class CodePatchRequest(BaseModel):
    code_snippet: str
    vulnerability: str

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nebius x NVIDIA Global AI Hackathon</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }
            h1 { color: #38bdf8; }
            .card { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }
            .badge { background: #7c3aed; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
            a { color: #38bdf8; text-decoration: none; }
            code { background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #f43f5e; }
        </style>
    </head>
    <body>
        <h1>🚀 Nebius x NVIDIA Global AI Hackathon Platform</h1>
        <div class="card">
            <h3>System Status: <span class="badge">ONLINE</span></h3>
            <p><strong>Inference Engine:</strong> Nebius Token Factory (OpenAI Compatible API)</p>
            <p><strong>Primary AI Models:</strong> NVIDIA Nemotron 3 Ultra (Reasoning) & Nemotron 3 Nano (Fast Calls)</p>
            <p><strong>Security Layer:</strong> NVIDIA OpenShell & Token Factory Sandboxes</p>
        </div>
        <div class="card">
            <h3>Interactive API Endpoints:</h3>
            <ul>
                <li><a href="/docs">Swagger UI API Documentation</a></li>
                <li><code>POST /api/claim/process</code> - Best Apps & Agents Track (OmniClaim)</li>
                <li><code>POST /api/code/patch</code> - Coding & Agentic Engineering Track (SafeCode)</li>
                <li><code>POST /api/serverless/job</code> - Nebius Serverless Async Jobs</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.post("/api/claim/process")
def process_claim_endpoint(claim: ClaimRequest):
    try:
        result = omni_agent.process_claim(claim.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/code/patch")
def code_patch_endpoint(req: CodePatchRequest):
    try:
        result = safe_agent.audit_and_patch(req.code_snippet, req.vulnerability)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/serverless/job")
def create_job_endpoint(claims: List[ClaimRequest]):
    try:
        claims_data = [c.model_dump() for c in claims]
        result = job_runner.run_batch_claims_job(claims_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
