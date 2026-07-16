#' ---
#' title: 4  01 Project Contract
#' ---
#' 

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectContract:
    """Declarative description of an RSE Workbench project."""

    # -------------------------------------------------------------------------
    # Project identity
    # -------------------------------------------------------------------------

    project_name: str
    project_root: Path
    workbench_dir: Path

    # -------------------------------------------------------------------------
    # Platform configuration
    # -------------------------------------------------------------------------

    image_mode: str = "build"          # build | sandbox
    base_image: str = "docker://spack/rockylinux9:develop"

    r_version: str = "4.5.1"
    python_version: str = "3.14"

    enable_direnv: bool = True

    # -------------------------------------------------------------------------
    # Slurm defaults
    # -------------------------------------------------------------------------

    slurm_build_partition: str = "hsph"
    slurm_build_cpus: int = 6
    slurm_build_mem: str = "32G"
    slurm_build_hours: int = 2
    slurm_email: str | None = None

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def __post_init__(self):

        if not self.project_name:
            raise ValueError("project_name must not be empty.")

        if self.image_mode not in {"build", "sandbox"}:
            raise ValueError(
                "image_mode must be either 'build' or 'sandbox'."
            )

    # -------------------------------------------------------------------------
    # Core directories
    # -------------------------------------------------------------------------

    @property
    def project_dir(self) -> Path:
        return self.project_root / self.project_name

    @property
    def runtime_dir(self) -> Path:
        return self.workbench_dir / "projects" / self.project_name

    @property
    def devcontainer_dir(self) -> Path:
        return self.project_dir / ".devcontainer"

    @property
    def env_dir(self) -> Path:
        return self.project_dir / "env"

    @property
    def filter_bin_dir(self) -> Path:
        return self.env_dir / "bin"

    @property
    def container_home(self) -> Path:
        return self.project_dir / ".container-home"

    @property
    def container_tmp(self) -> Path:
        return self.project_dir / ".container-tmp"

    # -------------------------------------------------------------------------
    # Slurm directories
    # -------------------------------------------------------------------------

    @property
    def slurm_dir(self) -> Path:
        return self.project_dir / "slurm"

    @property
    def submitit_dir(self) -> Path:
        return self.slurm_dir / "submitit"

    @property
    def launch_dir(self) -> Path:
        return self.slurm_dir / "launch"

    @property
    def launch_log_dir(self) -> Path:
        return self.launch_dir / "logs"

    @property
    def launch_script(self) -> Path:
        return self.launch_dir / "launch_container.sbatch"

    @property
    def install_dir(self) -> Path:
        return self.slurm_dir / "install"

    @property
    def install_log_dir(self) -> Path:
        return self.install_dir / "logs"

    @property
    def install_script(self) -> Path:
        return self.install_dir / "install_container.sbatch"

    # -------------------------------------------------------------------------
    # Platform files
    # -------------------------------------------------------------------------

    @property
    def singularity_def(self) -> Path:
        return self.devcontainer_dir / "Singularity.def"

    @property
    def build_image(self) -> Path:
        return self.devcontainer_dir / "Singularity.sif"

    @property
    def sandbox_image(self) -> Path:
        return Path(
            f"/tmp/{os.environ['USER']}-{self.project_name}-sandbox"
        )

    @property
    def singularity_image(self) -> Path:
        if self.image_mode == "sandbox":
            return self.sandbox_image
        return self.build_image

    @property
    def spack_yaml(self) -> Path:
        return self.project_dir / "spack.yaml"

    @property
    def rproject_toml(self) -> Path:
        return self.project_dir / "rproject.toml"

    @property
    def pyproject_toml(self) -> Path:
        return self.project_dir / "pyproject.toml"

    @property
    def activate_script(self) -> Path:
        return self.env_dir / "activate.sh"

    # -------------------------------------------------------------------------
    # Filesystem helpers
    # -------------------------------------------------------------------------

    @property
    def directories(self) -> list[Path]:
        """Directories expected to exist for every project."""

        return [
            self.project_dir,
            self.devcontainer_dir,
            self.env_dir,
            self.filter_bin_dir,
            self.container_home,
            self.container_tmp,
            self.submitit_dir,
            self.launch_dir,
            self.launch_log_dir,
            self.install_dir,
            self.install_log_dir,
        ]

    def create_directories(self) -> None:
        """Create the standard project directory structure."""

        for path in self.directories:
            path.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Convenience
    # -------------------------------------------------------------------------

    def summary(self) -> dict:

        return {
            "project_name": self.project_name,
            "project_dir": str(self.project_dir),
            "runtime_dir": str(self.runtime_dir),
            "image_mode": self.image_mode,
            "base_image": self.base_image,
            "singularity_image": str(self.singularity_image),
            "singularity_definition": str(self.singularity_def),
            "spack_yaml": str(self.spack_yaml),
            "rproject_toml": str(self.rproject_toml),
            "pyproject_toml": str(self.pyproject_toml),
            "env_dir": str(self.env_dir),
            "activate_script": str(self.activate_script),
            "container_home": str(self.container_home),
            "container_tmp": str(self.container_tmp),
            "partition": self.slurm_build_partition,
            "cpus": self.slurm_build_cpus,
            "memory": self.slurm_build_mem,
            "hours": self.slurm_build_hours,
        }

    def __repr__(self) -> str:

        return (
            f"ProjectContract("
            f"project='{self.project_name}', "
            f"mode='{self.image_mode}', "
            f"project_dir='{self.project_dir}')"
        )
