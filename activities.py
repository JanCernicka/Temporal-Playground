import anthropic
from temporalio import activity
from temporalio.exceptions import ApplicationError

from shared import RecipeRequest

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = (
    "You are a friendly home cook. Reply with exactly one recipe in Markdown: "
    "a title, servings and total time, an ingredient list with quantities, "
    "and numbered steps. No preamble."
)


class RecipeActivities:
    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self.client = client

    @activity.defn
    async def get_recipe(self, request: RecipeRequest) -> str:
        if request.dish:
            prompt = f"Give me a recipe for {request.dish}."
        else:
            prompt = "Give me a recipe for a dish of your choice."

        activity.logger.info("Asking Claude: %s", prompt)
        try:
            response = await self.client.beta.messages.create(
                model=MODEL,
                max_tokens=16000,
                output_config={"effort": "medium"},
                # If a safety classifier declines, the API retries on Anthropic's
                # recommended fallback model instead of returning a refusal.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
        except (
            anthropic.BadRequestError,
            anthropic.AuthenticationError,
            anthropic.PermissionDeniedError,
            anthropic.NotFoundError,
        ) as e:
            # Retrying these won't help, so tell Temporal to stop.
            raise ApplicationError(str(e), non_retryable=True) from e
        # Rate limits, 5xx and connection errors propagate and Temporal retries them.

        if response.stop_reason == "refusal":
            category = response.stop_details.category if response.stop_details else None
            raise ApplicationError(
                f"Claude declined the request (category: {category})",
                non_retryable=True,
            )

        return "".join(block.text for block in response.content if block.type == "text")
