"""Abstract base class for training data generators."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from oracle.schema import FailedGeneration, TrainingExample
from oracle.taxonomy import Category, Subcategory, Topic

logger = logging.getLogger(__name__)


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
        """Load examples from a JSONL file, skipping corrupt lines."""
        examples = []
        skipped = 0
        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    examples.append(TrainingExample.model_validate_json(line))
                except Exception as e:
                    skipped += 1
                    logger.warning("Skipping corrupt line %d in %s: %s", line_num, path.name, e)
                    continue

        if skipped:
            logger.warning("Skipped %d corrupt line(s) in %s, loaded %d valid", skipped, path.name, len(examples))

        return examples

    # ------------------------------------------------------------------
    # Failure tracking
    # ------------------------------------------------------------------

    FAILURES_FILE = "_failures.jsonl"

    def save_failure(self, failure: FailedGeneration) -> Path:
        """Append a failed generation record to the failures file."""
        path = self.output_dir / self.FAILURES_FILE
        with open(path, "a") as f:
            f.write(failure.model_dump_json() + "\n")
        return path

    @staticmethod
    def load_failures(output_dir: Path) -> list[FailedGeneration]:
        """Load all failure records from the failures file."""
        path = output_dir / BaseGenerator.FAILURES_FILE
        if not path.exists():
            return []

        failures = []
        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    failures.append(FailedGeneration.model_validate_json(line))
                except Exception as e:
                    logger.warning("Skipping corrupt failure line %d: %s", line_num, e)
        return failures

    @staticmethod
    def write_failures(output_dir: Path, failures: list[FailedGeneration]) -> Path:
        """Overwrite the failures file with an updated list (used after retries)."""
        path = output_dir / BaseGenerator.FAILURES_FILE
        if not failures:
            # Clean up empty file
            if path.exists():
                path.unlink()
            return path
        with open(path, "w") as f:
            for failure in failures:
                f.write(failure.model_dump_json() + "\n")
        return path

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
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    example_id = data.get("id", "")
                    if example_id.startswith(prefix):
                        try:
                            seq = int(example_id[len(prefix):])
                            max_seq = max(max_seq, seq)
                        except ValueError:
                            continue

        return max_seq + 1
