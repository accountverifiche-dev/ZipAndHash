# ZipAndHash (ZAH)

ZipAndHash (ZAH) is a safe, deterministic, and fully tested command-line utility designed to automate zipping, hashing, filtering, copying, and moving structured directory trees. It is intended for high‑integrity workflows such as archival processes, data handover pipelines, and automated batch-processing tasks.

All modules are covered by a complete unit-test suite with 100% coverage.

---

## Key Features

**Reliable directory processing**  
Zips each subdirectory of a source directory into individual archives placed in the destination directory.

**File filtering**  
Optional extension-based filtering (`--fzip`, `--fcpy`, `--fmv`) to restrict which files are included during zip/copy/move phases, plus an empty-archive filter (`--fmpt`) to avoid creating zip files for empty or fully filtered-out directories.

**Hash generation**  
Each generated ZIP file is hashed (default: `sha3_256`). All hashes are aggregated into a `hashes.txt` file, which itself is hashed to provide a final integrity checksum.

**Copy and move operations**  
After hashing, the tool can copy results (`--cpy`) or move the original data (`--mv`), with optional filtering.

**Safety mode**  
When operating in move mode, ZAH prompts the user unless `--unsafe` is specified.

**Single-instance lock**  
Ensures only one execution can run at a time through a filesystem lock mechanism.

**Structured logging**  
Console output includes colorized logs, and a log file (`ZAH.log`) is generated for full traceability.

**100% test coverage**  
All modules (`config`, `dir_operations`, `extensions`, `hash`, `zip`, `logger`, `single_instance`, `main`, and `__main__`) are covered by dedicated tests.

---

## Installation

The recommended way to install the tool is by using the provided helper scripts, which automatically create/activate a virtual environment and install the package:

- `install.bat` or `install_and_test.bat` on Windows
- `install.sh` or `install_and_test.sh` on Unix/Linux/macOS

`install_and_test` variants also install test dependencies and run the full pytest + coverage suite.

You can still install manually with `pip` if you prefer:

```bash
pip install .
```

### Editable installation (development mode)

```bash
pip install -e .
```

### Installing with test dependencies

If defined in `pyproject.toml`, you can install the project including optional `test` extras:

```bash
pip install .[test]
```

---

## Usage

The recommended way to run the tool is via the provided runner scripts, which activate the virtual environment and then invoke the CLI:

- `example_run.bat` (Windows)
- `example_run.sh` (Unix/Linux/macOS)

You can customize these scripts with your own `SRC`, `DST`, `CPY` and option flags.

You can also run ZAH directly from the command line.

Basic syntax:

```bash
zah <source_dir> <destination_dir> [options]
```

Or via Python:

```bash
python -m zah <source_dir> <destination_dir> [options]
```

### Common options

```
--sub            Place output inside a new subdirectory
--hash           Hashing algorithm (default: sha3_256)
--fzip           Filter files during zip
--fcpy           Filter files during copy
--fmv            Filter files during move
--fmpt           Skip creating zip files when the source directory is empty or all files are filtered out
--cpy <path>     Copy output into a secondary directory
--mv             Move source into destination after zipping
--unsafe         Disable safety confirmation
--debug          Enable detailed debug logging
```

### Example commands

**Simple zip + hash:**

```bash
zah data/ archives/
```

**Zip only selected file types:**

```bash
zah src/ dst/ --fzip
```

**Zip + copy filtered results:**

```bash
zah src/ dst/ --cpy backup/ --fzip --fcpy
```

**Full destructive move with manual confirmation:**

```bash
zah src/ dst/ --mv
```

**Unsafe mode (no confirmation):**

```bash
zah src/ dst/ --mv --unsafe
```

---

## Logging

ZAH writes:

- color-augmented logs to console
- a log file `ZAH.log` in the working directory

Enable debug logging with:

```bash
zah src dst --debug
```

---

## Test Suite

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=zah --cov-report=term-missing
```

Generate HTML coverage report:

```bash
pytest --cov=zah --cov-report=html
```

All modules in the project are covered at 100%.

---

## Project Structure

```
project/
│
├── zah/
│   ├── config.py
│   ├── dir_operations.py
│   ├── extensions.py
│   ├── hash.py
│   ├── logger.py
│   ├── single_instance.py
│   ├── zip.py
│   ├── main.py
│   └── __main__.py
│
└── tests/
    ├── test_config.py
    ├── test_dir_operations.py
    ├── test_extensions.py
    ├── test_hash.py
    ├── test_logger.py
    ├── test_zip.py
    ├── test_main.py
    ├── test_single_instance.py
    └── test___main__.py
```

---

## Example Runner Scripts

### Windows (`example_run.bat`)

```
call venv\Scripts\activate.bat
zah "C:\path\to\source" "C:\path\to\destination" --debug --fzip --unsafe
```

### Linux/macOS (`example_run.sh`)

```
. venv/bin/activate
eval zah "/path/to/source" "/path/to/destination" --debug --fzip --unsafe
```

---

## License

This project is distributed under the MIT License.

