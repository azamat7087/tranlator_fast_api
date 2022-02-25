from pydantic import BaseModel, Field, validator
from translator.utils import has_cyr


class TextToTranslate(BaseModel):
    from_lang: str = Field(..., max_length=4)
    to_lang: str = Field(..., max_length=4)
    text: str = Field(..., )


class TranslatedText(BaseModel):
    text: str = Field(..., )
