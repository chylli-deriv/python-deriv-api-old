import asyncio
def abc():
    async def asy1():
        return 1;
    async def asy2():
        return 1 + await asy1()
    return asy2()

async def caller():
    print(await abc())
asyncio.run(caller())