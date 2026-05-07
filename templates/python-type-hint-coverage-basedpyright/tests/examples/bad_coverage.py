from typing import Any


def load_payload() -> Any:
    return {"name": "jan", "enabled": True}


def extract_name(payload: dict[str, Any]) -> str:
    # Type error: returning dict instead of str
    return payload


def process_number(value: int) -> int:
    # Type error: adding int to string
    result = value + "100"
    return result


if __name__ == "__main__":
    data = load_payload()
    print(extract_name(data))
    print(process_number(42))
