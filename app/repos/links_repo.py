import os
import redis

redis_url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
client = redis.from_url(redis_url, decode_responses=True)


def save_link(code: str, url: str) -> None:
    client.set(f"link:{code}", url)


def get_link(code: str) -> str | None:
    return client.get(f"link:{code}")


def code_exists(code: str) -> bool:
    return client.exists(f"link:{code}") == 1


def track_click(code: str) -> None:
    client.incr(f"clicks:{code}")


def get_clicks(code: str) -> int:
    value = client.get(f"clicks:{code}")
    return int(value) if value else 0

def track_unique_view(code: str, visitor: str) -> None:
    # HyperLogLog: duplicate visitor apne aap ignore (12 KB fixed memory)
    client.pfadd(f"uv:{code}", visitor)


def get_unique_views(code: str) -> int:
    return client.pfcount(f"uv:{code}")
