"""分阶段运行 Table 5 隐藏实验语义的判别矩阵。"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "output" / "results" / "table5_hypotheses"
CASE_TARGETS = {
    "present60": (4,),
    "rectangle60": (10, 12),
}
REPEATED_FIXED_KEYS = {
    "ones": 0xFFFFFFFFFFFFFFFF,
    "alternating_a": 0xAAAAAAAAAAAAAAAA,
    "alternating_5": 0x5555555555555555,
}


@dataclass(frozen=True, slots=True)
class HypothesisJob:
    """一个可独立断点续跑的 Table 5 判别实验。"""

    name: str
    case: str
    targets: tuple[int, ...]
    algorithm: str
    key_treatment: str
    constant_values: str | None = None
    round_keys: tuple[int, ...] | None = None

    def output_path(self, output_dir: Path) -> Path:
        return output_dir / f"{self.case}_{self.name}.json"

    def command(
        self,
        python: str,
        output_dir: Path,
        *,
        time_limit: float | None,
        record_witness: bool,
    ) -> list[str]:
        command = [
            python,
            str(ROOT / "experiments" / "reproduce_table5_spn.py"),
            self.case,
            "--algorithm",
            self.algorithm,
            "--key-treatment",
            self.key_treatment,
            "--targets",
            *(str(target) for target in self.targets),
            "--output",
            str(self.output_path(output_dir)),
        ]
        if self.constant_values is not None:
            command.extend(("--constant-values", self.constant_values))
        if self.round_keys is not None:
            command.append("--round-keys")
            command.extend(f"0x{key:016x}" for key in self.round_keys)
        if time_limit is not None:
            command.extend(("--time-limit", str(time_limit)))
        if record_witness:
            command.append("--record-witness")
        return command


def _smoke_jobs() -> tuple[HypothesisJob, ...]:
    """优先区分字面 Rule 4、零密钥和常量取值解释。"""
    variants = (
        ("paper_unknown", "paper", None),
        ("zero_key_unknown", "ignore-rule4", None),
        ("zero_key_c0000", "ignore-rule4", "0000"),
        ("zero_key_c1111", "ignore-rule4", "1111"),
    )
    return tuple(
        HypothesisJob(
            name=name,
            case=case,
            targets=targets,
            algorithm="bdpt-exact",
            key_treatment=key_treatment,
            constant_values=constant_values,
        )
        for case, targets in CASE_TARGETS.items()
        for name, key_treatment, constant_values in variants
    )


def _constant_jobs() -> tuple[HypothesisJob, ...]:
    """在零轮密钥假设下穷举论文未给出的四个输入常量。"""
    return tuple(
        HypothesisJob(
            name=f"zero_key_c{value:04b}",
            case=case,
            targets=targets,
            algorithm="bdpt-exact",
            key_treatment="ignore-rule4",
            constant_values=f"{value:04b}",
        )
        for case, targets in CASE_TARGETS.items()
        for value in range(16)
    )


def _fixed_key_jobs() -> tuple[HypothesisJob, ...]:
    """测试几类逐轮重复的具体非零轮密钥。"""
    rounds = 9
    return tuple(
        HypothesisJob(
            name=f"fixed_{label}_unknown",
            case=case,
            targets=targets,
            algorithm="bdpt-exact",
            key_treatment="fixed",
            round_keys=(key,) * rounds,
        )
        for case, targets in CASE_TARGETS.items()
        for label, key in REPEATED_FIXED_KEYS.items()
    )


def build_jobs(phase: str) -> tuple[HypothesisJob, ...]:
    """生成指定阶段的去重实验列表。"""
    phases = {
        "smoke": _smoke_jobs(),
        "constants": _constant_jobs(),
        "fixed-keys": _fixed_key_jobs(),
    }
    if phase != "all":
        return phases[phase]
    jobs: dict[tuple[Any, ...], HypothesisJob] = {}
    for phase_jobs in phases.values():
        for job in phase_jobs:
            identity = (
                job.case,
                job.targets,
                job.algorithm,
                job.key_treatment,
                job.constant_values,
                job.round_keys,
            )
            jobs.setdefault(identity, job)
    return tuple(jobs.values())


def summarize_jobs(
    jobs: tuple[HypothesisJob, ...], output_dir: Path
) -> dict[str, Any]:
    """汇总判别位是否得到论文要求的 balanced zero。"""
    records: list[dict[str, Any]] = []
    for job in jobs:
        path = job.output_path(output_dir)
        record: dict[str, Any] = {
            **asdict(job),
            "output": str(path),
            "status": "missing",
            "target_parities": {},
            "matches_requested_targets": False,
        }
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            target_parities = {
                str(target): payload.get("results", {})
                .get(str(target), {})
                .get("parity")
                for target in job.targets
            }
            complete = all(parity is not None for parity in target_parities.values())
            record.update(
                {
                    "status": "complete" if complete else "partial",
                    "target_parities": target_parities,
                    "matches_requested_targets": complete
                    and all(parity == "zero" for parity in target_parities.values()),
                }
            )
        records.append(record)
    return {
        "criterion": "所有请求目标位均为 zero",
        "jobs": records,
        "matching_jobs": [
            record["name"] + ":" + record["case"]
            for record in records
            if record["matches_requested_targets"]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase",
        choices=("smoke", "constants", "fixed-keys", "all"),
        default="smoke",
        nargs="?",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--record-witness", action="store_true")
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    jobs = build_jobs(args.phase)
    for index, job in enumerate(jobs, start=1):
        command = job.command(
            sys.executable,
            output_dir,
            time_limit=args.time_limit,
            record_witness=args.record_witness,
        )
        print(f"[{index}/{len(jobs)}] {' '.join(command)}", flush=True)
        if args.execute:
            subprocess.run(command, cwd=ROOT, check=True)

    summary = summarize_jobs(jobs, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / f"summary_{args.phase}.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"汇总: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
