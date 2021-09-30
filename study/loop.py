import asyncio

def abc(loop):
    async def hello():
        1
    loop.create_task(hello())
    print("hello")
loop = asyncio.get_event_loop()
abc(loop)