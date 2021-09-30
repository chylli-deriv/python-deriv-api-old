import rx
import time
from rx import operators as op

def stream_generator(observer, scheduler):
    count = 0
    while True:
        observer.on_next(count)
        count = count + 1
        time.sleep(1)

obs = rx.create(stream_generator)
obs2 = obs.pipe(op.share())
obs2.subscribe(lambda i: print(f"in sub1 {i}"))
obs2.subscribe(lambda i: print(f"in sub2 {i}"))
