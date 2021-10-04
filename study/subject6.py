import rx
from rx.subject import Subject
from rx import operators as op
import asyncio
subject = Subject()
def get_source():
    source = subject.pipe(op.share())
    return source
def forget_old_source():
    return

async def func_test():
    source = get_source()
    source.subscribe(lambda d: print(f"get {d}"))
    response = None
    try:
        print("in try before wait")
        response = await source.pipe(op.first(), op.to_future())
        print(f"in try after await {response}")
    except Exception as err:
        print(f"error {err}")
    return source

subject.on_next(1)
subject.on_next(2)
asyncio.run(func_test())