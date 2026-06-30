#' ---
#' title: RSE Workbench Build Container
#' ---
#' 

from spython.main import Client

Client.build(
    image=str(TMP_SANDBOX),
    recipe=BASE_IMAGE,
    options=["--fakeroot", "--sandbox", "--fix-perms", "--force"],
    sudo=False,
)


def spython_exec(
    command,
    *,
    image=TMP_SANDBOX,
    writable=False,
    fakeroot=False,
    bind_project=False,
):
    options = ["--no-home"]

    if writable:
        options.append("--writable")

    if fakeroot:
        options.append("--fakeroot")

    if bind_project:
        options += ["--bind", f"{PROJECT_DIR}:/work"]

    return Client.execute(
        image=str(image),
        command=["bash", "--noprofile", "--norc", "-c", command],
        options=options,
        sudo=False,
        return_result=True
    )


from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.syntax import Syntax

console = Console()


def normalize_spython_result(result):
    message = result.get("message", "")
    return_code = result.get("return_code", None)

    if isinstance(message, list):
        stdout = message[0] if len(message) > 0 else ""
        stderr = message[1] if len(message) > 1 else ""
    else:
        stdout = message or ""
        stderr = ""

    return {
        "stdout": stdout,
        "stderr": stderr,
        "return_code": return_code,
        "raw": result,
    }


def show_spython(result, *, tail=None):
    normalized = normalize_spython_result(result)

    stdout = normalized["stdout"]
    stderr = normalized["stderr"]
    return_code = normalized["return_code"]

    if tail is not None:
        stdout = "\n".join(stdout.splitlines()[-tail:])
        stderr = "\n".join(stderr.splitlines()[-tail:])

    stdout_panel = Panel(
        Syntax(stdout.rstrip() or "<empty>", "text"),
        title="stdout / message",
        border_style="green",
    )

    stderr_panel = Panel(
        Syntax(stderr.rstrip() or "<empty>", "text"),
        title="stderr",
        border_style="yellow" if return_code == 0 else "red",
    )

    console.print(
        Panel(
            Columns([stdout_panel, stderr_panel]),
            title=f"Exit code: {return_code}",
            border_style="green" if return_code == 0 else "red",
        )
    )

    return normalized


show_spython(
    spython_exec(
        ". /opt/spack/share/spack/setup-env.sh && spack --version"
    )
)


show_spython(
    spython_exec(
        "mkdir -p /work",
        writable=True
    )
)


show_spython(
    spython_exec(
        "ls -l /work",
        writable=True
    )
)


show_spython(
    spython_exec(
        "ls -l /work",
        writable=True,
        bind_project=True
    )
)


show_spython(
    spython_exec(
        ". /opt/spack/share/spack/setup-env.sh && R --version",
        bind_project=True
    )
)


DEF = """
spack:
  specs:
  - r@4.5.1
  view: true
"""
with open(PROJECT_DIR / "spack.yaml", "w") as f:
    f.write(DEF)

show_spython(
    spython_exec(
        """
        . /opt/spack/share/spack/setup-env.sh && 
        cd /work &&
        spack env activate --create -d . &&
        spack env st
        """,
        writable=True,
        bind_project=True
    )
)

show_spython(
    spython_exec(
        """
        . /opt/spack/share/spack/setup-env.sh && 
        cd /work &&
        spack env activate -d . &&
        spack concretize &&
        spack install
        """,
        writable=True,
        bind_project=True
    )
)


show_spython(spython_exec("""
export SPACK_DISABLE_LOCAL_CONFIG=true
export SPACK_USER_CONFIG_PATH=/tmp/spack-user-config
export SPACK_USER_CACHE_PATH=/tmp/spack-user-cache
export SPACK_MISC_CACHE_PATH=/tmp/spack-misc-cache

rm -rf /tmp/spack-user-config /tmp/spack-user-cache /tmp/spack-misc-cache
mkdir -p /tmp/spack-user-config /tmp/spack-user-cache /tmp/spack-misc-cache

. /opt/spack/share/spack/setup-env.sh

spack config blame repos || true
spack config blame packages || true
spack compiler list || true
"""))


show_spython(spython_exec("""
export SPACK_DISABLE_LOCAL_CONFIG=true
export SPACK_USER_CONFIG_PATH=/tmp/spack-user-config
export SPACK_USER_CACHE_PATH=/tmp/spack-user-cache
export SPACK_MISC_CACHE_PATH=/tmp/spack-misc-cache

mkdir -p /tmp/spack-user-config /tmp/spack-user-cache /tmp/spack-misc-cache

. /opt/spack/share/spack/setup-env.sh
cd /work
spack env activate -d . &&
spack concretize &&
spack install --fail-fast -j8
""", writable=True, bind_project=True)
)


show_spython(spython_exec("""
export SPACK_DISABLE_LOCAL_CONFIG=true

. /opt/spack/share/spack/setup-env.sh
cd /work
spack env activate -d .

spack concretize --force
spack install --deprecated --fail-fast -j8
""", writable=True, bind_project=True))


Client.build(
    image=str(TMP_SANDBOX),
    recipe=BASE_IMAGE,
    options=["--fakeroot", "--sandbox", "--fix-perms", "--force"],
    sudo=False,
)


show_spython(
    spython_exec("""
export SPACK_DISABLE_LOCAL_CONFIG=true
. /opt/spack/share/spack/setup-env.sh
cd /work
spack env activate -d . &&

""", writable=True, bind_project=True
    )
)


DEF = """
spack:
  specs:
  - r@4.5.1
  view: true
"""
with open(PROJECT_DIR / "spack.yaml", "w") as f:
    f.write(DEF)


import submitit

SUBMITIT_DIR = RUNTIME_DIR / "submitit"
SUBMITIT_DIR.mkdir(parents=True, exist_ok=True)

n_cpus = 8

executor = submitit.AutoExecutor(folder=str(SUBMITIT_DIR / "%j"))

executor.update_parameters(
    timeout_min=360,
    slurm_partition="hsph",
    mem_gb=32.0,
    cpus_per_task=n_cpus,
)


job = executor.submit(spython_exec, """
export SPACK_DISABLE_LOCAL_CONFIG=true
export SPACK_USER_CONFIG_PATH=/tmp/spack-user-config
export SPACK_USER_CACHE_PATH=/tmp/spack-user-cache
export SPACK_MISC_CACHE_PATH=/tmp/spack-misc-cache

mkdir -p /tmp/spack-user-config /tmp/spack-user-cache /tmp/spack-misc-cache

. /opt/spack/share/spack/setup-env.sh
cd /work
spack env activate -d . &&
spack install --fail-fast -j8
""", writable=True, bind_project=True)

job.job_id


show_spython(job.result())
