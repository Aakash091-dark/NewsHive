import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from bedrock.bedrock_process import call_bedrock_structured
from config.schema import SummaryResponse
from logs.json_log import log as logger

async def summarize_text(text: str, target_words: int = 55) -> str:
    cleaned_text = text
    if not cleaned_text:
        logger.warn(
            "Empty text provided for summarization",
            extra={"module": "summarize_text"}
        )
        return "Empty text provided"

    system_role = "You are a text summarization assistant."

    prompt = f"""
    Summarize the following text in a concise manner of approximately {target_words} words.
    Make the summary clear, coherent, and human-readable. Preserve the key information.

    Text:
    {cleaned_text}

    Return only a JSON object like this:
    {{
        "summary": "<your summarized text>"
    }}
    """

    try:
        result = await call_bedrock_structured(system_role, prompt, SummaryResponse)
    except Exception as e:
        logger.error(
            "Bedrock summarization failed",
            extra={"error": str(e), "module": "summarize_text"},
            exc_info=True
        )
        return f"Error generating summary: {str(e)}"

    summary = ""
    if result and hasattr(result, "summary"):
        summary = result.summary.strip()
    elif isinstance(result, dict) and "summary" in result:
        summary = result["summary"].strip()
    else:
        summary = "Error: No summary returned"

    return summary

async def get_summary(full_content, target_words=55):
    if not full_content or len(full_content.strip()) < 40:
        return ""  
    try:
        summary = await summarize_text(full_content, target_words=target_words)
        return summary
    except Exception as e:
        return ""  