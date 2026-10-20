import asyncio

from temporalio import activity


@activity.defn
async def chop_ingredients(dish: str) -> list[str]:
    activity.logger.info("Chopping ingredients for %s", dish)
    await asyncio.sleep(5)
    return [dish, "onion", "garlic", "salt"]


@activity.defn
async def cook_dish(ingredients: list[str]) -> str:
    # Fails on the first attempt on purpose, so you can see a retry in the Web UI.
    if activity.info().attempt == 1:
        await asyncio.sleep(2)
        raise RuntimeError("The oven isn't hot yet")

    activity.logger.info("Cooking %s", ingredients)
    await asyncio.sleep(5)
    return f"{ingredients[0]} with {', '.join(ingredients[1:])}"


@activity.defn
async def serve_dish(meal: str) -> str:
    await asyncio.sleep(1)
    return f"Your {meal} is served. Enjoy!"
