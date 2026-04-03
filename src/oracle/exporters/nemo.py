"""NeMo / OpenAI-compatible JSONL exporter.

Exports training examples to formats suitable for fine-tuning with
NVIDIA NeMo, Hugging Face TRL, or OpenAI fine-tuning APIs.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from oracle.schema import DatasetMetadata, MessageRole, TrainingExample

logger = logging.getLogger(__name__)


def to_chat_messages(example: TrainingExample, include_thinking: bool = True) -> list[dict]:
    """Convert a TrainingExample to OpenAI-style chat messages.

    Handles tool-use messages with tool_calls and tool responses.
    When include_thinking is True, prepends <think>...</think> to assistant
    content for messages that have a thinking trace (Nemotron-3-Nano format).
    """
    messages = []
    for m in example.messages:
        content = m.content

        # Prepend thinking trace to assistant messages
        if include_thinking and m.thinking and m.role == MessageRole.ASSISTANT:
            content = f"<think>\n{m.thinking}\n</think>\n{content}"

        msg: dict = {"role": m.role.value, "content": content}

        # Assistant messages may include tool calls
        if m.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                }
                for i, tc in enumerate(m.tool_calls)
            ]

        # Tool messages reference the call they respond to
        if m.tool_call_id:
            msg["tool_call_id"] = m.tool_call_id

        messages.append(msg)

    return messages


def export_openai_chat(
    examples: list[TrainingExample],
    output_path: Path,
) -> Path:
    """Export to OpenAI chat fine-tuning format.

    Each line is: {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}

    This format is also compatible with NeMo SFT and Hugging Face TRL.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for example in examples:
            record = {"messages": to_chat_messages(example)}
            f.write(json.dumps(record) + "\n")

    logger.info("Exported %d examples to %s (OpenAI chat format)", len(examples), output_path)
    return output_path


def export_nemo_sft(
    examples: list[TrainingExample],
    output_path: Path,
) -> Path:
    """Export to NeMo SFT format.

    Each line is: {"system": "...", "conversations": [{"role": "user", "content": "..."}, ...]}

    This is the format NeMo's SFT trainer expects for multi-turn data.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for example in examples:
            messages = to_chat_messages(example)

            system_content = ""
            conversations = []
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    entry = {"role": msg["role"], "content": msg["content"]}
                    # Preserve tool-use fields
                    if "tool_calls" in msg:
                        entry["tool_calls"] = msg["tool_calls"]
                    if "tool_call_id" in msg:
                        entry["tool_call_id"] = msg["tool_call_id"]
                    conversations.append(entry)

            record = {
                "system": system_content,
                "conversations": conversations,
            }
            f.write(json.dumps(record) + "\n")

    logger.info("Exported %d examples to %s (NeMo SFT format)", len(examples), output_path)
    return output_path


def export_alpaca(
    examples: list[TrainingExample],
    output_path: Path,
) -> Path:
    """Export to Alpaca/instruction format.

    Each line is: {"instruction": "...", "input": "", "output": "..."}

    Simple format suitable for basic instruction tuning. Only uses the
    first user/assistant pair; multi-turn data is flattened.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for example in examples:
            messages = to_chat_messages(example)

            instruction = ""
            output_text = ""
            system_text = ""

            for msg in messages:
                if msg["role"] == "system":
                    system_text = msg["content"]
                elif msg["role"] == "user" and not instruction:
                    instruction = msg["content"]
                elif msg["role"] == "assistant" and not output_text:
                    output_text = msg["content"]

            record = {
                "instruction": instruction,
                "input": system_text,
                "output": output_text,
            }
            f.write(json.dumps(record) + "\n")

    logger.info("Exported %d examples to %s (Alpaca format)", len(examples), output_path)
    return output_path


def export_with_metadata(
    examples: list[TrainingExample],
    output_dir: Path,
    export_format: str = "openai_chat",
    name: str = "oracle-domain-expert",
    version: str = "0.1.0",
) -> tuple[Path, Path]:
    """Export examples with an accompanying metadata file.

    Returns (data_path, metadata_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export the data
    data_filename = f"{name}-{version}.jsonl"
    data_path = output_dir / data_filename

    exporters = {
        "openai_chat": export_openai_chat,
        "nemo_sft": export_nemo_sft,
        "alpaca": export_alpaca,
    }

    exporter = exporters.get(export_format)
    if not exporter:
        raise ValueError(f"Unknown format: {export_format}. Choose from: {list(exporters.keys())}")

    exporter(examples, data_path)

    # Build metadata
    difficulty_counts = Counter(e.difficulty for e in examples)
    format_counts = Counter(e.format.value for e in examples)
    categories = sorted(set(e.category for e in examples))
    total_tokens = sum(e.token_count or 0 for e in examples)

    metadata = DatasetMetadata(
        name=name,
        version=version,
        created_at=datetime.now(timezone.utc),
        example_count=len(examples),
        categories=categories,
        difficulty_distribution=dict(difficulty_counts),
        format_distribution=dict(format_counts),
        total_tokens=total_tokens,
    )

    meta_path = output_dir / f"{name}-{version}.meta.json"
    with open(meta_path, "w") as f:
        f.write(metadata.model_dump_json(indent=2))

    logger.info("Wrote metadata to %s", meta_path)
    return data_path, meta_path


# ---------------------------------------------------------------------------
# Train / Validation / Test split
# ---------------------------------------------------------------------------

def split_dataset(
    examples: list[TrainingExample],
    train_ratio: float = 0.85,
    val_ratio: float = 0.10,
    test_ratio: float = 0.05,
    seed: int = 42,
    stratify_by: str = "category",
) -> tuple[list[TrainingExample], list[TrainingExample], list[TrainingExample]]:
    """Split examples into train/validation/test sets.

    Stratifies by category (default) or difficulty to ensure each split
    has proportional representation across the dataset.

    Args:
        examples: Full dataset to split.
        train_ratio: Fraction for training (default 0.85).
        val_ratio: Fraction for validation (default 0.10).
        test_ratio: Fraction for test (default 0.05).
        seed: Random seed for reproducibility.
        stratify_by: Field to stratify on ("category" or "difficulty").

    Returns:
        (train, validation, test) tuple of example lists.
    """
    import random

    if abs(train_ratio + val_ratio + test_ratio - 1.0) >= 1e-6:
        raise ValueError(f"Ratios must sum to 1.0 (got {train_ratio + val_ratio + test_ratio})")

    rng = random.Random(seed)

    # Group examples by stratification key
    groups: dict[str, list[TrainingExample]] = {}
    for ex in examples:
        key = getattr(ex, stratify_by, "default")
        groups.setdefault(key, []).append(ex)

    train, val, test = [], [], []

    for key in sorted(groups.keys()):
        group = groups[key]
        rng.shuffle(group)

        n = len(group)
        n_val = max(1, round(n * val_ratio)) if n >= 3 else 0
        n_test = max(1, round(n * test_ratio)) if n >= 3 else 0
        n_train = n - n_val - n_test

        train.extend(group[:n_train])
        val.extend(group[n_train : n_train + n_val])
        test.extend(group[n_train + n_val :])

    logger.info(
        "Split %d examples: %d train / %d val / %d test (stratified by %s)",
        len(examples), len(train), len(val), len(test), stratify_by,
    )

    return train, val, test


def export_splits(
    examples: list[TrainingExample],
    output_dir: Path,
    export_format: str = "openai_chat",
    name: str = "oracle-domain-expert",
    version: str = "0.1.0",
    train_ratio: float = 0.85,
    val_ratio: float = 0.10,
    test_ratio: float = 0.05,
    seed: int = 42,
) -> dict[str, Path]:
    """Export dataset with train/val/test splits.

    Returns dict of {split_name: file_path}.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = split_dataset(
        examples, train_ratio, val_ratio, test_ratio, seed,
    )

    exporters = {
        "openai_chat": export_openai_chat,
        "nemo_sft": export_nemo_sft,
        "alpaca": export_alpaca,
    }
    exporter = exporters.get(export_format)
    if not exporter:
        raise ValueError(f"Unknown format: {export_format}. Choose from: {', '.join(exporters)}")

    paths = {}
    for split_name, split_data in [("train", train), ("val", val), ("test", test)]:
        if split_data:
            path = output_dir / f"{name}-{version}.{split_name}.jsonl"
            exporter(split_data, path)
            paths[split_name] = path
            logger.info("Exported %s split: %d examples → %s", split_name, len(split_data), path)

    return paths
