# RSE Workbench

**Status:** experimental / work in progress  
**Audience:** potential coauthors, research software engineers, data managers, lab data scientists, and collaborators interested in reproducible scientific computing on shared infrastructure.

RSE Workbench is the first prototype of a **Quarto Manual**: a cloneable, executable manual for assembling reproducible research computing projects one validated step at a time.

A Quarto Manual is not a passive tutorial and not a rigid command-line wrapper. It is closer to a LEGO or IKEA instruction booklet for research computing: each page guides the user through one bounded assembly step, produces concrete project artifacts, and ends with a functional test that checks whether the external project state matches the expected state.

The current RSE Workbench manual focuses on reproducible data science environments for Harvard research computing contexts, especially projects that combine Quarto, Python, R, Spack-managed system dependencies, containers, Slurm, and project-specific data conventions.

This repository is still unstable. Names, folders, extension behavior, and CLI commands may change as the prototype matures.

---

## Why this exists

Research software engineers often inherit or support projects where critical setup assumptions are implicit:

- Where does the project live?
- Which files are project-owned?
- Which data are raw, interim, or processed?
- Which dependencies are system-level versus language-level?
- Which steps must happen before others?
- Which runtime assumptions come from the HPC cluster?
- How do we know the environment is ready?
- How do we hand the project off to another researcher or RSE?

A README can explain setup commands, and a CLI can automate a stable workflow. Both are useful. But many research projects sit between those extremes.

A README works well when setup is short, linear, stable, and mostly copy-pasteable. A CLI works well when the workflow is predictable enough for a developer to encode the right defaults. RSE Workbench targets the harder middle case: setup procedures where order matters, later steps depend on earlier artifacts, users need to edit project-specific variables, files are generated along the way, and success needs to be verified.

The goal is not to replace documentation, package managers, containers, workflow engines, or tests. The goal is to compose them into a guided, editable project assembly process.

---

## The core idea

A Quarto Manual treats project setup as **notebook-wrapped, test-driven assembly**.

Each manual page has two jobs:

1. Explain and execute one project assembly step.
2. Provide or generate a corresponding functional test.

For example:

```text
pages/01_project_contract.qmd
tests/test_01_project_contract.py
```

The page is the human-facing instruction.  
The test is the comparison against the expected result.

Progress is not recorded in a custom state file. Instead, progress is inferred from the assembled project state:

- files
- directories
- package manifests
- lockfiles
- generated scripts
- container images
- rendered outputs
- Slurm logs
- successful commands
- pipeline metadata

This means the manual does **not** implement its own progress database, checkpoint tracker, or workflow engine. Existing tools remain responsible for their own layers.

---

## Design principles

### 1. The manual does not own progress

The project directory is the source of truth. A step is complete when the expected evidence exists and the corresponding tests pass.

### 2. Use existing tools

RSE Workbench is intentionally built around existing tools rather than replacing them:

- **Quarto** provides executable notebooks, books, websites, and project extensions.
- **Pandoc/Lua filters** provide structured access to Quarto document blocks.
- **pytest** or **testthat** provides functional inspections.
- **uv**, `pyproject.toml`, `renv`, `rv`, or other package managers handle language environments.
- **Spack** handles system dependencies where appropriate.
- **Singularity/Apptainer** or site runtimes provide isolation.
- **Slurm** handles scheduled execution on HPC.
- **Make**, `targets`, Snakemake, or other workflow engines may own computational DAGs when needed.

Quarto custom project types are intended for tailoring projects to a particular purpose, including organization-level standards for documentation or analysis. Quarto filters operate on the Pandoc abstract syntax tree between parsing and output, which makes them a natural fit for custom manual blocks and export behavior. ([Quarto](https://quarto.org/docs/extensions/project-types?utm_source=chatgpt.com))

### 3. A manual is different from a README

A README explains a procedure.  
A Quarto Manual helps the user execute, modify, and verify that procedure repeatedly in real project directories.

If the build has four pieces, a README may be enough. If the build has hundreds of order-dependent pieces, an instruction booklet becomes the better medium.

### 4. A manual is different from a wrapper

A wrapper hides a workflow behind a command. That is useful when the workflow is stable. But research environments often vary by dataset, cluster, package stack, security context, data-sharing requirement, and scientific question.

A Quarto Manual keeps the process visible and editable while still producing concrete files and tests.

### 5. The manual is allowed to teach by doing

Many users do not need more prose. They need a structured way to work through a procedure without holding every dependency, convention, and order constraint in memory.

---

## Current scope

The first manual type is **RSE Workbench**.

Its initial use case is reproducible computing environments for climate and public health data science on shared HPC infrastructure.

The current prototype is designed around:

- project contracts
- project-owned files
- data/code/notebook organization
- R and Python analysis code
- Quarto notebooks and reports
- Spack-managed system dependencies
- language-level package management
- container/runtime isolation
- activation and dependency-check scripts
- Slurm launch support
- pytest-based project inspections

Future manuals could target other recurring workflows, such as:

- a lab’s standard data analysis pipeline
- a machine-learning workflow
- a geospatial processing workflow
- a LEGO/warehouse analysis workflow
- an end-to-end data cleaning, modeling, and deployment workflow

---

## Architecture

At a high level:

```text
RSE Workbench manual repository
  ├── templates/
  │   └── rse_workbench/
  │       ├── pages/
  │       └── manual.yml
  │
  ├── projects/
  │   └── myproj/
  │       ├── pages/
  │       ├── src/
  │       ├── tests/
  │       ├── slurm/
  │       ├── data/
  │       └── manual.yml
  │
  ├── src/
  │   └── rse_workbench/
  │
  ├── tests/
  │
  └── _extensions/
      └── quarto-manual/
```

The intended workflow is:

```text
clone manual
  -> create project from template
  -> edit manual pages
  -> export source/tests/scripts/configs
  -> run page-level tests
  -> render manual book
  -> run full project test suite
```

---

## Custom manual blocks

RSE Workbench uses custom Quarto/Pandoc fenced Divs to distinguish different kinds of content.

Example:

````markdown
::: {.manual-project-source file="src/{{ project_package }}/contract.py"}
```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectContract:
    project_name: str
    project_dir: Path
```
:::
````

The Div tells the manual where the block should go.  
The inner code block contains the payload.

Planned block classes include:

```text
.manual-lib-source       exports reusable manual-library code
.manual-project-source   exports project-specific source code
.manual-project-test     exports pytest/testthat tests
.manual-project-script   exports shell, Slurm, or helper scripts
.manual-project-config   exports YAML/TOML/config files
.manual-run              rendered/executed in the page, not exported
.manual-explain          explanatory only, not exported
```

The export system should be implemented through Quarto/Pandoc machinery, not a hand-written QMD parser. This follows the same spirit as existing Quarto extensions such as code-extraction and code-filtering tools: let Quarto parse Quarto, then operate on the structured document representation.

---

## Intended user workflow

Eventually, a user should be able to run:

```bash
cd /path/to/frontier/town/$USER

git clone <repo-url> rse-workbench
cd rse-workbench

uv sync
uv run rse-manual new myproj --template rse_workbench

cd projects/myproj

uv run rse-manual inflate .
quarto preview
uv run pytest .
```

A project then contains ordered pages such as:

```text
pages/00_before_you_start.qmd
pages/01_project_contract.qmd
pages/02_platform_recipe.qmd
pages/03_system_dependencies.qmd
pages/04_language_packages.qmd
pages/05_activation.qmd
pages/06_build_launch.qmd
pages/07_final_inspection.qmd
```

Each page has a paired test:

```text
tests/test_00_before_you_start.py
tests/test_01_project_contract.py
tests/test_02_platform_recipe.py
tests/test_03_system_dependencies.py
tests/test_04_language_packages.py
tests/test_05_activation.py
tests/test_06_build_launch.py
tests/test_07_final_inspection.py
```

The user can work page by page, or run the full test suite:

```bash
uv run pytest .
```

pytest is a good fit for the Python prototype because its fixture system lets tests request shared setup objects by name, which is useful for project contracts and environment checks. ([Pytest Documentation](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html?utm_source=chatgpt.com))

---

## What `inflate` means

The planned `inflate` step exports implementation files from manual pages.

For example, a manual page may contain:

- a `.manual-project-source` block that writes `src/myproj/contract.py`
- a `.manual-project-test` block that writes `tests/test_01_project_contract.py`
- a `.manual-project-script` block that writes `slurm/build/build_platform.sbatch`
- a `.manual-project-config` block that writes `spack.yaml`

This is inspired by the idea that a notebook can be the first source of truth for code, tests, examples, and documentation. The generated files are conventional files that existing tools can use.

Generated files should include a header such as:

```python
# Generated by rse-manual.
# Source: pages/01_project_contract.qmd
# Do not edit directly unless you intend to stop using the manual as source of truth.
```

The overwrite policy should be conservative:

```text
If target does not exist:
  write file

If target exists and contains generated header:
  overwrite file

If target exists and lacks generated header:
  fail with a clear error

If --force is passed:
  overwrite anyway

If --check is passed:
  report planned changes without writing
```

---

## What this is not

RSE Workbench is not intended to be:

- a replacement for a README
- a replacement for package documentation
- a replacement for uv, conda, renv, Spack, or other environment managers
- a replacement for Make, targets, Snakemake, Nextflow, or other workflow engines
- a replacement for Slurm or HPC site policies
- a general-purpose GUI
- a promise that complex environments will “just work”

Instead, it is an attempt to make complex setup more explicit, inspectable, teachable, and repeatable.

---

## Why not just a README?

A README is the right baseline comparison.

READMEs are effective when the task is short, linear, stable over time and context, and mostly copy-pasteable. Once a procedure leaves those confines, even a good README has diminishing returns.

The problem RSE Workbench targets is the next level of complexity: setup procedures where order matters, later steps depend on earlier artifacts, users need to edit project-specific variables, files are generated along the way, and success needs to be verified.

A README explains a procedure.  
A Quarto Manual helps users execute, modify, and verify that procedure repeatedly in real project directories.

---

## Why not just a CLI?

A CLI is useful when a developer can safely encode the right defaults.

But research projects often need local judgment:

- Which data source is being staged?
- Which packages are project-specific?
- Which dependencies belong in Spack versus R or Python?
- Which runtime should be used?
- Which Slurm resources are appropriate?
- Which artifacts are publishable?
- Which setup assumptions are site-specific?

A Quarto Manual avoids hiding these choices. It gives users a structured, editable path through them.

---

## Relationship to AI-assisted setup

AI tools can help draft environment files, scripts, tests, and explanations. But AI-generated setup can also produce plausible fragments without a reviewed order of operations.

RSE Workbench is intended to provide a place where AI-assisted work can be made explicit:

- generated suggestions can be placed into manual pages
- assumptions can be reviewed
- scripts and config files can be exported
- tests can verify the resulting project state
- the final workflow remains inspectable by humans

The goal is not to hide engineering judgment behind AI, but to make the judgment traceable.

---

## Development status

This repository is a work in progress.

Current priorities:

- define the Quarto Manual architecture
- stabilize the RSE Workbench manual type
- implement a minimal `rse-manual` CLI
- support `new`, `inflate`, `test`, `render`, and `preview`
- implement custom manual blocks with Quarto/Pandoc filters
- migrate existing RSE Workbench notebooks into page/test pairs
- produce one working project example
- document limitations clearly

Expected instability:

- folder names may change
- CLI names may change
- Quarto extension names may change
- block class names may change
- Python package structure may change
- extraction behavior may change
- examples may be incomplete

Please treat this repository as a prototype, not stable infrastructure.

---

## Open design questions

We are actively seeking feedback on:

1. What is the smallest useful project contract?
2. Which setup artifacts should be generated from manual pages?
3. Which artifacts should remain hand-authored?
4. Should export happen during `quarto render`, or only through an explicit `inflate` command?
5. How should R/testthat and Python/pytest manuals share conventions?
6. How much site-specific HPC logic should live in the manual?
7. How should Quarto Manuals interact with DataLad, stagecoach, LEGO, or future data registries?
8. How should AI-assisted edits be disclosed or reviewed?
9. What evidence would show that manuals improve onboarding or reproducibility?

---

## Contributing

At this stage, the best way to contribute is through design feedback, example workflows, and concrete failure cases.

Useful contributions include:

- comments on the architecture
- suggestions for clearer terminology
- examples of painful project setup workflows
- candidate manual pages
- tests that capture expected project state
- feedback on what should be site-specific versus general
- examples from R, Python, geospatial, machine learning, or HPC workflows

Because the project is unstable, please coordinate before making large implementation changes.

---

## Working thesis

RSE Workbench explores the idea that some research software workflows are too complex for prose-only documentation and too variable for rigid automation.

A Quarto Manual provides a middle path:

> clone the manual, enter the project, follow the pages, generate the artifacts, run the tests, and leave behind a reproducible workspace.
