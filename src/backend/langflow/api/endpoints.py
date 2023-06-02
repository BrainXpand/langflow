import logging
from importlib.metadata import version

from fastapi import APIRouter, HTTPException, Response
from starlette.responses import HTMLResponse, JSONResponse
import html

from langflow.api.schemas import (
    ExportedFlow,
    GraphData,
    PredictRequest,
    PredictResponse,
)
from langflow.interface.run import process_graph_cached
from langflow.interface.types import build_langchain_types_dict

# build router
router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/all")
def get_all():
    return build_langchain_types_dict()

@router.get("/logs", response_class=HTMLResponse)
async def logs_endpoint():
    try:
        with open('stdout.log', 'r') as f:
            stdout = f.readlines()
        with open('stderr.log', 'r') as f:
            stderr = f.readlines()
    except FileNotFoundError:
        return HTMLResponse("<h1>No logs have been created yet</h1>")

    content = """
    <style>
    .logs {
        display: flex;
        justify-content: space-around;
    }
    .stdout, .stderr {
        width: 45%;
        overflow-x: auto;
        white-space: pre-wrap;
    }
    </style>
    <script src="https://unpkg.com/ansi_up"></script>
    <script>
    document.addEventListener('DOMContentLoaded', (event) => {
        const ansi_up = new AnsiUp();
        const stdout_container = document.getElementById('stdout');
        const stderr_container = document.getElementById('stderr');
        stdout_container.innerHTML = ansi_up.ansi_to_html(stdout_container.innerText);
        stderr_container.innerHTML = ansi_up.ansi_to_html(stderr_container.innerText);
    });
    </script>
    """

    content += '<div class="logs">'
    content += '<div class="stdout">'
    content += "<h1>Standard Output</h1><hr>"
    content += "<pre id='stdout'>{}</pre>".format(html.escape(''.join(stdout)))
    content += '</div>'
    
    content += '<div class="stderr">'
    content += "<h1>Standard Error</h1><hr>"
    content += "<pre id='stderr'>{}</pre>".format(html.escape(''.join(stderr)))
    content += '</div>'
    content += '</div>'

    return content

@router.get("/clear_logs")
async def clear_logs():
    try:
        open('stdout.log', 'w').close()
        open('stderr.log', 'w').close()
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    return JSONResponse({"status": "success", "message": "Logs cleared successfully"})


@router.post("/predict", response_model=PredictResponse)
async def get_load(predict_request: PredictRequest):
    try:
        exported_flow: ExportedFlow = predict_request.exported_flow
        graph_data: GraphData = exported_flow.data
        data = graph_data.dict()
        response = process_graph_cached(data, predict_request.message)
        return PredictResponse(result=response.get("result", ""))
    except Exception as e:
        # Log stack trace
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# get endpoint to return version of langflow
@router.get("/version")
def get_version():
    return {"version": version("langflow")}


@router.get("/health")
def get_health():
    return {"status": "OK"}
