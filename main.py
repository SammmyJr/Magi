from PyQt5.QtWidgets import QTextEdit
from agent import Agent
from agent import Response
import asyncio

# Melchior: llama3:8b (llama3:8b-q4_K_M) ~ Balanced, logical, factual
# Balthasar: mistral:7b () ~ Creative, fluent
# Caspar: phi3:3.8b (phi3:3.8b-mini-4k-instruct-q4_K_M) ~ Efficient, crisp reasoning 

# Went with Mistral 7B for all of them. Works easier and is a bit lighter to run.

agents = {
    Agent("Balthasar"),
    Agent("Caspar"),
    Agent("Melchior"),
}

async def promptAll(prompt: str) -> dict[str, str]:
    summary = {}
    results = await asyncio.gather(*(agent.prompt(prompt) for agent in agents))

    for agent, res in zip(agents, results):
        summary[agent.name] = res
    
    return summary
