from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectContract:
    """Editable project values with all runtime paths derived from them."""

    project_name: str
    project_dir: Path
    workbench_dir: Path
    runtime_dir: Path
    base_image: str = "docker://spack/rockylinux8:develop"
    r_version: str = "4.5.1"
    python_version: str = "3.14"
    slurm_partition: str = "hsph"
    slurm_cpus: int = 12
    slurm_mem: str = "32G"
    slurm_hours: int = 6
    enable_direnv: bool = False

    @property
    def singularity_def(self) -> Path:
        return self.project_dir / ".devcontainer" / "Singularity.def"

    @property
    def singularity_sif(self) -> Path:
        return self.project_dir / ".devcontainer" / "Singularity.sif"

    @property
    def spack_yaml_path(self) -> Path:
        return self.project_dir / "spack.yaml"

    @property
    def rproject_toml_path(self) -> Path:
        return self.project_dir / "rproject.toml"

    @property
    def pyproject_toml_path(self) -> Path:
        return self.project_dir / "pyproject.toml"

    @property
    def container_home(self) -> Path:
        return self.project_dir / ".container-home"

    @property
    def container_tmp(self) -> Path:
        return self.project_dir / ".container-tmp"

    @property
    def submitit_dir(self) -> Path:
        return self.project_dir / "slurm" / "submitit"

    @property
    def launch_script(self) -> Path:
        return self.project_dir / "slurm" / "launch" / "launch_container.sh"

    def ensure_directories(self) -> None:
        for path in [
            self.runtime_dir,
            self.singularity_def.parent,
            self.container_home,
            self.container_tmp,
            self.submitit_dir,
            self.launch_script.parent,
            self.project_dir / "env",
        ]:
            path.mkdir(parents=True, exist_ok=True)
