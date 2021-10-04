import rx
from rx.subject import Subject
from rx import operators as op
import asyncio
subject = Subject()
subject.subscribe(lambda i: print(f"get {i} after subject created"))
def get_source():
    subject.subscribe(lambda i: print(f"get {i} in get_source before share "))
    source = subject.pipe(op.share())
    source.subscribe(lambda i: print(f"get {i} in get_source"))
    return source
def forget_old_source():
    return

async def func_test():
    source = get_source()
    source.subscribe(lambda d: print(f"get {d}"))
    response = None
    try:
        print("in try before wait")
        #response = await source.pipe(op.first(), op.to_future())
        source.pipe(op.first()).subscribe(lambda i:print(f"get in first {i}"))#, op.to_future())
        print(f"in try after await {response}")
    except Exception as err:
        print(f"error {err}")
    return source

loop = asyncio.get_event_loop()
task = loop.create_task(func_test())
subject.on_next(1)
subject.on_next(2)
loop.run_until_complete(task)
#asyncio.run(task)