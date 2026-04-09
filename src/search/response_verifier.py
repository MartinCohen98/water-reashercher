from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Union

import requests
from bs4 import BeautifulSoup

EXPECTED_KEYS = {"Data", "Sources"}
EXPECTED_SOURCE_KEYS = {"Source", "Excerpt", "Relevance"}


@dataclass
class VerificationResult:
    valid: bool
    errors: List[str]
    parsed: Dict[str, Any] = None


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _fetch_page_text(url: str, timeout: int = 10) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())


def _excerpt_found_in_page(excerpt: str, page_text: str) -> bool:
    excerpt_norm = _normalize_text(excerpt)
    if not excerpt_norm:
        return False
    page_norm = _normalize_text(page_text)
    return excerpt_norm in page_norm


def parse_model_response(response: Union[str, Dict[str, Any]]) -> VerificationResult:
    errors: List[str] = []
    parsed: Dict[str, Any] = {}

    if isinstance(response, str):
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            error_msg = f"invalid JSON: {exc.msg}"
            print(f"[Parse Error] {error_msg}")
            return VerificationResult(valid=False, errors=[error_msg], parsed={})
    elif isinstance(response, dict):
        parsed = response
    else:
        error_msg = "response must be a JSON string or dict"
        print(f"[Parse Error] {error_msg}")
        return VerificationResult(valid=False, errors=[error_msg], parsed={})

    if not isinstance(parsed, dict):
        error_msg = "top-level JSON must be an object"
        print(f"[Parse Error] {error_msg}")
        return VerificationResult(valid=False, errors=[error_msg], parsed={})

    actual_keys = set(parsed.keys())
    if actual_keys != EXPECTED_KEYS:
        missing = EXPECTED_KEYS - actual_keys
        extra = actual_keys - EXPECTED_KEYS
        if missing:
            error_msg = f"missing keys: {', '.join(sorted(missing))}"
            errors.append(error_msg)
        if extra:
            error_msg = f"unexpected keys: {', '.join(sorted(extra))}"
            errors.append(error_msg)

    data_value = parsed.get("Data")
    if not isinstance(data_value, str):
        error_msg = "Data must be a string"
        errors.append(error_msg)

    sources = parsed.get("Sources")
    if not isinstance(sources, list):
        error_msg = "Sources must be a list"
        errors.append(error_msg)
    else:
        if len(sources) == 0:
            error_msg = "Sources must include at least one entry"
            errors.append(error_msg)
        for index, source_item in enumerate(sources, start=1):
            if not isinstance(source_item, dict):
                error_msg = f"Sources[{index}] must be an object"
                errors.append(error_msg)
                continue
            item_keys = set(source_item.keys())
            if item_keys != EXPECTED_SOURCE_KEYS:
                missing = EXPECTED_SOURCE_KEYS - item_keys
                extra = item_keys - EXPECTED_SOURCE_KEYS
                if missing:
                    error_msg = f"Sources[{index}] missing keys: {', '.join(sorted(missing))}"
                    errors.append(error_msg)
                if extra:
                    error_msg = f"Sources[{index}] unexpected keys: {', '.join(sorted(extra))}"
                    errors.append(error_msg)

    for error in errors:
        print(f"[Parse Error] {error}")

    return VerificationResult(valid=not errors, errors=errors, parsed=parsed if not errors else {})


def verify_model_response(response: Union[str, Dict[str, Any]]) -> VerificationResult:
    parsed_result = parse_model_response(response)
    if not parsed_result.valid:
        return parsed_result

    parsed = parsed_result.parsed
    sources = parsed.get("Sources", [])
    validation_errors: List[str] = []

    for index, source_item in enumerate(sources, start=1):
        url = source_item.get("Source", "")
        excerpt = source_item.get("Excerpt", "")

        if not url or not excerpt:
            error_msg = f"Missing URL or excerpt for validation"
            validation_errors.append(f"Sources[{index}]" + error_msg)
            source_item["Validation"] = error_msg
            continue

        try:
            page_text = _fetch_page_text(url)
            if _excerpt_found_in_page(excerpt, page_text):
                success_msg = f"Excerpt verified at source {index}"
                source_item["Validation"] = success_msg
            else:
                error_msg = f"Excerpt not found at URL"
                validation_errors.append(f"Sources[{index}]" + error_msg)
                source_item["Validation"] = error_msg
        except Exception as exc:
            error_msg = f"Failed to fetch URL, could not verify source"
            validation_errors.append(f"Sources[{index}]" + error_msg)
            source_item["Validation"] = error_msg

    return VerificationResult(
        valid=parsed_result.valid,
        errors=parsed_result.errors + validation_errors,
        parsed=parsed,
    )
