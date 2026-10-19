import asyncio
import os
import sys
import uuid

from temporalio.client import Client

from shared import TASK_QUEUE, RecipeRequest
from workflows import RecipeWorkflow


async def main() -> None:
    dish = " ".join(sys.argv[1:]) or None
    client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))

    recipe = await client.execute_workflow(
        RecipeWorkflow.run,
        RecipeRequest(dish=dish),
        id=f"recipe-{uuid.uuid4()}",
        task_queue=TASK_QUEUE,
    )
    print(recipe)


if __name__ == "__main__":
    asyncio.run(main())
