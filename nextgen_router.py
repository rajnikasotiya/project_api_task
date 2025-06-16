from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.custom_exceptions import (
    NextGenException, InvalidPayloadException, NotFoundException, NetworkException, LLMProviderException, TimeoutException
)
from app.config.error_codes import ErrorCode
from app.models.request import TaskRequest
from app.services.llm_service import process_task
from app.config.logger import logger
from pydantic import ValidationError

router = APIRouter()

@router.get("/", tags=["Index"])
def index():
    logger.info("NextGen API is live!")
    return {"message": "NextGen API is live!"}

@router.get("/capabilities", tags=["Core"])
async def get_capabilities():
    try:
        models = ["03-mini-openai", "gpt-4", "llama-3"]
        logger.info("Fetching capabilities")
        return JSONResponse(status_code=ErrorCode.SUCCESS, content={"models": models})
    except Exception as e:
        logger.error(f"Error in /capabilities: {str(e)}")
        raise NextGenException(detail=f"Error in /capabilities: {str(e)}")


@router.post("/heartbeat", tags=["Core"])
async def heartbeat():
    try:
        logger.info("Heartbeat check")
        return JSONResponse(status_code=ErrorCode.SUCCESS, content={"info": "heartbeat OK", "role": "backend"})
    except Exception as e:
        logger.error(f"Error in /heartbeat: {str(e)}")
        raise NextGenException(detail=f"Error in /heartbeat: {str(e)}")


@router.post("/generate", tags=["LLM"])
async def generate_5ws(request: TaskRequest):
    try:
        logger.info(f"Received task: {request.task_name}")
        response = await process_task(request)
        return JSONResponse(status_code=ErrorCode.SUCCESS, content=response)
    except (ValidationError, RequestValidationError) as ve:
        logger.warning(f"Validation error: {ve}")
        raise InvalidPayloadException(detail=str(ve))
    except InvalidPayloadException as ipe:
        logger.warning(f"Invalid payload: {ipe.detail}")
        raise ipe
    except NetworkException as ne:
        logger.error(f"Network error: {ne.detail}")
        raise ne
    except LLMProviderException as le:
        logger.error(f"LLM provider error: {le.detail}")
        raise le
    except TimeoutException as te:
        logger.error(f"Timeout error: {te.detail}")
        raise te
    except NextGenException as ne:
        logger.error(f"NextGen error: {ne.detail}")
        raise ne
    except Exception as e:
        logger.error(f"Unhandled error in /generate: {str(e)}")
        raise NextGenException(detail=f"Unhandled error in /generate: {str(e)}")
