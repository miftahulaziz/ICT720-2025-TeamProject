import subprocess
import uuid
def send_line_broadcast_curl(access_token, message1, message2):
    """Sends a Line broadcast message using curl."""

    unique_id = uuid.uuid4()
    data = f"""{{
        "messages":[
            {{
                "type":"text",
                "text":"{message1}"
            }},
            {{
                "type":"text",
                "text":"{message2}"
            }}
        ]
    }}"""

    command = [
        "curl",
        "-v",
        "-X",
        "POST",
        "https://api.line.me/v2/bot/message/broadcast",
        "-H",
        "Content-Type: application/json",
        "-H",
        f"Authorization: Bearer {access_token}",
        "-H",
        f"X-Line-Retry-Key: {unique_id}",
        "-d",
        data,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("curl command executed successfully:")
        print(result.stdout)
        if result.stderr:
            print("Standard Error:")
            print(result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error executing curl command: {e}")
        if e.stderr:
            print("Standard Error:")
            print(e.stderr)


