"""Anexus SDK CLI.

Usage:
    python -m anexus_sdk login              # Auto login via browser
    python -m anexus_sdk code <platform>    # Generate verification code
    python -m anexus_sdk whoami             # Check login status
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
        sys.argv = [sys.argv[0]] + args[1:]
        code_main()

    elif cmd in ("whoami", "status"):
        from .code_gen import check_login
        result = check_login()
        if result.get("logged_in"):
            print("")
            print("  Logged in")
            print(f"  Username:  {result['username']}")
            print(f"  User ID:   {result['user_id']}")
            print(f"  Email:     {result['email']}")
            print(f"  Role:      {result['role']}")
            print("")
        else:
            print("")
            print(f"  Not logged in: {result.get('error', 'Unknown')}")
            print("  Run `python -m anexus_sdk login` to sign in.")
            print("")
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__.strip())
        sys.exit(1)


main()