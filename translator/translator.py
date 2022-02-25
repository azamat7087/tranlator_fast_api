from fastapi import Body, HTTPException, APIRouter, Depends, status, Response
import core.service as service
from translator.schemas import TextToTranslate, TranslatedText
from auth.jwt_bearer import JWTBearer
from translator.parsers.selenium_parser import translate_text
router = APIRouter()


@router.post("/", response_model=TranslatedText, status_code=status.HTTP_200_OK, tags=['Translator'],
             dependencies=[Depends(JWTBearer())])
async def link_generate(response: Response,
                        params: dict = Depends(service.default_parameters),
                        translate: TextToTranslate = Body(..., )):
    try:
        text = translate_text(**translate.dict())
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{str(e)}")
