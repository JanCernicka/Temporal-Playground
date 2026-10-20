import asyncio
import os
import sys
import uuid

from temporalio.client import Client

from workflows import TASK_QUEUE, CookingWorkflow


async def main() -> None:
    dish = " ".join(sys.argv[1:]) or "pancakes"
    client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))

    handle = await client.start_workflow(
        CookingWorkflow.run,
        dish,
        id=f"cooking-{uuid.uuid4().hex[:8]}",
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow {handle.id}. Watch it in the Web UI, e.g. http://localhost:8233")
    print(await handle.result())


if __name__ == "__main__":
    asyncio.run(main())
