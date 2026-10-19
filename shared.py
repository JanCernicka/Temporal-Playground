from dataclasses import dataclass

TASK_QUEUE = "recipe-task-queue"


@dataclass
class RecipeRequest:
    # What to cook, e.g. "chicken curry". None lets Claude pick a dish.
    dish: str | None = None
