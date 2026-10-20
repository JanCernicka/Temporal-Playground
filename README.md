# Temporal-Playground
Just for testing out Temporal to run some workflows.

## Demo workflow (no API key needed)

`demo/` holds a fake cooking workflow that only waits and returns strings, so you can watch Temporal in the Web UI without paying for anything. One run takes about 30 seconds:

1. `chop_ingredients` activity (5 s)
2. A 10 s durable timer
3. `cook_dish` activity: fails on its first attempt on purpose, then succeeds on the retry
4. `serve_dish` activity, which returns the final message

Run it (with `temporal server start-dev` running and dependencies installed as below):

```bash
cd demo
python worker.py                 # terminal 1
python starter.py "pancakes"     # terminal 2
```

What to look at in the Web UI (http://localhost:8233):

- **Event History:** activities scheduled and completed, the timer firing, and the workflow tasks in between.
- **Pending Activities:** while `cook_dish` waits for its retry, you see the attempt number and the last failure.
- **Queries:** run `get_status` while the workflow is running to see which step it is on.
- **Workers:** the task queue `demo-task-queue` lists your worker as a poller.
- **Start Workflow** button: start one from the UI with type `CookingWorkflow`, task queue `demo-task-queue` and input `"pancakes"` (a JSON string).

## Recipe workflow

A Temporal workflow (Python SDK) that asks Claude for a cooking recipe.

| File | What it does |
| --- | --- |
| `workflows.py` | `RecipeWorkflow`: runs the `get_recipe` activity with a timeout and retry policy |
| `activities.py` | `get_recipe`: calls the Claude API (`claude-opus-5-5`) and returns the recipe as Markdown |
| `worker.py` | Worker that hosts the workflow and activity on the `recipe-task-queue` task queue |
| `starter.py` | Starts a workflow run and prints the recipe |
| `shared.py` | Task queue name and the `RecipeRequest` input |

### Prerequisites

- Python 3.10+
- [Temporal CLI](https://docs.temporal.io/cli) (or any Temporal server reachable at `localhost:7233`)
- An Anthropic API key

### Run it

1. Start a local Temporal server (Web UI at http://localhost:8233):

   ```bash
   temporal server start-dev
   ```

2. Install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. In one terminal, start the worker:

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   python worker.py
   ```

4. In another terminal, start the workflow:

   ```bash
   python starter.py "chicken curry"   # or just: python starter.py  (Claude picks a dish)
   ```

The recipe is printed in the starter terminal, and the run shows up in the Temporal Web UI.

Set `TEMPORAL_ADDRESS` if your server is not at `localhost:7233`.

### Notes

- Retries are handled by Temporal (up to 5 attempts), so the Anthropic client's own retries are turned off. Rate limits, server errors and network errors are retried; bad requests, auth errors and refusals fail the workflow right away.
- The request opts into server-side refusal fallback (`fallbacks="default"`): if a safety classifier declines, the API retries on Anthropic's recommended fallback model instead of returning a refusal.
