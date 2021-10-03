import rx
from rx.subject import Subject
from rx import operators as op
import asyncio
loop = asyncio.get_event_loop()
def get_source():
    #subject = Subject()
    #subject.on_next(1)
    subject = rx.defer(lambda i: rx.of(1,2,3)).pipe(op.share())
    return subject
def forget_old_source():
    return

def func_test():
    source = get_source().pipe(op.share())
    source.subscribe(lambda d: print(f"get {d}"))
    async def process_response():
        response = None
        try:
            print("in try before wait")
            response = await source.pipe(op.first(), op.to_future(loop.create_future))
            print(f"in try after await {response}")
        except Exception as err:
            print(f"error {err}")
    task = loop.create_task(process_response())
    loop.run_until_complete(task)
    return source

func_test()
#source = get_source()
#def myof(i):
#    print(f"get {i} in defer")
#    return rx.of(1,2,3)
#source = rx.defer(myof)
#print(type(source))
#source.subscribe(lambda i: print(f"get {i}"))