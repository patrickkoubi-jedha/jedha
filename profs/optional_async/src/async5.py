import asyncio

async def main():
    print("Hello, I am in function main, and I will not await the function bye to finish before I can continue!")
    print("Bye will start as soon as I have finished creating the task and printed Hello!")
    task = asyncio.create_task(bye())
    print("Hello!")

async def bye():
    print("OK i'm in function bye... I will await 5 seconds before I can print the next line!")
    await asyncio.sleep(5) # forces the program to wait for five seconds

    #will print the bellow line if main is still running
    print("I awaited 5 sec in function bye!")  
asyncio.run(main())
