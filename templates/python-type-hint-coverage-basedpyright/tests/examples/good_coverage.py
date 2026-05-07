def normalize_name(raw_name: str) -> str:
    return raw_name.strip().title()


def build_greeting(user_name: str) -> str:
    normalized = normalize_name(user_name)
    return f"Hello {normalized}"


if __name__ == "__main__":
    print(build_greeting("  jan  "))
