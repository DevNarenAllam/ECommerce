"""
Provides various rate limiting dependencies for use with FastAPI.

The rate limiting dependencies use Redis to track and enforce rate limiting
policies for different types of rate limiting algorithms, including:

- Token Bucket
- Leaky Bucket
- Fixed Window Counter
- Sliding Window Log
- Sliding Window Counter

Each dependency takes a `user_id` parameter and optional configuration
parameters to customize the rate limiting behavior. The dependencies will
raise an `HTTPException` with a 429 Too Many Requests status code if the
rate limit is exceeded.
"""

from fastapi import Depends, FastAPI, HTTPException
from datetime import datetime, timedelta
import time
import redis

app = FastAPI()
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


def get_redis_client():
    return redis_client


def token_bucket_dependency(
    user_id: str,
    max_tokens: int = 10,
    refill_rate: int = 1,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    """
    Provides a rate limiting dependency that implements a token bucket algorithm.

    The token bucket algorithm allows a certain number of requests (tokens) to be
    made within a given time window, and refills the bucket at a fixed rate. If the
    bucket is empty, further requests are denied until the bucket is refilled.

    Args:
        user_id (str): A unique identifier for the user or client making the requests.
        max_tokens (int, optional): The maximum number of tokens in the bucket. Defaults to 10.
        refill_rate (int, optional): The rate at which tokens are refilled, in tokens per second. Defaults to 1.
        redis_client (redis.StrictRedis): A Redis client instance used to store the token bucket state.

    Returns:
        dict: A dictionary with a "status" key indicating whether the request is allowed.

    Raises:
        HTTPException: If the token bucket is empty and the rate limit is exceeded.
    """
    key = f"token_bucket:{user_id}"
    tokens, last_refill_time = redis_client.hmget(key, "tokens", "last_refill_time")

    if tokens is None:
        tokens = max_tokens
        last_refill_time = time.time()
    else:
        tokens = int(tokens)
        last_refill_time = float(last_refill_time)

    # Refill tokens based on elapsed time
    now = time.time()
    tokens_to_add = (now - last_refill_time) * refill_rate
    tokens = min(max_tokens, tokens + int(tokens_to_add))
    last_refill_time = now

    if tokens <= 0:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Decrement token and store back in Redis
    tokens -= 1
    redis_client.hmset(key, {"tokens": tokens, "last_refill_time": last_refill_time})
    return {"status": "Allowed"}


def leaky_bucket_dependency(
    user_id: str,
    capacity: int = 10,
    leak_rate: float = 1,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    """
    Provides a rate limiting dependency that implements a leaky bucket algorithm.

    The leaky bucket algorithm allows a certain number of requests (the capacity of the
    bucket) to be made within a given time window, and "leaks" requests at a fixed rate.
    If the bucket is full, further requests are denied until the bucket has leaked enough
    to accept new requests.

    Args:
        user_id (str): A unique identifier for the user or client making the requests.
        capacity (int, optional): The maximum number of requests the bucket can hold.
            Defaults to 10.
        leak_rate (float, optional): The rate at which requests "leak" out of the bucket,
            in requests per second. Defaults to 1.
        redis_client (redis.StrictRedis): A Redis client instance used to store the leaky
            bucket state.

    Returns:
        dict: A dictionary with a "status" key indicating whether the request is allowed.

    Raises:
        HTTPException: If the leaky bucket is full and the rate limit is exceeded.
    """
    key = f"leaky_bucket:{user_id}"
    requests, last_check = redis_client.hmget(key, "requests", "last_check")
    requests = int(requests) if requests else 0
    last_check = float(last_check) if last_check else time.time()

    # Calculate leaked tokens
    now = time.time()
    leaked = (now - last_check) * leak_rate
    requests = max(0, requests - int(leaked))
    last_check = now

    if requests >= capacity:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Add a request and save the updated state
    requests += 1
    redis_client.hmset(key, {"requests": requests, "last_check": last_check})
    return {"status": "Allowed"}


def fixed_window_counter_dependency(
    user_id: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    """
    Provides a rate limiting dependency that implements a fixed window counter algorithm.

    The fixed window counter algorithm allows a certain number of requests (the max requests)
    to be made within a fixed time window (the window seconds). If the number of requests
    within the current window exceeds the max requests, further requests are denied until
    the next window starts.

    Args:
        user_id (str): A unique identifier for the user or client making the requests.
        max_requests (int, optional): The maximum number of requests allowed within the
            window. Defaults to 10.
        window_seconds (int, optional): The duration of the fixed time window, in seconds.
            Defaults to 60.
        redis_client (redis.StrictRedis): A Redis client instance used to store the fixed
            window counter state.

    Returns:
        dict: A dictionary with a "status" key indicating whether the request is allowed.

    Raises:
        HTTPException: If the number of requests within the current window exceeds the
            max requests.
    """

    key = f"fixed_window:{user_id}:{int(time.time() // window_seconds)}"
    requests = redis_client.get(key)

    if requests and int(requests) >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Increment request count with expiration
    redis_client.incr(key)
    redis_client.expire(key, window_seconds)
    return {"status": "Allowed"}


def sliding_window_log_dependency(
    user_id: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    """
    Provides a rate limiting dependency that implements a sliding window counter algorithm.

    The sliding window counter algorithm allows a certain number of requests (the max requests)
    to be made within a fixed time window (the window seconds). If the number of requests
    within the current window exceeds the max requests, further requests are denied until
    the next window starts.

    Args:
        user_id (str): A unique identifier for the user or client making the requests.
        max_requests (int, optional): The maximum number of requests allowed within the
            window. Defaults to 10.
        window_seconds (int, optional): The duration of the fixed time window, in seconds.
            Defaults to 60.
        redis_client (redis.StrictRedis): A Redis client instance used to store the sliding
            window counter state.

    Returns:
        dict: A dictionary with a "status" key indicating whether the request is allowed.

    Raises:
        HTTPException: If the number of requests within the current window exceeds the
            max requests.
    """

    key = f"sliding_window_log:{user_id}"
    now = time.time()

    # Remove expired requests
    redis_client.zremrangebyscore(key, 0, now - window_seconds)

    # Check request count
    request_count = redis_client.zcard(key)
    if request_count >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Add new request timestamp
    redis_client.zadd(key, {now: now})
    return {"status": "Allowed"}


def sliding_window_counter_dependency(
    user_id: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    sub_window_seconds: int = 10,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    """
    Provides a rate limiting dependency that implements a sliding window counter algorithm.

    The sliding window counter algorithm allows a certain number of requests (the max requests)
    to be made within a fixed time window (the window seconds), divided into smaller sub-windows
    (the sub-window seconds). If the number of requests within the current window exceeds the
    max requests, further requests are denied until the next window starts.

    Args:
        user_id (str): A unique identifier for the user or client making the requests.
        max_requests (int, optional): The maximum number of requests allowed within the
            window. Defaults to 10.
        window_seconds (int, optional): The duration of the fixed time window, in seconds.
            Defaults to 60.
        sub_window_seconds (int, optional): The duration of the sub-windows, in seconds.
            Defaults to 10.
        redis_client (redis.StrictRedis): A Redis client instance used to store the sliding
            window counter state.

    Returns:
        dict: A dictionary with a "status" key indicating whether the request is allowed.

    Raises:
        HTTPException: If the number of requests within the current window exceeds the
            max requests.
    """
    now = int(time.time())
    key_pattern = f"sliding_window_counter:{user_id}:{now // sub_window_seconds}"
    window_start = now - window_seconds

    # Aggregate counts within the sliding window
    total_requests = sum(
        int(
            redis_client.get(
                f"sliding_window_counter:{user_id}:{timestamp // sub_window_seconds}"
            )
            or 0
        )
        for timestamp in range(window_start, now, sub_window_seconds)
    )

    if total_requests >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Increment the request count in the current sub-window
    redis_client.incr(key_pattern)
    redis_client.expire(key_pattern, window_seconds)
    return {"status": "Allowed"}
