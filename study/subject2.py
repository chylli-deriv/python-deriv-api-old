import rx
from rx.subject import Subject
from rx import operators as op
import asyncio
loop = asyncio.get_event_loop()
def get_source():
    subject = Subject()
    subject.on_next("hello")
    return subject
def forget_old_source():
    return

def func_test():
    source = get_source().pipe(op.finally_action(forget_old_source), op.share())
    async def process_response():
        response = None
        try:
            print("in try before wait")
            response = await source.pipe(op.first(), op.to_future(loop.create_future))
            print("in try after await")
        except Exception as err:
            print(f"error {err}")
    task = loop.create_task(process_response())
    loop.run_until_complete(task)
    return source

func_test()
