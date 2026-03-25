"""Abstract base class for training data generators."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from oracle.schema import TrainingExample
from oracle.taxonomy import Category, Subcategory, Topic


class BaseGenerator(ABC):
    """Base class that all generators implement.

    A generator takes a taxonomy position (category, subcategory, topic)
    and a difficulty level, and produces one or more TrainingExample records.
    """

    def __init__(self, output_dir: Path, system_prompt: str | None = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if system_prompt is None:
            prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "system.txt"
            self.system_prompt = prompt_path.read_text().strip()
        else:
            self.system_prompt = system_prompt

    @abstractmethod
    async def generate(
        self,
        category: Category,
        subcategory: Subcategory,
        topic: Topic,
        difficulty: str,
        count: int = 1,
    ) -> list[TrainingExample]:
        """Generate training examples for a given topic and difficulty.

        Args:
            category: The top-level category.
            subcategory: The subcategory within the category.
            topic: The specific topic to generate for.
            difficulty: One of beginner, intermediate, advanced, expert.
            count: Number of examples to generate.

        Returns:
            List of validated TrainingExample records.
        """

    def save_examples(self, examples: list[TrainingExample]) -> Path:
        """Append examples to a JSONL file organized by category."""
        if not examples:
            return self.output_dir

        category = examples[0].category
        output_file = self.output_dir / f"{category}.jsonl"

        with open(output_file, "a") as f:
            for example in examples:
                f.write(example.model_dump_json() + "\n")

        return output_file

    @staticmethod
    def load_examples(path: Path) -> list[TrainingExample]:
        """Load examples from a JSONL file."""
        examples = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    examples.append(TrainingExample.model_validate_json(line))
        return examples

    @staticmethod
    def make_id(category_slug: str, subcategory_slug: str, seq: int) -> str:
        """Generate a canonical example ID."""
        return f"{category_slug}-{subcategory_slug}-{seq:04d}"

    def _get_next_seq(self, category_slug: str, subcategory_slug: str) -> int:
        """Find the next available sequence number for a category/subcategory pair."""
        prefix = f"{category_slug}-{subcategory_slug}-"
        output_file = self.output_dir / f"{category_slug}.jsonl"

        max_seq = -1
        if output_file.exists():
            with open(output_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    example_id = data.get("id", "")
                    if example_id.startswith(prefix):
                        try:
                            seq = int(example_id[len(prefix):])
                            max_seq = max(max_seq, seq)
                        except ValueError:
                            continue

        return max_seq + 1
