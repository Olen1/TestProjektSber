import sys


def build_greeting(name: str) -> str:
    """Return a friendly greeting for the provided name."""
    safe_name = name.strip() or "world"
    return f"Hello, {safe_name}!"


def main(argv: list[str]) -> int:
    """Entry point for the script.

    Usage:
        python app.py            # prints "Hello, world!"
        python app.py Alina      # prints "Hello, Alina!"
    """
    name = argv[1] if len(argv) > 1 else "world"
    print(build_greeting(name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


