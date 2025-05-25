from functools import partial
from typing import Any, Callable, Coroutine, Dict

import pytest

from throttled.asyncio import (
    RateLimiterType,
    Throttled,
    exceptions,
    per_sec,
    rate_limiter,
    store,
    types,
    utils,
)


@pytest.fixture
def decorated_demo() -> Callable[[int, int], Coroutine]:
    @Throttled(
        key="/api/product",
        using=RateLimiterType.FIXED_WINDOW.value,
        quota=rate_limiter.per_min(1),
        store=store.MemoryStore(),
    )
    async def demo(left: int, right: int) -> int:
        return left + right

    yield demo


@pytest.mark.asyncio
class TestThrottled:
    async def test_demo(self, decorated_demo: Callable[[int, int], Coroutine]) -> None:
        assert await decorated_demo(1, 2) == 3
        with pytest.raises(exceptions.LimitedError):
            await decorated_demo(2, 3)

    async def test_limit__timeout(self):
        throttle: Throttled = Throttled(timeout=1, quota=per_sec(1))
        assert (await throttle.limit("key")).limited is False

        def _callback(
            left: float, right: float, elapsed: types.TimeLikeValueT, *args, **kwargs
        ):
            assert left <= elapsed < right

        async with utils.Timer(callback=partial(_callback, 1, 2)):
            assert (await throttle.limit("key")).limited is False

        # case: retry_after > timeout
        async with utils.Timer(callback=partial(_callback, 0, 0.1)):
            assert (await throttle.limit("key", cost=2)).limited

        # case: timeout < retry_after
        async with utils.Timer(callback=partial(_callback, 0, 0.1)):
            assert (await throttle.limit("key", timeout=0.5)).limited

    async def test_enter(self):
        construct_kwargs: Dict[str, Any] = {
            "key": "key",
            "quota": per_sec(1),
            "store": store.MemoryStore(),
        }
        throttle: Throttled = Throttled(**construct_kwargs)
        async with throttle as rate_limit_result:
            assert rate_limit_result.limited is False

        try:
            async with throttle:
                pass
        except exceptions.LimitedError as e:
            assert e.rate_limit_result.limited
            assert e.rate_limit_result.state.remaining == 0
            assert e.rate_limit_result.state.reset_after == 1
            assert e.rate_limit_result.state.retry_after == 1

        async with Throttled(**construct_kwargs, timeout=1) as rate_limit_result:
            assert not rate_limit_result.limited
