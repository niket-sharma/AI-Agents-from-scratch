from __future__ import annotations

import os
from typing import Iterable, List, Optional, Sequence

from dotenv import load_dotenv
from openai import OpenAI

from src.memory import BaseMemory, ConversationBufferMemory
from src.tools import BaseTool
from src.utils import Message, Role, get_logger


class BaseAgent:
    """Reusable building block for chat-style agents."""

    def __init__(
        self,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_output_tokens: int = 512,
        memory: Optional[BaseMemory] = None,
        tools: Optional[Iterable[BaseTool]] = None,
        client: Optional[OpenAI] = None,
        auto_load_env: bool = True,
    ) -> None:
        if auto_load_env:
            load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key and not client:
            raise ValueError(
                "OPENAI_API_KEY not found. Set it in your environment or pass a client."
            )
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.memory = memory or ConversationBufferMemory()
        self.tools = list(tools or [])
        self.client = client or OpenAI(api_key=api_key)  # type: ignore[arg-type]
        self.logger = get_logger(self.__class__.__name__)

    def _build_messages(self, user_prompt: str) -> List[dict]:
        messages: List[Message] = [Message(Role.SYSTEM.value, self.system_prompt)]
        if self.memory:
            messages.extend(self.memory.get_context())
        messages.append(Message(Role.USER.value, user_prompt))
        return [message.to_dict() for message in messages]

    def complete(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_messages: Optional[Sequence[Message]] = None,
    ) -> str:
        messages_dicts = self._build_messages(prompt)
        if extra_messages:
            messages_dicts.extend([message.to_dict() for message in extra_messages])
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages_dicts,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_output_tokens,
        )
        content = response.choices[0].message.content or ""
        if self.memory:
            self.memory.add(Message(Role.USER.value, prompt))
            self.memory.add(Message(Role.ASSISTANT.value, content))
        return content.strip()

    def run_step(self, user_message: str) -> str:
        """Convenience helper for interactive sessions."""
        self.logger.info("User: %s", user_message)
        response = self.complete(user_message)
        self.logger.info("Assistant: %s", response)
        return response
