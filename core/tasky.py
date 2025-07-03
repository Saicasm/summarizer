from celery import shared_task
from .llm_service import LLMService

@shared_task
def process_query(query_text, use_web_search):
    llm_service = LLMService()
    result = llm_service.process_query(query_text, use_web_search)
    return result