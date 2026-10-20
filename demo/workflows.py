from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import chop_ingredients, cook_dish, serve_dish

TASK_QUEUE = "demo-task-queue"


@workflow.defn
class CookingWorkflow:
    def __init__(self) -> None:
        self.status = "starting"

    @workflow.run
    async def run(self, dish: str) -> str:
        self.status = "chopping ingredients"
        ingredients = await workflow.execute_activity(
            chop_ingredients,
            dish,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # A durable timer: shows up as TimerStarted / TimerFired in the event history.
        self.status = "letting it rest"
        await workflow.sleep(timedelta(seconds=10))

        self.status = "cooking"
        meal = await workflow.execute_activity(
            cook_dish,
            ingredients,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=3),
                maximum_attempts=3,
            ),
        )

        self.status = "serving"
        result = await workflow.execute_activity(
            serve_dish,
            meal,
            start_to_close_timeout=timedelta(seconds=30),
        )

        self.status = "done"
        return result

    # Callable from the Web UI's "Queries" tab while the workflow runs.
    @workflow.query
    def get_status(self) -> str:
        return self.status
