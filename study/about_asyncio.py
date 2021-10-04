import asyncio


async def sleep_print():
    print("before sleep")
    await asyncio.sleep(1)
    print("ok")

async def main():
    asyncio.create_task(sleep_print())
    await asyncio.sleep(5)
    print("end main")

asyncio.run(main())