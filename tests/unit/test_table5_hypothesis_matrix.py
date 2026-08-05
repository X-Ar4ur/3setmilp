import json
import sys

from experiments.run_table5_hypothesis_matrix import (
    build_jobs,
    summarize_jobs,
)


def test_table5_hypothesis_phases_have_stable_sizes() -> None:
    assert len(build_jobs("smoke")) == 8
    assert len(build_jobs("constants")) == 32
    assert len(build_jobs("fixed-keys")) == 6
    assert len(build_jobs("all")) == 42


def test_fixed_key_job_passes_nine_round_keys(tmp_path) -> None:
    job = build_jobs("fixed-keys")[0]
    command = job.command(
        sys.executable,
        tmp_path,
        time_limit=30.0,
        record_witness=True,
    )

    round_key_index = command.index("--round-keys")
    output_index = command.index("--output")
    assert output_index < round_key_index
    assert len(command[round_key_index + 1 : round_key_index + 10]) == 9
    assert command[-3:] == ["--time-limit", "30.0", "--record-witness"]


def test_hypothesis_summary_requires_every_requested_target_zero(tmp_path) -> None:
    job = next(
        candidate
        for candidate in build_jobs("smoke")
        if candidate.case == "rectangle60"
    )
    path = job.output_path(tmp_path)
    path.write_text(
        json.dumps(
            {
                "results": {
                    "10": {"parity": "zero"},
                    "12": {"parity": "unknown"},
                }
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_jobs((job,), tmp_path)

    assert summary["jobs"][0]["status"] == "complete"
    assert not summary["jobs"][0]["matches_requested_targets"]
    assert summary["matching_jobs"] == []
