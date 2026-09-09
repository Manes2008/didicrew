import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any
import functools

# Khoi tao ThreadPoolExecutor danh rieng cho cac tac vu nang CPU/GPU/AI
# Giup Event Loop cua FastAPI luon giai phong de xu ly async I/O
_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="videocrew_worker")

def get_executor() -> ThreadPoolExecutor:
    """Lay instance ThreadPoolExecutor toan cuc."""
    return _executor

async def run_in_thread(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Chay mot ham dong bo (blocking) trong ThreadPool ma khong lam nghen Event Loop.
    Su dung thay the cho cac tac vu AI, Render Video, CrewAI kickoff.
    """
    loop = asyncio.get_running_loop()
    p_func = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(_executor, p_func)

def shutdown_executor():
    """Dong toan bo worker threads khi server tat."""
    _executor.shutdown(wait=False)
