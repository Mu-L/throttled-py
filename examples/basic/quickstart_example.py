from throttled import RateLimiterType, Throttled, rate_limiter, store, utils

throttle = Throttled(
    # 📈 使用令牌桶作为限流算法。
    # 📈 Use Token Bucket algorithm.
    using=RateLimiterType.TOKEN_BUCKET.value,
    # 🪣 设置配额：每秒填充 1,000 个 Token（limit），桶大小为 1,000（burst）。
    # 🪣 Set quota: 1,000 tokens per second (limit), bucket size 1,000 (burst).
    quota=rate_limiter.per_sec(1_000, burst=1_000),
    # 📁 使用内存作为存储
    # 📁 Use In-Memory storage.
    store=store.MemoryStore(),
)


def call_api() -> bool:
    # 💧消耗 Key=/ping 的一个 Token。
    result = throttle.limit("/ping", cost=1)
    return result.limited


if __name__ == "__main__":
    # 💻 Python 3.12.10, Linux 5.4.119-1-tlinux4-0009.1, Arch: x86_64, Specs: 2C4G.
    # ✅ Total: 100000, 🕒 Latency: 0.0068 ms/op, 🚀 Throughput: 122513 req/s (--)
    # ❌ Denied: 98000 requests
    benchmark: utils.Benchmark = utils.Benchmark()
    denied_num: int = sum(benchmark.serial(call_api, 100_000))
    print(f"❌ Denied: {denied_num} requests")
