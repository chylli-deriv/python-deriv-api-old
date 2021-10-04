import rx
import asyncio
from rx.subject import Subject
from rx import operators as op

subject = Subject()
subject.subscribe(lambda i: print(f"get {i} after subject created"))
def get_source():
    subject.subscribe(lambda i: print(f"get {i} in get_source before share "))
    source = subject.pipe(op.share())
    source.subscribe(lambda i: print(f"get {i} in get_source"))
    return source
def forget_old_source():
    return
number = 0
async def emit():
    global number
    await asyncio.sleep(1)
    subject.on_next(number)
    number = number + 1

async def func_test():
    source = get_source()
    source.subscribe(lambda d: print(f"get {d}"))
    response = None
    try:
        print("in try before wait")
        response = await source.pipe(op.first(), op.to_future())
        #source.pipe(op.first()).subscribe(lambda i:print(f"get in first {i}"))#, op.to_future())
        print(f"in try after await {response}")
    except Exception as err:
        print(f"error {err}")
    return source

async def main():
    tasks = []
    tasks.append(asyncio.create_task(func_test()))
    tasks.append(emit())
    tasks.append(emit())
    await asyncio.wait(tasks)
asyncio.run(main())

#asyncio.run(task)