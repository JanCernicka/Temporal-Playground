import asyncio
import os

import anthropic
from temporalio.client import Client
from temporalio.worker import Worker

from activities import RecipeActivities
from shared import TASK_QUEUE
from workflows import RecipeWorkflow


async def main() -> None:
    client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))

    # Temporal owns retries (see the workflow's RetryPolicy), so the SDK's are off.
    activities = RecipeActivities(anthropic.AsyncAnthropic(max_retries=0))

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[RecipeWorkflow],
        activities=[activities.get_recipe],
    )
    print(f"Worker listening on task queue '{TASK_QUEUE}'. Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
