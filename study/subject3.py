import rx
from rx import operators as op
from rx.subject import Subject
subject1 = Subject()
subject1.subscribe(lambda i: print(f"get {i} in source2 subscribe1"))
subject1.subscribe(lambda i: print(f"get {i} in source2 subscribe2"))

source1 = rx.defer(lambda i: rx.of(1,2,3))
#source2 = source1.pipe(op.share())
source1.subscribe(subject1)

