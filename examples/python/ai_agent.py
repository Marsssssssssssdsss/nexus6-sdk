"""Anexus: AI Agent workflow example.

Shows how an AI agent checks login status and generates verification codes.

Requirements:
    pip install anexus-sdk

Run:
    python examples/python/ai_agent.py
"""

from anexus_sdk import check_login, generate_code


def act_on_behalf_of_user(target_platform: str) -> str:
    """
    AI-friendly function: check if the human is logged in,
    then generate a verification code for the target platform.

    Returns the auth code string, or raises an error.
    """
    # Step 1: Check if the human is logged in
    status = check_login()
    if not status.get("logged_in"):
        raise RuntimeError(
            "User is not logged in. "
            "Run `python -m anexus_sdk login` first."
        )

    print(f"  Logged in as: {status['username']}")

    # Step 2: Generate a verification code
    result = generate_code(target_platform)
    if not result.get("success"):
        raise RuntimeError(f"Failed to generate code: {result.get('error')}")

    code = result["code"]
    print(f"  Generated code for {target_platform}:")
    print(f"    {code}")
    print(f"  Expires: {result['expires_in']}")

    # Step 3: Return the code — pass it to the target platform
    return code


if __name__ == "__main__":
    print("AI Agent Demo")
    print("=" * 50)

    try:
        code = act_on_behalf_of_user("shopify")
        print(f"\nAuth code ready: {code[:50]}...")
        print("Send this code to the target platform.")
    except RuntimeError as e:
        print(f"\nError: {e}")