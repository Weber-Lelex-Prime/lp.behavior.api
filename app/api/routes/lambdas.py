from fastapi import APIRouter
from app.services.lambdaServices import lambdaService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import json

router = APIRouter()

@router.get("/", tags=["lambdas"])
async def listOfLambdas():
    lambdaServiceManager = lambdaService()
    json_compatible_item_data = jsonable_encoder({"lambdas" : json.dumps(lambdaServiceManager.loadActiveLambdas()) })
    print(json_compatible_item_data)
    return JSONResponse(content=json_compatible_item_data)