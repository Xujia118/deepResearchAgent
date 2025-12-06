import heapq
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

# --- Step 1: Priority Planner ---


@dataclass(order=True)
class ResearchTask:
    """
    Data class for a single unit of work.
    We use order=True so heapq can compare tasks based on 'priority'.
    """
    priority: int  # 0=High, 1=Medium, 2=Low
    question: str = field(compare=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)


class TodoList:
    """
    Manages the order of operations using a Priority Queue.
    """

    def __init__(self):
        self.heap = []
        self.entry_count = 0  # Tie-breaker to ensure FIFO for same-priority items

    def add_task(self, question: str, priority: int = 1):
        """
        Pushes a task onto the heap.
        Priority: 0 (High), 1 (Medium), 2 (Low)
        """
        # We push a tuple (priority, entry_count, task) to handle sorting correctly
        task = ResearchTask(priority=priority, question=question)
        heapq.heappush(self.heap, task)
        print(f"➕ Added Task [P{priority}]: {question}")

    def get_next_task(self) -> Optional[ResearchTask]:
        """Pops the highest priority task (lowest integer value)."""
        if not self.heap:
            return None
        return heapq.heappop(self.heap)

    def snapshot(self) -> List[dict]:
        """Returns a list of pending tasks for debugging."""
        # Return a sorted copy without popping
        return [
            {"id": t.id, "priority": t.priority, "question": t.question}
            for t in sorted(self.heap)
        ]

    def is_empty(self):
        return len(self.heap) == 0
