#!/bin/bash
#SBATCH -p hsph
#SBATCH --mem=24g
#SBATCH --time=04:00:00
#SBATCH -c 4
#SBATCH --job-name=RSEWorkBench
# Logging
#SBATCH --output=/n/holylabs/LABS/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/slurm/launch/logs/launch_%j.out
#SBATCH --error=/n/holylabs/LABS/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/slurm/launch/logs/launch_%j.err

set -o errexit -o nounset -o pipefail

PROJECT_DIR="${PROJECT_DIR:-$SLURM_SUBMIT_DIR}"
TUNNEL_NAME="${TUNNEL_NAME:-$(basename "$PROJECT_DIR")-tunnel}"

cd "$PROJECT_DIR"

MY_SCRATCH=$(TMPDIR=/scratch mktemp -d)
echo "Scratch: $MY_SCRATCH"
echo "Project: $PROJECT_DIR"
echo "Tunnel: $TUNNEL_NAME"
echo "Host: $(hostname)"

module purge

echo "================= Tool SitRep ===================="
echo "=================================================="
echo "Date: $(date)"
echo "Host: $(hostname)"
echo "User: $(whoami)"
echo "SLURM_JOB_ID: ${SLURM_JOB_ID}"
echo "Working directory: $(pwd)"
echo "=================================================="
echo "Setting up workbench:"

source .venv/bin/activate
echo "Setting persistent/private VS Code auth/state..."
export VSCODE_CLI_DATA_DIR="${VSCODE_CLI_DATA_DIR:-$HOME/.vscode-cli-rse-workbench}"
mkdir -p "$VSCODE_CLI_DATA_DIR"
chmod 700 "$VSCODE_CLI_DATA_DIR"

echo "Setting node-local build workspace"
BUILD_ROOT="${BUILD_ROOT:-/tmp/$USER-rse-workbench-${SLURM_JOB_ID}}"
mkdir -p "$BUILD_ROOT"

echo "Setting Singularity temp/cache/state"
export TMPDIR="$BUILD_ROOT/tmp"
export SINGULARITY_TMPDIR="$BUILD_ROOT/singularity-tmp"
export SINGULARITY_CACHEDIR="$BUILD_ROOT/singularity-cache"

echo "Setting Apptainer-compatible names, harmless if using Singularity"
export APPTAINER_TMPDIR="$SINGULARITY_TMPDIR"
export APPTAINER_CACHEDIR="$SINGULARITY_CACHEDIR"

mkdir -p "$TMPDIR" "$SINGULARITY_TMPDIR" "$SINGULARITY_CACHEDIR"

echo "Creating dirs where interactive sandboxes should live"
export RSE_SANDBOX_ROOT="$BUILD_ROOT/sandboxes"
mkdir -p "$RSE_SANDBOX_ROOT"

echo "Setting where final images should be copied if desired"
export RSE_IMAGE_DIR="${RSE_IMAGE_DIR:-$PROJECT_DIR/.devcontainer/images}"
mkdir -p "$RSE_IMAGE_DIR"
echo "=================================================="

curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' \
  | tar -C "$BUILD_ROOT" -xzf -

"$BUILD_ROOT/code" tunnel \
  --accept-server-license-terms \
  --name "$TUNNEL_NAME"
