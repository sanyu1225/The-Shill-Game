import uuid


def generate_id(text: str) -> str:
    """
    Generate a deterministic UUID from a text string.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))


if __name__ == "__main__":
    print(generate_id("alice"))
    print(generate_id("bob"))
