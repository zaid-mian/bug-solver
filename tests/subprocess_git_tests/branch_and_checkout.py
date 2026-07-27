import subprocess

result = subprocess.run(["git", "branch"], capture_output=True, text=True)

print(result)
print(result.stdout)

result = subprocess.run(
    ["git", "branch", "--show-current"], capture_output=True, text=True
)
print(result)
print(result.stdout)
