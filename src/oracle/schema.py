"""Pydantic models for training examples.

Every generated example — whether synthetic or extracted — is validated
through these models before being written to disk.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, computed_field, model_validator


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """A tool/function call made by the assistant."""

    name: str = Field(description="Tool function name (e.g., seer_dig, tome_tld_lookup)")
    arguments: dict = Field(default_factory=dict, description="Tool call arguments")


class Message(BaseModel):
    """A single message in a conversation.

    For tool-use training, the flow is:
    1. user: asks a question
    2. assistant: decides to call a tool (content explains reasoning, tool_calls contains the call)
    3. tool: returns the tool result (content is the result, tool_call_id references the call)
    4. assistant: interprets the result for the user
    """

    role: MessageRole
    content: str = Field(min_length=1)
    tool_calls: list[ToolCall] | None = Field(default=None, description="Tool calls made by the assistant")
    tool_call_id: str | None = Field(default=None, description="ID of the tool call this message responds to")


class GenerationMethod(str, Enum):
    """How the training example was produced."""

    SYNTHETIC = "synthetic"
    RFC_EXTRACTION = "rfc_extraction"
    ICANN_EXTRACTION = "icann_extraction"
    IANA_EXTRACTION = "iana_extraction"
    WIPO_EXTRACTION = "wipo_extraction"
    MANUAL = "manual"


class ExampleFormat(str, Enum):
    """The conversational format of the example."""

    INSTRUCTION = "instruction"  # Single Q&A turn
    MULTI_TURN = "multi_turn"  # Multi-turn conversation
    SCENARIO = "scenario"  # Scenario-based problem solving
    TOOL_USE = "tool_use"  # Tool-calling with result interpretation


class TrainingExample(BaseModel):
    """A single training example for the dataset.

    This is the canonical record format. All generators produce these,
    all validators check these, and all exporters consume these.
    """

    # --- Identity ---
    id: str = Field(description="Unique ID: {category}-{subcategory}-{seq:04d}")

    # --- Taxonomy position ---
    category: str = Field(description="Category slug from taxonomy")
    subcategory: str = Field(description="Subcategory slug from taxonomy")
    topic: str = Field(description="Specific topic name")

    # --- Content ---
    difficulty: str = Field(description="beginner | intermediate | advanced | expert")
    format: ExampleFormat = Field(default=ExampleFormat.INSTRUCTION)
    messages: list[Message] = Field(min_length=2, description="At least system + user + assistant")

    # --- Provenance ---
    sources: list[str] = Field(default_factory=list, description="Source references (RFCs, documents)")
    generated_by: GenerationMethod = Field(default=GenerationMethod.SYNTHETIC)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(default="0.1.0")

    # --- Quality ---
    token_count: int | None = Field(default=None, description="Approximate token count (set by validator)")
    quality_score: float | None = Field(default=None, description="0.0-1.0 quality score (set by validator)")

    @computed_field
    @property
    def content_hash(self) -> str:
        """SHA-256 hash of message content for deduplication."""
        content = json.dumps(
            [{"role": m.role.value, "content": m.content} for m in self.messages],
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @model_validator(mode="after")
    def validate_message_structure(self) -> "TrainingExample":
        """Ensure messages follow expected patterns."""
        roles = [m.role for m in self.messages]

        # Must have at least a user and assistant message
        if MessageRole.USER not in roles:
            raise ValueError("Messages must include at least one user message")
        if MessageRole.ASSISTANT not in roles:
            raise ValueError("Messages must include at least one assistant message")

        # System message, if present, must be first
        if MessageRole.SYSTEM in roles and roles[0] != MessageRole.SYSTEM:
            raise ValueError("System message must be the first message")

        # Tool messages must follow an assistant message or another tool message
        # (multiple tool results can follow a single assistant tool_calls message)
        for i, msg in enumerate(self.messages):
            if msg.role == MessageRole.TOOL:
                if i == 0:
                    raise ValueError("Tool message cannot be the first message")
                prev_role = self.messages[i - 1].role
                if prev_role not in (MessageRole.ASSISTANT, MessageRole.TOOL):
                    raise ValueError("Tool message must follow an assistant or tool message")

        return self


class DatasetMetadata(BaseModel):
    """Metadata for an exported dataset file."""

    name: str = "oracle-domain-expert"
    version: str = "0.1.0"
    description: str = "Domain name industry expert training dataset"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    example_count: int = 0
    categories: list[str] = Field(default_factory=list)
    difficulty_distribution: dict[str, int] = Field(default_factory=dict)
    format_distribution: dict[str, int] = Field(default_factory=dict)
    total_tokens: int = 0
