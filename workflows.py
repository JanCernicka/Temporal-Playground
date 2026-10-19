from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Activities run outside the workflow sandbox, so import them as pass-through.
with workflow.unsafe.imports_passed_through():
    from activities import RecipeActivities
    from shared import RecipeRequest


@workflow.defn
class RecipeWorkflow:
    @workflow.run
    async def run(self, request: RecipeRequest) -> str:
        return await workflow.execute_activity_method(
            RecipeActivities.get_recipe,
            request,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )
