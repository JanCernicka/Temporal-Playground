import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import chop_ingredients, cook_dish, serve_dish
from workflows import TASK_QUEUE, CookingWorkflow


async def main() -> None:
    client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CookingWorkflow],
        activities=[chop_ingredients, cook_dish, serve_dish],
    )
    print(f"Worker listening on task queue '{TASK_QUEUE}'. Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
