# Solution Design: Cross-Platform Python Project Scaffolder

## 1. Purpose

Build a cross-platform Python project scaffolding CLI that creates standardized Python projects using `uv`.

The tool must support:

- macOS
- Windows
- Python application projects
- Python library projects
- Libraries that can be built and published to PyPI

The scaffolder itself should be implemented as a Python CLI so that project-generation logic is shared across operating systems.

OS-specific scripts should only be used for bootstrapping when needed.

---

## 2. High-Level Goal

A developer should be able to run a command from a terminal and create a fully configured Python project with:

- `uv`
- managed Python version
- virtual environment
- dependency synchronization
- `ruff`
- `ty`
- `prek`
- standard linting and type-checking configuration
- pre-commit hooks
- optional Makefile support
- README
- application or library project layout
- PyPI-ready library build configuration

Example target experience:

```text
$ py-scaffold new

Python Project Scaffolder

Project name: payment-utils

Project type:
1. application
2. library

Select project type [1]: 2

Python version [3.12]: 3.12

Creating project...

✓ uv detected
✓ Python 3.12 available
✓ Project initialized
✓ Virtual environment created
✓ Dependencies synchronized
✓ Ruff configured
✓ ty configured
✓ prek configured
✓ Git hooks installed
✓ Makefile generated
✓ README generated
✓ Project validation passed

Project created successfully:
./payment-utils
```

Non-interactive usage must also be supported:

```bash
py-scaffold new payment-utils --type library --python 3.12
```

---

# 3. Design Principles

The implementation should follow these principles.

## 3.1 Cross-platform core

Do not duplicate project-generation logic in Bash and PowerShell.

Use:

```text
setup.sh      -> bootstrap only
setup.ps1     -> bootstrap only

Python CLI    -> all scaffolding logic
```

The Python implementation must use cross-platform APIs such as:

- `pathlib`
- `subprocess`
- `shutil`
- `sys`
- `platform`

Avoid OS-specific shell commands unless absolutely necessary.

---

## 3.2 uv-first

Use `uv` as the primary tool for:

- Python discovery
- Python installation
- project initialization
- virtual environment creation
- dependency management
- dependency synchronization
- running development tools
- building libraries
- publishing libraries

Avoid introducing `pip`, `virtualenv`, Poetry, Pipenv, or Conda into the generated workflow.

---

## 3.3 Safe bootstrap behavior

The scaffolder must not silently install `uv`.

If `uv` is missing:

1. Detect the operating system.
2. Print the official install command.
3. Ask the user to install `uv`.
4. Exit with a non-zero exit code.

Example macOS guidance:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Example Windows guidance:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

The user should rerun the scaffolder after installing `uv`.

---

## 3.4 Let uv manage Python

Do not implement separate Python installation logic for Windows and macOS.

Expected flow:

```text
Requested Python version
        |
        v
uv python find <version>
        |
   +----+----+
   |         |
 found     missing
   |         |
   |    uv python install <version>
   |         |
   +----+----+
        |
        v
Continue
```

The default Python version should initially be:

```text
3.12
```

It must be configurable by CLI argument.

Example:

```bash
py-scaffold new my-project --python 3.13
```

---

# 4. Scope

## 4.1 In scope

The first version must support:

- macOS
- Windows
- interactive CLI
- non-interactive CLI
- application projects
- library projects
- project-name validation
- configurable Python version
- uv initialization
- virtual environment setup
- dependency synchronization
- developer dependencies
- Ruff configuration
- ty configuration
- prek configuration
- Git hook installation
- Makefile generation
- README generation
- initial project validation
- library build using `uv build`
- library publishing documentation for PyPI

---

## 4.2 Out of scope for V1

Do not implement these in the first version:

- Django template
- FastAPI template
- data engineering template
- Docker
- CI/CD pipeline generation
- GitHub repository creation
- PyPI credential creation
- automatic PyPI publishing during scaffolding
- Nexus publishing
- project upgrades/migrations
- plugin system
- remote template repositories
- organization-specific package indexes

These can be added later.

---

# 5. Architecture

Recommended architecture:

```text
                    User Terminal
                         |
                         v
                  py-scaffold CLI
                         |
        +----------------+----------------+
        |                                 |
 Environment checks                 User configuration
        |                                 |
        +----------------+----------------+
                         |
                         v
                  Project Generator
                         |
       +-----------------+--------------------+
       |                 |                    |
      uv              Tooling              Templates
       |                 |                    |
 init/python       Ruff / ty / prek       README
 venv/sync         Git hooks              Makefile
 dependencies                            pyproject
                         |
                         v
                   Validation
                         |
               +---------+---------+
               |                   |
          Application            Library
                                   |
                                uv build
                                   |
                                   v
                                  PyPI
```

---

# 6. Proposed Repository Structure

```text
python-project-scaffolder/
|
├── pyproject.toml
├── README.md
├── LICENSE
|
├── scripts/
│   ├── setup.sh
│   └── setup.ps1
|
├── src/
│   └── py_scaffold/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── constants.py
│       ├── errors.py
│       ├── environment.py
│       ├── runner.py
│       ├── validation.py
│       ├── generator.py
│       │
│       ├── steps/
│       │   ├── python_setup.py
│       │   ├── project_init.py
│       │   ├── dependencies.py
│       │   ├── quality.py
│       │   ├── hooks.py
│       │   ├── makefile.py
│       │   └── readme.py
│       │
│       ├── profiles/
│       │   ├── base.py
│       │   ├── application.py
│       │   └── library.py
│       │
│       └── templates/
│           ├── README.application.md
│           ├── README.library.md
│           ├── Makefile
│           └── prek.toml
|
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

# 7. CLI Design

The executable command should be:

```bash
py-scaffold
```

Primary command:

```bash
py-scaffold new
```

Supported syntax:

```bash
py-scaffold new [PROJECT_NAME]
```

Options:

```text
--type application|library
--python <version>
--path <destination>
--no-make
--no-hooks
--non-interactive
--force
```

Example:

```bash
py-scaffold new payment-service \
    --type application \
    --python 3.12
```

Library example:

```bash
py-scaffold new company-utils \
    --type library \
    --python 3.12
```

Future commands may include:

```text
py-scaffold doctor
py-scaffold version
py-scaffold upgrade
```

Only `new` is required for V1.

---

# 8. Interactive Input Flow

If required values are not passed as CLI arguments, prompt the user.

Required input:

```text
Project name
Project type
Python version
```

Example:

```text
Project name: payment-service

Project type:
1. application
2. library

Select project type [1]: 1

Python version [3.12]:
```

Defaults:

```text
project type   = application
python version = 3.12
destination    = current directory
```

---

# 9. Project Name Validation

Project names must be validated before creating files.

Accept examples:

```text
payment-service
payment_service
paymentutils
company-data-utils
```

Reject:

```text
payment service
/payment
../payment
payment/service
.
..
```

The tool should derive:

```text
Distribution name:
payment-utils

Python package name:
payment_utils
```

For libraries, the Python import package must use a valid Python identifier.

Example:

```text
project name:
payment-utils

package:
payment_utils
```

---

# 10. Environment Detection

Create an `EnvironmentChecker`.

Responsibilities:

```text
check_uv()
check_git()
check_make()
check_python()
get_os()
```

Example model:

```python
@dataclass
class EnvironmentStatus:
    os: str
    uv_available: bool
    uv_version: str | None
    git_available: bool
    make_available: bool
```

---

# 11. uv Detection

Use:

```python
shutil.which("uv")
```

If not found:

```text
ERROR: uv is not installed.

Install uv first:

macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

After installation, rerun this command.
```

Exit code:

```text
1
```

---

# 12. Python Version Handling

Do not rely only on:

```bash
python --version
```

Use uv.

First:

```bash
uv python find 3.12
```

If unavailable:

```bash
uv python install 3.12
```

Then use the requested Python version for project setup.

The implementation must encapsulate this behavior in:

```python
PythonSetup
```

Pseudo-flow:

```python
def ensure_python(version):
    if uv_python_exists(version):
        return

    install_python(version)
```

---

# 13. Project Creation Flow

The generator should run steps in a predictable pipeline.

```text
1. Validate input
2. Validate target directory
3. Check uv
4. Check Git
5. Check Make
6. Ensure requested Python
7. Initialize project
8. Create virtual environment
9. Sync environment
10. Install dev dependencies
11. Configure Ruff
12. Configure ty
13. Configure prek
14. Install Git hooks
15. Generate Makefile
16. Generate README
17. Validate project
18. Show completion summary
```

Each step should be independently testable.

---

# 14. uv Project Initialization

## Application

Use:

```bash
uv init --app <project-name>
```

If implementation requirements make explicit package creation preferable, the agent may use equivalent supported `uv init` options while preserving the intended application structure.

Expected example:

```text
payment-service/
├── pyproject.toml
├── README.md
├── .python-version
└── src/
    └── ...
```

The generated structure must be validated against the version of uv used by the implementation.

---

## Library

Use:

```bash
uv init --lib <project-name>
```

Expected conceptual structure:

```text
payment-utils/
├── pyproject.toml
├── README.md
├── .python-version
├── src/
│   └── payment_utils/
│       └── __init__.py
└── ...
```

The generated library must be buildable with:

```bash
uv build
```

---

# 15. Virtual Environment

Run:

```bash
uv venv
```

Expected environment:

```text
.venv/
```

Then:

```bash
uv sync
```

Although uv may automatically create the virtual environment during synchronization, keep `uv venv` as an explicit scaffolding step for clarity.

---

# 16. Development Dependencies

Install:

```bash
uv add --dev ruff ty prek
```

Expected `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "prek",
    "ruff",
    "ty",
]
```

Exact ordering does not matter.

Runtime dependencies must not include these tools.

---

# 17. Ruff Configuration

Ruff configuration should live in:

```text
pyproject.toml
```

Initial recommended baseline:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "B",
    "UP",
    "SIM",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

The `target-version` must match the selected Python version where practical.

Do not enable an excessively strict ruleset in V1.

The goal is:

- syntax/error detection
- imports
- common bug patterns
- upgrade suggestions
- useful simplifications
- consistent formatting

---

# 18. ty Configuration

ty configuration should also live in:

```text
pyproject.toml
```

Use:

```toml
[tool.ty]
```

or the appropriate current supported configuration structure.

The implementation agent must verify the current `ty` configuration schema before implementation.

V1 should prefer sensible defaults rather than a large custom rule list.

Primary validation command:

```bash
uv run ty check
```

---

# 19. prek Configuration

Create:

```text
prek.toml
```

Prefer local hooks that execute the project-managed versions of Ruff and ty.

Conceptual configuration:

```toml
[[repos]]
repo = "local"

[[repos.hooks]]
id = "ruff-format"
name = "ruff format"
entry = "uv run ruff format"
language = "system"

[[repos.hooks]]
id = "ruff-check"
name = "ruff check"
entry = "uv run ruff check --fix"
language = "system"

[[repos.hooks]]
id = "ty-check"
name = "ty check"
entry = "uv run ty check"
language = "system"
pass_filenames = false
```

The implementation agent must verify the current `prek.toml` schema before finalizing this file.

Install hooks using:

```bash
uv run prek install
```

Run all hooks using:

```bash
uv run prek run --all-files
```

---

# 20. Make Support

Make is a convenience feature.

It must not be required for project functionality.

Check using:

```python
shutil.which("make")
```

If Make exists:

```text
✓ Make detected
```

If Make does not exist:

```text
⚠ Make is not installed.
The Makefile will still be generated.
You can run the underlying uv commands directly.
```

Do not silently install Make.

The project must work without Make.

---

# 21. Generated Makefile

Recommended Makefile:

```makefile
.PHONY: install sync format lint lint-fix typecheck check hooks setup build clean

install:
	uv sync

sync:
	uv sync

format:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

typecheck:
	uv run ty check

check: lint typecheck

hooks:
	uv run prek run --all-files

setup:
	uv sync
	uv run prek install

build:
	uv build

clean:
	rm -rf dist build .ruff_cache .venv
```

Important:

The `clean` command above is Unix-oriented.

Because Windows support is required, V1 should choose one of these strategies:

### Preferred

Keep Makefile commands platform-independent where possible and avoid destructive cleanup commands requiring shell-specific syntax.

For example:

```makefile
clean:
	uv run python scripts/clean.py
```

Or omit `clean` in V1.

Recommended V1 decision:

```text
Do not include `clean` until a cross-platform implementation exists.
```

---

# 22. README Generation

Every generated project must contain a README.

Application README should include:

```text
Project name
Description placeholder
Requirements
Setup
Run
Development commands
Linting
Formatting
Type checking
Pre-commit hooks
```

Example commands:

```bash
uv sync
uv run ruff check .
uv run ruff format .
uv run ty check
uv run prek run --all-files
```

---

## Library README

Additionally include:

```text
Build
Publishing
Installation
```

Build:

```bash
uv build
```

Generated artifacts:

```text
dist/
```

Publish to PyPI:

```bash
uv publish
```

Do not publish automatically.

The README should explain that PyPI authentication must be configured separately.

---

# 23. PyPI Support

Library projects must be prepared for PyPI.

Required validation:

```bash
uv build
```

Expected artifacts:

```text
dist/<package>.whl
dist/<package>.tar.gz
```

Publishing:

```bash
uv publish
```

The scaffolder itself must never ask for or store PyPI credentials during project creation.

Authentication is outside scaffolding scope.

---

# 24. Command Runner

Create a common subprocess abstraction.

Example:

```python
class CommandRunner:
    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        ...
```

Do not execute commands using:

```python
shell=True
```

unless there is a documented and unavoidable reason.

Preferred:

```python
subprocess.run(
    ["uv", "sync"],
    cwd=project_path,
    check=True,
)
```

This is safer and more portable.

---

# 25. Configuration Model

Recommended model:

```python
@dataclass(frozen=True)
class ProjectConfig:
    name: str
    package_name: str
    project_type: ProjectType
    python_version: str
    destination: Path
    create_makefile: bool = True
    install_hooks: bool = True
```

Project type:

```python
class ProjectType(str, Enum):
    APPLICATION = "application"
    LIBRARY = "library"
```

---

# 26. Profiles

Avoid embedding all behavior directly in the CLI.

Use project profiles.

Conceptual interface:

```python
class ProjectProfile(Protocol):

    def init_command(
        self,
        config: ProjectConfig,
    ) -> list[str]:
        ...

    def generate_files(
        self,
        config: ProjectConfig,
    ) -> None:
        ...
```

Implement:

```text
ApplicationProfile
LibraryProfile
```

This makes future profiles possible:

```text
FastAPIProfile
CLIProfile
DataEngineeringProfile
AutomationProfile
```

without restructuring the CLI.

---

# 27. Error Handling

Use clear domain-specific errors.

Recommended:

```text
ScaffoldError
├── MissingUvError
├── InvalidProjectNameError
├── TargetDirectoryExistsError
├── PythonInstallationError
├── ProjectInitializationError
├── DependencyInstallationError
├── HookInstallationError
└── ValidationError
```

User-facing failures should be concise.

Example:

```text
✗ Unable to install Python 3.12 using uv.

Command:
uv python install 3.12

Run the command manually for more details.
```

Avoid dumping Python stack traces during normal CLI usage.

Provide an optional future:

```text
--verbose
```

for debugging.

---

# 28. Existing Directory Handling

Default behavior:

If the target directory already exists and is not empty:

```text
ERROR: Target directory already exists and is not empty:
./payment-service
```

Do not overwrite files.

Optional:

```bash
--force
```

may be implemented, but even with force the implementation must not blindly remove arbitrary directories.

Safe behavior is more important than convenience.

---

# 29. Failure and Rollback Strategy

Project creation is a multi-step process.

If initialization fails after the scaffolder created a brand-new directory, the CLI should report exactly where it failed.

V1 does not need full transactional rollback.

However:

- never delete a pre-existing directory
- never overwrite unrelated files
- clearly report partial project creation
- return a non-zero exit code

Example:

```text
Project creation failed during dependency installation.

Partial project remains at:
./payment-service

Fix the reported issue and rerun the required command.
```

---

# 30. Git

Check if Git is available:

```python
shutil.which("git")
```

Git should be recommended but not necessarily mandatory unless `prek install` requires a Git repository for the chosen workflow.

If a Git repository is required for hook installation:

```text
if git available:
    initialize or use repo
    install hooks
else:
    skip hooks with warning
```

Do not automatically install Git.

---

# 31. Bootstrap Scripts

## macOS

`scripts/setup.sh`

Responsibilities:

```text
1. Check uv
2. Print uv installation command if missing
3. Exit when missing
4. Start scaffolder when available
```

Do not put project-generation logic here.

---

## Windows

`scripts/setup.ps1`

Same responsibilities.

The two scripts should have equivalent behavior.

---

# 32. Logging and Terminal Output

Use concise status messages.

Example:

```text
Checking environment...

✓ uv 0.x.x
✓ Git available
⚠ Make not found
✓ Python 3.12 available

Creating project...

✓ Project initialized
✓ Development dependencies installed
✓ Ruff configured
✓ ty configured
✓ prek configured
✓ Hooks installed

Project ready.
```

Suggested symbols:

```text
✓ success
⚠ warning
✗ error
```

Fallback to plain text if terminal encoding becomes an issue.

---

# 33. Validation Phase

After scaffolding, automatically run:

```bash
uv sync
uv run ruff check .
uv run ty check
```

Optionally run:

```bash
uv run prek run --all-files
```

For a library:

```bash
uv build
```

The generated project is considered successful only if required validation passes.

---

# 34. Generated Application Acceptance Criteria

Given:

```bash
py-scaffold new demo-app --type application --python 3.12
```

The result must:

- create `demo-app`
- contain `pyproject.toml`
- contain a README
- use Python 3.12
- contain `.venv` after setup
- contain `uv.lock`
- contain Ruff as a dev dependency
- contain ty as a dev dependency
- contain prek as a dev dependency
- contain Ruff configuration
- contain ty configuration
- contain `prek.toml`
- contain Makefile unless disabled
- successfully run `uv sync`
- successfully run `uv run ruff check .`
- successfully run `uv run ty check`

---

# 35. Generated Library Acceptance Criteria

Given:

```bash
py-scaffold new demo-utils --type library --python 3.12
```

The result must satisfy all common criteria plus:

- have an importable Python package
- use a valid package/module name
- use a `src` layout where supported by uv
- successfully run:

```bash
uv build
```

- generate both wheel and source distribution where supported
- include README instructions for:

```bash
uv build
uv publish
```

- contain no Nexus-specific configuration

---

# 36. Scaffolder Package Configuration

The scaffolder itself should expose:

```toml
[project.scripts]
py-scaffold = "py_scaffold.cli:main"
```

It should itself be installable using uv.

Development example:

```bash
uv sync
uv run py-scaffold new example
```

Once released publicly:

```bash
uv tool install <package-name>
```

or:

```bash
uvx <package-name>
```

The exact public package name should be selected separately after checking PyPI availability.

Do not hardcode an assumed available PyPI package name in implementation.

---

# 37. Recommended CLI Library

V1 may be built using either:

```text
argparse
```

or a third-party CLI library.

Preferred V1 approach:

```text
argparse
```

Reason:

- built into Python
- no runtime dependency
- sufficient for the initial command surface

If the CLI grows significantly, migrating to Typer is acceptable later.

---

# 38. Template Strategy

Templates should be packaged with the scaffolder.

Use Python package resources rather than assuming templates exist relative to the current working directory.

Recommended API:

```python
import importlib.resources
```

Avoid:

```python
Path(__file__).parent.parent / "../../templates"
```

when a package-resource approach can be used.

---

# 39. Idempotency

Environment checks must be idempotent.

Running the scaffolder again must never accidentally modify an existing project without explicit intent.

Commands such as:

```text
uv python install
uv sync
```

may safely be rerun where appropriate.

Project creation itself should fail safely when the destination already exists.

---

# 40. Security Considerations

The implementation must:

- avoid `shell=True`
- validate project names
- prevent path traversal
- never store PyPI tokens
- never silently execute remote installer scripts
- never automatically install OS package managers
- never delete existing directories
- never commit credentials
- avoid logging secrets

---

# 41. Testing Strategy

## Unit tests

Test:

```text
project-name validation
package-name normalization
OS detection
uv detection
Make detection
Git detection
Python-version parsing
command generation
profile selection
configuration generation
```

Mock subprocess calls.

---

## Integration tests

Run scaffolding against temporary directories.

Test:

```text
application project
library project
custom Python version
existing directory
missing Make
hooks disabled
Makefile disabled
```

Where CI environment permits, execute actual:

```bash
uv sync
uv run ruff check .
uv run ty check
uv build
```

---

# 42. Recommended Implementation Order

The implementation agent should build in this order.

## Phase 1 — Core CLI

Implement:

```text
py-scaffold new
ProjectConfig
ProjectType
input parsing
project-name validation
```

---

## Phase 2 — Environment

Implement:

```text
uv detection
Git detection
Make detection
Python detection/install via uv
```

---

## Phase 3 — Project creation

Implement:

```text
application profile
library profile
uv init
uv venv
uv sync
```

---

## Phase 4 — Developer tooling

Implement:

```text
uv add --dev ruff ty prek
Ruff config
ty config
prek config
hook installation
```

---

## Phase 5 — Generated files

Implement:

```text
Makefile
README
```

---

## Phase 6 — Validation

Implement:

```text
ruff validation
ty validation
prek validation
library build validation
```

---

## Phase 7 — Tests

Implement:

```text
unit tests
integration tests
Windows verification
macOS verification
```

---

# 43. Target Execution Flow

Final expected orchestration:

```python
def create_project(config: ProjectConfig) -> None:

    validate_config(config)

    environment = inspect_environment()

    require_uv(environment)

    ensure_python(config.python_version)

    profile = get_profile(config.project_type)

    project_path = initialize_project(
        config=config,
        profile=profile,
    )

    create_virtual_environment(project_path)

    sync_dependencies(project_path)

    install_dev_dependencies(project_path)

    configure_ruff(project_path, config)

    configure_ty(project_path, config)

    configure_prek(project_path)

    if config.install_hooks:
        install_hooks(project_path)

    if config.create_makefile:
        generate_makefile(project_path)

    generate_readme(project_path, config)

    validate_generated_project(
        project_path,
        config,
    )

    print_summary(project_path)
```

The implementation does not need to use these exact function names, but it should preserve this separation of responsibilities.

---

# 44. Definition of Done

V1 is complete when:

1. The same Python CLI implementation runs on macOS and Windows.
2. `uv` is the only required Python environment/package-management tool.
3. Missing `uv` results in installation instructions rather than silent installation.
4. Python can be installed through uv when the requested version is absent.
5. Application projects can be created.
6. Library projects can be created.
7. Ruff is configured and working.
8. ty is configured and working.
9. prek hooks are configured and working.
10. Makefile is generated but Make is optional.
11. README is generated.
12. Generated application projects pass validation.
13. Generated library projects pass validation.
14. Generated library projects build successfully with `uv build`.
15. Library README documents publishing to PyPI with `uv publish`.
16. No Nexus configuration or publishing logic exists.
17. Unit and integration tests cover the primary flows.
18. Existing user directories/files cannot be destructively overwritten by default.

---

# 45. Future Enhancements

After V1, consider:

```text
py-scaffold doctor
py-scaffold upgrade
py-scaffold new --profile fastapi
py-scaffold new --profile cli
py-scaffold new --profile data-engineering
CI template generation
Docker support
GitHub Actions
license selection
pytest configuration
coverage configuration
semantic-release integration
PyPI trusted publishing setup
organization-specific profiles
remote/custom templates
```

Keep these out of V1 unless explicitly requested.

---

# 46. Final Architectural Decision

The implementation should follow this model:

```text
               macOS / Windows
                      |
                      v
                 uv bootstrap
                      |
                      v
               Python CLI Core
                      |
        +-------------+-------------+
        |                           |
   Environment                   Profiles
        |                           |
   uv / Python /               Application
   Git / Make                   Library
        |                           |
        +-------------+-------------+
                      |
                      v
               Project Generator
                      |
       +--------------+---------------+
       |              |               |
      uv          Quality tools      Files
                   Ruff
                   ty
                   prek
                      |
                      v
                 Validation
                      |
             +--------+--------+
             |                 |
        Application          Library
                                |
                             uv build
                                |
                                v
                               PyPI
```

This design should be treated as the source of truth for the initial implementation.
