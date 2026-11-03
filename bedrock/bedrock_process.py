from config.settings import LLM_MODEL, AWS_REGION
from langchain_aws import ChatBedrock
from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import JsonOutputParser
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception
from logs.json_log import log

class KeywordResponse(BaseModel):
    keywords: List[str]


llm = ChatBedrock(
    model_id=LLM_MODEL,
    region_name=AWS_REGION,
    temperature=0.2,
    model_kwargs={"timeout": 60},
)

def is_retryable_error(exception):
    error_message = str(exception)
    return "ThrottlingException" in error_message or "Too many tokens" in error_message or "RequestLimitExceeded" in error_message

@retry(
    retry=retry_if_exception(is_retryable_error),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(8),
    before_sleep=lambda retry_state: log.info(f"Retrying Bedrock call due to throttling... Attempt {retry_state.attempt_number}. Error: {str(retry_state.outcome.exception())}")
)
async def call_bedrock_structured(system_role: str, prompt: str, schema: type[BaseModel], context=None):
    parser = JsonOutputParser(pydantic_object=schema)

    json_prompt = f"""
    {prompt}

    Format the output as a JSON object with the following schema:
    {parser.get_format_instructions()}
    
    IMPORTANT: Only return the JSON object matching the schema. Do not include the schema definition itself in the output.
    """

    response = await llm.ainvoke(
        [
            {"role": "system", "content": system_role},
            {"role": "user", "content": f"{json_prompt}\n\nContext: {context or ''}"}
        ],
    )
    
    if response and hasattr(response, 'content'):
        return parser.parse(response.content)
    return None
