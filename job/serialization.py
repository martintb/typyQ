from __future__ import annotations

import json
import pickle
from dataclasses import dataclass, asdict, fields
from getpass import getuser
from pathlib import Path
from typing import Any, Dict, Tuple, Type

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - fallback for older interpreters
    import tomli as tomllib  # type: ignore


@dataclass
class JobModel:
    job_class: str
    run_number: int = 0
    walltime: float = 4
    exclusive: bool = False
    memory: int | None = None
    virtual_memory: int | None = None
    dependent_on: int | None = None
    num_procs: int = 1
    queue_file: str | None = None
    queue_name: str | None = None
    name: str | None = None
    email: str | None = None
    user: str = getuser()
    export_env: bool = False
    node: str | None = None
    pe: str | None = None
    reserve: bool = False
    ppri: int | None = None
    gpu: bool = False
    standby: bool = False
    dependency_type: str = "afterok"
    notify: int | None = None
    notify_signal: str = "SIGTERM"

    @classmethod
    def from_job(cls, job_obj: Any) -> "JobModel":
        data: Dict[str, Any] = {field.name: getattr(job_obj, field.name, None) for field in fields(cls)}
        data["job_class"] = job_obj.__class__.__name__
        return cls(**data)

    def apply_to_job(self, job_obj: Any) -> Any:
        for field in fields(self):
            if field.name == "job_class":
                continue
            setattr(job_obj, field.name, getattr(self, field.name))
        return job_obj


def ensure_toml_path(path: str | Path) -> Path:
    path = Path(path)
    if path.suffix.lower() == ".toml":
        return path
    return path.with_suffix(".toml")


def format_toml_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value)


def dump_toml(data: Dict[str, Any]) -> str:
    lines = [f"{key} = {format_toml_value(value)}" for key, value in data.items()]
    return "\n".join(lines) + "\n"


def load_toml(path: Path) -> Dict[str, Any]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def resolve_job_class(name: str) -> Type[Any]:
    from typyQ import job

    candidates = {
        cls.__name__: cls
        for cls in (
            job.Job,
            job.GridEngineJob,
            job.VenusJob,
            job.RuthJob,
            job.FarberJob,
            job.NoQJob,
            job.WraithJob,
            job.NeonJob,
            job.SLURMJob,
            job.OpuntiaJob,
            job.RARITANJob,
            job.StampedeJob,
            job.PBSJob,
            job.CarverJob,
        )
    }
    try:
        return candidates[name]
    except KeyError:
        raise ValueError("Unknown job class: {}".format(name))


def instantiate_job(model: JobModel) -> Any:
    cls = resolve_job_class(model.job_class)
    job_obj = cls()
    return model.apply_to_job(job_obj)


def load_job_model(path: str | Path) -> Tuple[JobModel, bool]:
    path = Path(path)
    if path.suffix.lower() == ".toml":
        data = load_toml(path)
        model = JobModel(**data)
        return model, False

    with path.open("rb") as fh:
        legacy_job = pickle.load(fh)
    model = JobModel.from_job(legacy_job)
    return model, True


def save_job_model(model: JobModel, path: str | Path) -> Path:
    target = ensure_toml_path(path)
    content = dump_toml(asdict(model))
    target.write_text(content)
    return target


def migrate_pickle(source: str | Path, destination: str | Path | None = None) -> Path:
    model, legacy = load_job_model(source)
    if not legacy:
        return ensure_toml_path(source)
    target = ensure_toml_path(destination or source)
    return save_job_model(model, target)
