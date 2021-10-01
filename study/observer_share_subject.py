from rx import of, operators as op
from rx.subject import Subject
import random
test1 = of(1,2,3,4,5)
sub = test1.pipe(
   op.map(lambda a : a+random.random()),
)
sub1 = Subject()
print("From first subscriber")
subscriber1 = sub1.subscribe(lambda i: print("From sub1 {0}".format(i)))
print("From second subscriber")
subscriber2 = sub1.subscribe(lambda i: print("From sub2 {0}".format(i)))
sub.subscribe(sub1)
