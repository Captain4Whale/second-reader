from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "orchestrate_post_phase_d_parallel_eval.py"
SPEC = importlib.util.spec_from_file_location("post_phase_d_parallel_orchestrator", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
orchestrator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = orchestrator
SPEC.loader.exec_module(orchestrator)


def test_balanced_assign_keeps_one_queue_per_target() -> None:
    tasks = [
        orchestrator.ShardTask(
            job_id=f"job_{index}",
            lane="excerpt",
            stage="runtime",
            item_id=f"unit_{index}",
            shard_id=f"shard_{index}",
            run_id="run",
            expected_outputs=(Path(f"/tmp/out_{index}.json"),),
            weight=weight,
        )
        for index, weight in enumerate([8, 6, 4, 3, 2, 1], start=1)
    ]

    queues = orchestrator.balanced_assign(tasks, target_ids=("target_a", "target_b"))

    assert sorted(queues) == ["target_a", "target_b"]
    assert all(task.target_id == target_id for target_id, queue in queues.items() for task in queue)
    assigned_ids = sorted(task.item_id for queue in queues.values() for task in queue)
    assert assigned_ids == [f"unit_{index}" for index in range(1, 7)]


def test_runtime_check_command_validates_bundle_status() -> None:
    task = orchestrator.ShardTask(
        job_id="job_runtime",
        lane="longspan",
        stage="runtime",
        item_id="window_a",
        shard_id="runtime_window_a",
        run_id="run",
        expected_outputs=(Path("/tmp/window_a.json"),),
        weight=1,
        target_id="target_a",
    )

    command = orchestrator.build_check_command(task)

    assert "window_a.json" in command
    assert "status" in command
    assert "completed" in command


def test_merge_tasks_expect_lane_level_outputs() -> None:
    tasks = orchestrator.merge_tasks()

    assert {task.lane for task in tasks} == {"longspan", "excerpt"}
    assert all(task.stage == "merge" for task in tasks)
    assert all(any(path.name == "aggregate.json" for path in task.expected_outputs) for task in tasks)


def test_flatten_assigned_queues_preserves_target_order() -> None:
    queues = {
        "target_a": [
            orchestrator.ShardTask(
                job_id="job_a1",
                lane="excerpt",
                stage="runtime",
                item_id="unit_a1",
                shard_id="shard_a1",
                run_id="run",
                expected_outputs=(Path("/tmp/out_a1.json"),),
                weight=1,
                target_id="target_a",
            )
        ],
        "target_b": [
            orchestrator.ShardTask(
                job_id="job_b1",
                lane="longspan",
                stage="runtime",
                item_id="unit_b1",
                shard_id="shard_b1",
                run_id="run",
                expected_outputs=(Path("/tmp/out_b1.json"),),
                weight=1,
                target_id="target_b",
            )
        ],
    }

    ordered = orchestrator.flatten_assigned_queues(queues, target_ids=("target_a", "target_b"))

    assert [task.job_id for task in ordered] == ["job_a1", "job_b1"]


def test_launch_all_tasks_launches_everything_before_waiting(monkeypatch) -> None:
    tasks = [
        orchestrator.ShardTask(
            job_id=f"job_{index}",
            lane="excerpt",
            stage="runtime",
            item_id=f"unit_{index}",
            shard_id=f"shard_{index}",
            run_id="run",
            expected_outputs=(Path(f"/tmp/out_{index}.json"),),
            weight=1,
            target_id="target_a" if index % 2 else "target_b",
        )
        for index in range(1, 4)
    ]
    launched: list[str] = []
    waited: list[tuple[list[str], int, str]] = []

    monkeypatch.setattr(orchestrator, "launch_registered_job", lambda task: launched.append(task.job_id))

    def _record_wait(job_ids: list[str], *, poll_seconds: int, label: str) -> None:
        waited.append((job_ids, poll_seconds, label))

    monkeypatch.setattr(orchestrator, "_wait_for_jobs", _record_wait)

    orchestrator.launch_all_tasks(tasks, poll_seconds=17, label="runtime")

    assert launched == ["job_1", "job_2", "job_3"]
    assert waited == [(["job_1", "job_2", "job_3"], 17, "runtime")]
