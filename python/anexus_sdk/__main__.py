"""Anexus SDK CLI.

Usage:
    python -m anexus_sdk login              # Auto login via browser
    python -m anexus_sdk code <platform>    # Generate verification code
    python -m anexus_sdk code --target X    # Generate verification code
"""

import sys


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-h")]

    if not args:
        print(__doc__.strip())
        sys.exit(0)

    cmd = args[0]

    if cmd == "login":
        from .login import main as login_main
        login_main()

    elif cmd == "code":
        from .code_gen import main as code_main
        # Replace "code" with the actual target in sys.argv
        sys.argv = [sys.argv[0]] + args[1:]
        code_main()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__.strip())
        sys.exit(1)


main()