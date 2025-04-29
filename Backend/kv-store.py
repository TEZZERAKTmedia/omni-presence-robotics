import subprocess
import os

# Path to the kvstore executable
KVSTORE_EXEC = os.path.join(os.path.dirname(__file__), 'kv-store/kvstore')

def kv_put(key: str, value: str) -> str:
    try:
        result = subprocess.run(
            [KVSTORE_EXEC, "put", key, value],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[KV ERROR] put failed: {e.stderr.strip()}"

def kv_get(key: str) -> str:
    try:
        result = subprocess.run(
            [KVSTORE_EXEC, "get", key],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[KV ERROR] get failed: {e.stderr.strip()}"

def kv_delete(key: str) -> str:
    try:
        result = subprocess.run(
            [KVSTORE_EXEC, "delete", key],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[KV ERROR] delete failed: {e.stderr.strip()}"


# Optional testing block
if __name__ == "__main__":
    print(kv_put("foo", "bar"))
    print(kv_get("foo"))
    print(kv_delete("foo"))
