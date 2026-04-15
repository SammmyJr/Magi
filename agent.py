from PyQt5.QtWidgets import QTextEdit
from ollama import chat
from ollama import ChatResponse
import json
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

class Agent:
    def __init__(self, _name: str):
        self.name = _name
        self.model = self.name.lower()
    
    async def prompt(self, prompt: str) -> str: 
        loop = asyncio.get_event_loop()
        def call_chat():
            return chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        
        response = await loop.run_in_executor(ThreadPoolExecutor(), call_chat)
        
        text = response.message.content

        try:
            match = re.search(r'\{.*?\}ENDOFJSON', text, re.DOTALL)
            if match:
                json_str = match.group().split("ENDOFJSON")[0]
            rawResponse = json.loads(json_str)
            response = Response(self, rawResponse["answer"], rawResponse["vote"], rawResponse["confidence"])

            return response
        
        # In cases where the model fails to output a proper JSON object
        except UnboundLocalError:
            return Response(self, "Failed to respond", {"yes": 0.0, "no": 0.0, "abstain": 1.0}, 0.0)
        except KeyError:
            return Response(self, "Failed to respond", {"yes": 0.0, "no": 0.0, "abstain": 1.0}, 0.0)
        except json.decoder.JSONDecodeError:
            return Response(self, "Failed to respond", {"yes": 0.0, "no": 0.0, "abstain": 1.0}, 0.0)

class Response():
    def __init__(self, _model: Agent, _answer: str, _vote: dict, _confidence: float):
        self.model = _model
        self.answer = _answer
        self.yes = float(_vote["yes"])
        self.no = float(_vote["no"])
        self.abstain = float(_vote["abstain"])
        self.confidence = _confidence

    def __str__(self):
        output = f"""{self.model.name} says:
{self.answer}
---
Yes: {self.yes}
No: {self.no}
Abstain: {self.abstain}
Confidence: {self.confidence}
"""
        return output
