import asyncio

async def main():
    print("Hello!")
    task = asyncio.create_task(bye())
    print("I created the bye task and am waiting!")
    await asyncio.sleep(10)

async def bye():
    print("OK")
    await asyncio.sleep(5) # forces the program to wait for one second
    print("Goodbye!")  
asyncio.run(main())
