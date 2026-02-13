import asyncio

async def main():
    print("I am in function main, and I will await the function bye to finish before I can continue!")
    await bye()
    print("I awaited the end of function bye, and bye was finished!")

async def bye():
    print("OK i'm in function bye")
    await asyncio.sleep(5) # forces the program to wait for five seconds
    print("I awaited 5 sec in function bye!")  
asyncio.run(main())
