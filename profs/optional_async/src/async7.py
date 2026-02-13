import asyncio
import time
import logging

logger = logging.getLogger(__name__)

async def API_call(url: int):
    await asyncio.sleep(2) # let's say an API call takes 2 seconds to finish
    return "test"

list_of_urls = [i for i in range(100)]

async def main():
    logger.info("Starting query...")
    start = time.time()

    # we create a list of tasks, each task is an API call to a url in the list of urls
    tasks = [asyncio.create_task(API_call(url)) for url in list_of_urls]

    # we use asyncio.gather to run all the tasks concurrently and wait for them to finish
    result =  await asyncio.gather(*tasks)
    end = time.time()
    elapsed = str(end - start)
    logger.info("The process took {} seconds".format(elapsed))
    return result