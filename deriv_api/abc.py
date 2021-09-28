import rx
from rx import operators as op
import asyncio

async def try1():
    abc = await rx.of(1).pipe(op.first(), op.to_future())
    print(abc)

asyncio.run(try1())