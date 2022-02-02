import json
import sys

ARGV_FILE = ".git/MOCK_EDITOR_ARGV"
EXIT_CODE_FILE = ".git/MOCK_EDITOR_EXIT_CODE"


def main() -> None:
    """Substitute editor, to test git code"""
    with open(ARGV_FILE, "w") as f:
        json.dump(sys.argv, f)
    with open(EXIT_CODE_FILE) as f:
        return_code = int(f.readline())
    sys.exit(return_code)


if __name__ == "__main__":
    main()
