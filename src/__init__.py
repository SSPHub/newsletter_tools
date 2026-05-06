import subprocess

replies_path = "replies.txt"

# To not track the replies.txt that may contain PII
command = ["git", "update-index", "--assume-unchanged", replies_path]

# Execute the command
try:
    subprocess.run(command, check=True, capture_output=True, text=True)
    print(f"Ommitting the {replies_path} executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e.stderr}")
