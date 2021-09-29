from FuturePipe import pipe
from rx import of, operators as op

import asyncio

def abc():
    return of(1).pipe(op.first(), op.to_future())

async def fn1(res):
    return res + 1

async def main():
    print(abc());
    result = await pipe(abc(), fn1, fn1)
    print(result)

asyncio.run(main())