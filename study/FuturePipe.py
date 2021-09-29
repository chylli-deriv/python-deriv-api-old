# idea come from https://stackoverflow.com/questions/43325501/how-do-i-write-a-sequence-of-promises-in-python
from asyncio.futures import Future
async def pipe(future, *fns):
    if not isinstance(future, Future):
        raise Exception("future should be an instance of Future")

    result = await future;
    for fn in fns:
        result = await fn(result)

    return result