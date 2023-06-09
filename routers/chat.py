from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel
from typing import Union
from fastapi.responses import StreamingResponse
from chains import queryCSV

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)




class ChatQuestionDto(BaseModel):
    question: str
    api_key: Union[str, None] = None


# sse response streaming

@router.post("/question2")
async def simple_question2(chat_question_dto: ChatQuestionDto):
    print('question: ', chat_question_dto.question)
    if chat_question_dto.api_key is None:
        raise HTTPException(status_code=400, detail="api_key is required")
    return queryCSV.getDateFromGPT(chat_question_dto.question)

