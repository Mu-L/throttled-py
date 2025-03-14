<h1 align="center">throttled-py</h1>
<p align="center">
    <em>🔧 High-performance Python rate limiting library with multiple algorithms (Fixed Window, Sliding Window, Token Bucket, Leaky Bucket & GCRA) and storage backends (Redis, In-Memory).</em>
</p>

<p align="center">
    <a href="https://github.com/ZhuoZhuoCrayon/throttled-py">
        <img src="https://badgen.net/badge/python/%3E=3.8/green?icon=github" alt="Python">
    </a>
     <a href="https://github.com/ZhuoZhuoCrayon/throttled-py">
        <img src="https://codecov.io/gh/ZhuoZhuoCrayon/throttled-py/graph/badge.svg" alt="Coverage Status">
    </a>
</p>

[简体中文](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/README.md) | English

## 🚀 Features

### 1) Storage

| Redis | In-Memory(Thread-Safety) |
|-------|--------------------------|
| ✅     | ✅                        |

### 2) Rate Limiting Algorithms

| [Fixed Window](https://github.com/ZhuoZhuoCrayon/throttled-py/tree/main/docs/basic#21-%E5%9B%BA%E5%AE%9A%E7%AA%97%E5%8F%A3) | [Sliding Window](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#22-%E6%BB%91%E5%8A%A8%E7%AA%97%E5%8F%A3) | [Token Bucket](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#23-%E4%BB%A4%E7%89%8C%E6%A1%B6) | [Leaky Bucket](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#24-%E6%BC%8F%E6%A1%B6) | [GCRA](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#25-gcra) |
|-----------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| ✅                                                                                                                           | ✅                                                                                                                                       | ✅                                                                                                                            | ✅                                                                                                                   | ✅                                                                                             |

We provide algorithm analysis documents - click any algorithm name to view implementation details.

## 🔰 Installation

```shell
$ pip install throttled-py
```

## 📝 Usage

### 1) Basic Usage

#### Core API

* `limit`: Deduct requests and return [**RateLimitResult**](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/README_EN.md#1-ratelimitresult).
* `peek`: Check current rate limit state for a key (returns [**RateLimitState**](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/README_EN.md#2-ratelimitstate)).

```python
from throttled import Throttled

# Default: In-Memory storage, Token Bucket algorithm, 60 reqs / sec.
throttle = Throttled()

# Deduct 1 request -> RateLimitResult(limited=False,
# state=RateLimitState(limit=60, remaining=59, reset_after=1)
print(throttle.limit("key", 1))
# Check state -> RateLimitState(limit=60, remaining=59, reset_after=1)
print(throttle.peek("key"))

# Deduct 60 requests (limited) -> RateLimitResult(limited=True,
# state=RateLimitState(limit=60, remaining=59, reset_after=1))
print(throttle.limit("key", 60))
```

#### Decorator

```python
from throttled import Throttled, rate_limter, exceptions

@Throttled(key="/ping", quota=rate_limter.per_min(1))
def ping() -> str:
    return "ping"

ping()  # Success

try:
    ping()  # Raises LimitedError
except exceptions.LimitedError as exc:
    print(exc)  # "Rate limit exceeded: remaining=0, reset_after=60"
    print(exc.rate_limit_result)  # Access RateLimitResult
```

### 2) Storage Backends

#### Redis

```python
from throttled import RateLimiterType, Throttled, rate_limter, store

@Throttled(
    key="/api/products",
    using=RateLimiterType.TOKEN_BUCKET.value,
    quota=rate_limter.per_min(1),
    store=store.RedisStore(server="redis://127.0.0.1:6379/0", options={"PASSWORD": ""}),
)
def products() -> list:
    return [{"name": "iPhone"}, {"name": "MacBook"}]

products()  # Success
products()  # Raises LimitedError
```

#### In-Memory

If you want to throttle the same Key at different locations in your program, make sure that Throttled receives the same MemoryStore and uses a consistent [`Quota`](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/README_EN.md#3-quota).

The following example uses memory as the storage backend and throttles the same Key on ping and pong:

```python
from throttled import Throttled, rate_limter, store

mem_store = store.MemoryStore()

@Throttled(key="ping-pong", quota=rate_limter.per_min(1), store=mem_store)
def ping() -> str: return "ping"

@Throttled(key="ping-pong", quota=rate_limter.per_min(1), store=mem_store)
def pong() -> str: return "pong"

ping()  # Success
pong()  # Raises LimitedError
```

### 3) Algorithms

The rate limiting algorithm is specified by the **`using`** parameter. The supported algorithms are as follows:

* [Fixed window](https://github.com/ZhuoZhuoCrayon/throttled-py/tree/main/docs/basic#21-%E5%9B%BA%E5%AE%9A%E7%AA%97%E5%8F%A3%E8%AE%A1%E6%95%B0%E5%99%A8): `RateLimiterType.FIXED_WINDOW.value`
* [Sliding window](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#22-%E6%BB%91%E5%8A%A8%E7%AA%97%E5%8F%A3): `RateLimiterType.SLIDING_WINDOW.value`
* [Token Bucket](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#23-%E4%BB%A4%E7%89%8C%E6%A1%B6): `RateLimiterType.TOKEN_BUCKET.value`
* [Leaky Bucket](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#24-%E6%BC%8F%E6%A1%B6): `RateLimiterType.LEAKING_BUCKET.value`
* [Generic Cell Rate Algorithm, GCRA)](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/docs/basic/readme.md#25-gcra): `RateLimiterType.GCRA.value`

```python
from throttled import RateLimiterType, Throttled, rate_limter, store

throttle = Throttled(
    # 🌟Specifying a current limiting algorithm
    using=RateLimiterType.FIXED_WINDOW.value, 
    quota=rate_limter.per_min(1),
    store=store.MemoryStore()
)
assert throttle.limit("key", 2).limited is True
```

### 4) Quota Configuration

#### Quick Setup

```python
from throttled import rate_limter

rate_limter.per_sec(60)   # 60 / sec
rate_limter.per_min(60)   # 60 / min
rate_limter.per_hour(60)  # 60 / hour
rate_limter.per_day(60)   # 60 / day
```

#### Burst Capacity

The **`burst`** parameter can be used to adjust the ability of the throttling object to handle burst traffic. This is valid for the following algorithms:

* `TOKEN_BUCKET`
* `LEAKING_BUCKET`
* `GCRA`

```python
from throttled import rate_limter

# Allow 120 burst requests.
# When burst is not specified, the default setting is the limit passed in.
rate_limter.per_min(60, burst=120)
```

#### Custom Quota

```python
from datetime import timedelta
from throttled.rate_limter import Quota, Rate

# A total of 120 requests are allowed in two minutes, and a burst of 150 requests is allowed.
Quota(Rate(period=timedelta(minutes=2), limit=120), burst=150)
```

## ⚙️ Data Models & Configuration

### 1) RateLimitResult

RateLimitState represents the result after executing the RateLimiter for the given key.

| Field     | Type           | Description                                                                             |
|-----------|----------------|-----------------------------------------------------------------------------------------|
| `limited` | bool           | Limited represents whether this request is allowed to pass.                             |
| `state`   | RateLimitState | RateLimitState represents the result after executing the RateLimiter for the given key. |

### 2) RateLimitState

RateLimitState represents the current state of the rate limiter for the given key.

| Field         | Type  | Description                                                                                                                          |
|---------------|-------|--------------------------------------------------------------------------------------------------------------------------------------|
| `limit`       | int   | Limit represents the maximum number of requests allowed to pass in the initial state.                                                |
| `remaining`   | int   | Remaining represents the maximum number of requests allowed to pass for the given key in the current state.                          |
| `reset_after` | float | ResetAfter represents the time in seconds for the RateLimiter to return to its initial state. In the initial state, Limit=Remaining. |

### 3) Quota

Quota represents the quota limit configuration.

| Field   | Type | Description                                                                                                    |
|---------|------|----------------------------------------------------------------------------------------------------------------|
| `burst` | int  | Optional burst capacity that allows exceeding the rate limit momentarily(supports Token / Leaky Bucket, GCRA). |
| `rate`  | Rate | The base rate limit configuration.                                                                             |

### 4) Rate

Rate represents the rate limit configuration.

| Field    | Type               | Description                                                         |
|----------|--------------------|---------------------------------------------------------------------|
| `period` | datetime.timedelta | The time period for which the rate limit applies.                   |
| `limit`  | int                | The maximum number of requests allowed within the specified period. |

### 5) Store Configuration

#### Common Parameters

| Param     | Description                     | Default                      |
|-----------|---------------------------------|------------------------------|
| `server`  | Redis connection URL            | `"redis://localhost:6379/0"` |
| `options` | Storage-specific configurations | `{}`                         |

#### RedisStore Options

RedisStore is developed based on the Redis API provided by [redis-py](https://github.com/redis/redis-py).

In terms of Redis connection configuration management, the configuration naming of [django-redis](https://github.com/jazzband/django-redis) is basically used to reduce the learning cost.

| Parameter                  | Description                                                                                                                                                    | Default                               |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| `CONNECTION_FACTORY_CLASS` | ConnectionFactory is used to create and maintain [ConnectionPool](https://redis-py.readthedocs.io/en/stable/connections.html#redis.connection.ConnectionPool). | `"throttled.store.ConnectionFactory"` |
| `CONNECTION_POOL_CLASS`    | ConnectionPool import path.                                                                                                                                    | `"redis.connection.ConnectionPool"`   |
| `CONNECTION_POOL_KWARGS`   | [ConnectionPool construction parameters](https://redis-py.readthedocs.io/en/stable/connections.html#connectionpool).                                           | `{}`                                  |
| `REDIS_CLIENT_CLASS`       | RedisClient import path, uses [redis.client.Redis](https://redis-py.readthedocs.io/en/stable/connections.html#redis.Redis) by default.                         | `"redis.client.Redis"`                |
| `REDIS_CLIENT_KWARGS`      | [RedisClient construction parameters](https://redis-py.readthedocs.io/en/stable/connections.html#redis.Redis).                                                 | `{}`                                  |
| `PASSWORD`                 | Password.                                                                                                                                                      | `null`                                |
| `SOCKET_TIMEOUT`           | ConnectionPool parameters.                                                                                                                                     | `null`                                |
| `SOCKET_CONNECT_TIMEOUT`   | ConnectionPool parameters.                                                                                                                                     | `null`                                |
| `SENTINELS`                | `(host, port)` tuple list, for sentinel mode, please use `SentinelConnectionFactory` and provide this configuration.                                           | `[]`                                  |
| `SENTINEL_KWARGS`          | [Sentinel construction parameters](https://redis-py.readthedocs.io/en/stable/connections.html#id1).                                                            | `{}`                                  |

#### MemoryStore Options

MemoryStore is essentially a [LRU Cache](https://en.wikipedia.org/wiki/Cache_replacement_policies#LRU) based on memory with expiration time.

| Parameter  | Description                                                                                                                          | Default |
|------------|--------------------------------------------------------------------------------------------------------------------------------------|---------|
| `MAX_SIZE` | Maximum capacity. When the number of stored key-value pairs exceeds `MAX_SIZE`, they will be eliminated according to the LRU policy. | `1024`  |

## 📚 Version History

[See CHANGELOG_EN.md](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/CHANGELOG_EN.md)

## 📄 License

[The MIT License](https://github.com/ZhuoZhuoCrayon/throttled-py/blob/main/LICENSE)
