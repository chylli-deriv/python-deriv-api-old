from rx.subject import Subject
from rx import operators as op
import asyncio
source = Subject()
source.subscribe(lambda i: print(f"get {i} out try_sub"))
async def try_sub():
    print("will subscribe")
    source.subscribe(lambda i: print(f"get {i}"))
    print("subscribe done")
number = 0
async def emit():
    global number
    await asyncio.sleep(1)
    source.on_next(number)
    number = number + 1

async def main():
    tasks = []
    tasks.append(asyncio.create_task(try_sub()))
    for i in range(5):
        tasks.append(asyncio.create_task(emit()))
    print("source done")
    await asyncio.wait(tasks)
    source.on_completed()
asyncio.run(main())