import rx
from rx import operators as op
from rx.subject import Subject
subject = Subject()
#source1 = subject.pipe(op.share())
source1 = subject.pipe(op.first())
print(type(source1))
source1.subscribe(lambda i: print(f"get {i}"))
source1.subscribe(lambda i: print(f"get {i}"))
subject.on_next(1)
subject.on_next(2)


# subject can be subscribed many times
# shared observer can also be subscribed many times
# rx.defer can emit items many times for every subscription
# but rx.defer then pipe, then pipe will think it as one subscription, then only print itmes one time
# but I don't know why piped subject still can subscribe many times