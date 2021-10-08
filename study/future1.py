from asyncio import *
import asyncio

f1 = Future()
loop = get_event_loop()
def print_f(f):
    try:
        result = f1.result()
        print(f"result is {result}")
    except CancelledError:
        print(f"cancelled")
    except Exception as err:
        print(f"rejected {err}")

    loop.stop()

f1.add_done_callback(print_f)

#f1.set_result("hello")
#f1.set_exception(Exception())
f1.cancel()
loop.run_forever()