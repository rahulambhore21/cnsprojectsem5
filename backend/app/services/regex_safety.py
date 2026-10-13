import re
from typing import Optional
from app.config import settings

_BODY = r'(?:[^()\\]|\\.)*'
_QUANT = r'(?:[+*]|\{\d*,\d*\})'
# A quantified group whose body itself contains a quantifier, e.g. (a+)+  (.*)*  (\w+\s?)*
_NESTED_QUANTIFIER = re.compile(r'\(' + _BODY + _QUANT + _BODY + r'\)\s*(?:[+*]|\{\d+,?\d*\})')


def validate_user_regex(pattern: Optional[str]) -> Optional[str]:
    """
    Validates a user/AI supplied regex before it is stored and executed against every log.
    Returns the pattern unchanged, or raises ValueError if it is invalid or likely to backtrack catastrophically.
    """
    if pattern is None or pattern == "":
        return None
    if len(pattern) > settings.MAX_REGEX_LENGTH:
        raise ValueError(f"Regex exceeds {settings.MAX_REGEX_LENGTH} characters.")
    try:
        re.compile(pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}")
    if _NESTED_QUANTIFIER.search(pattern):
        raise ValueError("Regex rejected: nested quantifiers can cause catastrophic backtracking.")
    return pattern
