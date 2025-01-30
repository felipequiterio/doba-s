from typing import Dict
import json
import time
from utils.log import get_custom_logger

logger = get_custom_logger("LLM")


class ToolCallValidationError(Exception):
    """Raised when tool call validation fails"""

    pass


def get_arguments(response: dict, max_retries: int = 3, delay: float = 1.0) -> Dict:
    """
    Extract arguments from LLM response with retry mechanism

    Args:
        response: Raw response from LLM
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        Dict containing the extracted arguments

    Raises:
        ToolCallValidationError: If validation fails after all retries
    """
    retries = 0
    while retries < max_retries:
        try:
            if "tool_calls" not in response.get("message", {}):
                raise ToolCallValidationError("No tool_calls found in response")

            tool_calls = response["message"]["tool_calls"]
            if not tool_calls or not isinstance(tool_calls, list):
                raise ToolCallValidationError("Invalid tool_calls format")

            if "function" not in tool_calls[0]:
                raise ToolCallValidationError("No function data in tool call")

            if "arguments" not in tool_calls[0]["function"]:
                raise ToolCallValidationError("No arguments found in function call")

            args = tool_calls[0]["function"]["arguments"]

            # Validate args is valid JSON
            try:
                if isinstance(args, str):
                    args = json.loads(args)
            except json.JSONDecodeError:
                raise ToolCallValidationError("Arguments are not valid JSON")

            return args

        except (KeyError, IndexError, ToolCallValidationError) as e:
            retries += 1
            if retries == max_retries:
                logger.error(
                    f"Tool call validation failed after {max_retries} retries: {str(e)}"
                )
                raise ToolCallValidationError(f"Final validation error: {str(e)}")

            logger.warning(
                f"Tool call validation failed (attempt {retries}/{max_retries}): {str(e)}"
            )
            logger.warning(f"Retrying in {delay} seconds...")
            time.sleep(delay)
