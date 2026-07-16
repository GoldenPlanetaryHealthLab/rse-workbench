from __future__ import annotations

def build_container(singularity_def, SINGULARITY_IMAGE):
    from spython.main import Client
    from pathlib import Path
    import os

    job_id = os.environ.get("SLURM_JOB_ID", "local")
    user = os.environ["USER"]
    tmp_root = Path(f"/tmp/{user}-rse-workbench-{job_id}")
    singularity_tmp = tmp_root / "singularity-tmp"
    singularity_cache = tmp_root / "singularity-cache"

    singularity_tmp.mkdir(parents=True, exist_ok=True)
    singularity_cache.mkdir(parents=True, exist_ok=True)

    os.environ["SINGULARITY_TMPDIR"] = str(singularity_tmp)
    os.environ["SINGULARITY_CACHEDIR"] = str(singularity_cache)
    os.environ["APPTAINER_TMPDIR"] = str(singularity_tmp)
    os.environ["APPTAINER_CACHEDIR"] = str(singularity_cache)

    return Client.build(
        image=str(SINGULARITY_IMAGE),
        recipe=str(singularity_def),
        options=["--fakeroot", "--force"],
        sudo=False,
        return_result=True,
    )


INSTALL_RUNTIME_COMMAND = r"""
set -euo pipefail

df -h /tmp /work

. /opt/spack/share/spack/setup-env.sh
cd /work

spack env activate -d .
spack concretize --force
spack install --deprecated --fail-fast -j8 --no-checksum

rv sync
"""


from pathlib import Path
from typing import Any

def install_in_container(
    project_dir: Path,
    SINGULARITY_IMAGE: Path,
    runtime_command: str = INSTALL_RUNTIME_COMMAND,
) -> dict[str, Any]:
    """Install the project Spack and data science environments inside the final SIF."""

    from spython.main import Client
    from pathlib import Path
    import os

    project_dir = Path(project_dir)
    SINGULARITY_IMAGE = Path(SINGULARITY_IMAGE)

    container_home = project_dir / ".container-home"
    container_tmp = project_dir / ".container-tmp"

    container_home.mkdir(parents=True, exist_ok=True)
    container_tmp.mkdir(parents=True, exist_ok=True)

    os.environ.update({
        "SINGULARITYENV_R_LIBS": "",
        "SINGULARITYENV_R_LIBS_USER": "",
        "SINGULARITYENV_R_LIBS_SITE": "",
        "SINGULARITYENV_SPACK_DISABLE_LOCAL_CONFIG": "true",
    })

    options = [
        "--cleanenv",
        "--home", f"{container_home}:/home/rse",
        "--bind", f"{project_dir}:/work",
        "--bind", f"{container_tmp}:/tmp",
    ]

    return Client.execute(
        image=str(SINGULARITY_IMAGE),
        command=["bash", "--noprofile", "--norc", "-lc", runtime_command],
        options=options,
        sudo=False,
        return_result=True,
    )
