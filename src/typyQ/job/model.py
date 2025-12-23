"""Structured job model and serialization helpers."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from getpass import getuser
from importlib import import_module
from pathlib import Path
import pickle
from typing import Any, Iterable
import tomllib
import tomli_w

DEFAULT_EXTENSION = ".job.toml"


@dataclass
class JobModel:
    """Serializable representation of a job configuration."""

    job_class: str
    run_number: int = 0
    walltime: float = 4
    exclusive: bool = False
    memory: Any = None
    virtual_memory: Any = None
    dependent_on: Any = None
    num_procs: int = 1
    queue_file: str | None = None
    queue_name: str | None = None
    name: str | None = None
    email: str | None = None
    user: str = field(default_factory=getuser)
    export_env: bool = False
    node: str | None = None
    pe: str | None = None
    reserve: bool = False
    ppri: Any = None
    gpu: bool = False
    standby: bool = False
    dependency_type: str = "afterok"
    notify: Any = None
    notify_signal: str = "SIGTERM"
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_job(cls, job: Any) -> "JobModel":
        field_names = {f.name for f in fields(cls)} - {"extras"}
        values: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        for key, val in vars(job).items():
            if key in field_names:
                values[key] = val
            else:
                extras[key] = val

        job_class = f"{job.__class__.__module__}.{job.__class__.__name__}"
        return cls(job_class=job_class, extras=extras, **values)

    def to_job(self) -> Any:
        module_name, class_name = self.job_class.rsplit(".", 1)
        module = import_module(module_name)
        job_cls = getattr(module, class_name)
        job = job_cls()

        for field_obj in fields(self):
            if field_obj.name in {"job_class", "extras"}:
                continue
            setattr(job, field_obj.name, getattr(self, field_obj.name))

        for key, val in self.extras.items():
            setattr(job, key, val)

        return job


def normalize_job_path(path: Path) -> Path:
    """Ensure job paths use the TOML extension."""
    if path.suffix in {"", ".pkl"}:
        return path.with_suffix(DEFAULT_EXTENSION)
    return path


def read_model(path: Path) -> JobModel:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return JobModel(**data)


def write_model(path: Path, model: JobModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(tomli_w.dumps(asdict(model)).encode("utf-8"))


def save_job(path: Path, job: Any) -> Path:
    target_path = normalize_job_path(path)
    write_model(target_path, JobModel.from_job(job))
    return target_path


def load_job(path: Path, migrate_legacy: bool = True) -> tuple[Any, Path, bool]:
    """Load a job configuration from TOML or migrate a legacy pickle.

    Returns the job instance, the path used for saving updates, and a flag
    indicating whether migration occurred.
    """

    path = Path(path)
    if path.suffix == "":
        path = normalize_job_path(path)
    if path.suffix == ".pkl":
        with path.open("rb") as handle:
            job = pickle.load(handle)
        target_path = normalize_job_path(path)
        migrated = False
        if migrate_legacy:
            write_model(target_path, JobModel.from_job(job))
            migrated = True
        return job, target_path, migrated

    model = read_model(path)
    return model.to_job(), path, False


def dump_job(job: Any) -> str:
    """Render a job configuration as TOML text."""
    return tomli_w.dumps(asdict(JobModel.from_job(job)))


__all__: Iterable[str] = [
    "DEFAULT_EXTENSION",
    "JobModel",
    "dump_job",
    "load_job",
    "normalize_job_path",
    "read_model",
    "save_job",
    "write_model",
]
