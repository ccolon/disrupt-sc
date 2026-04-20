import pathlib
import sys
import os
import time
import shutil
#logger = logging.getLogger(__name__)

ROOT_FOLDER = pathlib.Path(__file__).parent.parent.parent
PARAMETER_FOLDER = ROOT_FOLDER / "config" / "parameters"
OUTPUT_FOLDER = ROOT_FOLDER / "output"
TMP_FOLDER = ROOT_FOLDER / "tmp"

# Global variable to store the isolated cache directory for this process
_ISOLATED_CACHE_DIR = None
_CACHE_ISOLATION_ENABLED = False

def setup_cache_isolation(scope: str):
    """Setup isolated cache directory for this process."""
    global _ISOLATED_CACHE_DIR, _CACHE_ISOLATION_ENABLED
    
    if _CACHE_ISOLATION_ENABLED:
        return  # Already setup
    
    process_id = os.getpid()
    timestamp = round(time.time() * 1000)
    dir_name = f"{scope}_pid_{process_id}_{timestamp}"
    
    _ISOLATED_CACHE_DIR = TMP_FOLDER / dir_name
    _ISOLATED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _CACHE_ISOLATION_ENABLED = True

def get_cache_dir() -> pathlib.Path:
    """Get the cache directory (isolated or shared)."""
    if _CACHE_ISOLATION_ENABLED and _ISOLATED_CACHE_DIR:
        return _ISOLATED_CACHE_DIR
    return TMP_FOLDER

def cleanup_isolated_cache():
    """Clean up isolated cache directory."""
    global _ISOLATED_CACHE_DIR, _CACHE_ISOLATION_ENABLED
    
    if _CACHE_ISOLATION_ENABLED and _ISOLATED_CACHE_DIR and _ISOLATED_CACHE_DIR.exists():
        shutil.rmtree(_ISOLATED_CACHE_DIR)
        _ISOLATED_CACHE_DIR = None
        _CACHE_ISOLATION_ENABLED = False

DATA_ENV_VAR = "DISRUPT_SC_DATA_PATH"
SIBLING_DATA_FOLDER = ROOT_FOLDER.parent / "disrupt-sc-data"
EXAMPLE_DATA_FOLDER = ROOT_FOLDER / "examples" / "data"
BUNDLED_EXAMPLE_SCOPES = {"Testkistan"}


def _normalize_data_path(path: str | os.PathLike) -> pathlib.Path:
    """Expand and resolve a configured data path."""
    return pathlib.Path(path).expanduser().resolve()


def resolve_input_folder() -> pathlib.Path:
    """Resolve the default data root used by non-bundled scopes."""
    data_path = os.environ.get(DATA_ENV_VAR)
    if data_path:
        input_folder = _normalize_data_path(data_path)
        if not input_folder.exists():
            raise FileNotFoundError(
                f"{DATA_ENV_VAR} points to '{input_folder}', but that folder does not exist."
            )
        return input_folder

    if SIBLING_DATA_FOLDER.exists():
        return SIBLING_DATA_FOLDER.resolve()

    return EXAMPLE_DATA_FOLDER.resolve()


def get_data_root() -> pathlib.Path:
    """Return the resolved root folder containing scope data folders."""
    return INPUT_FOLDER


def get_data_path(scope: str) -> pathlib.Path:
    """Return the resolved folder for a specific scope."""
    data_path = os.environ.get(DATA_ENV_VAR)
    if data_path:
        return _normalize_data_path(data_path) / scope

    example_path = EXAMPLE_DATA_FOLDER / scope
    if scope in BUNDLED_EXAMPLE_SCOPES and example_path.exists():
        return example_path.resolve()

    if SIBLING_DATA_FOLDER.exists():
        return SIBLING_DATA_FOLDER.resolve() / scope

    return example_path.resolve()


INPUT_FOLDER = resolve_input_folder()

sys.path.insert(1, str(ROOT_FOLDER))
# if __file__ == "__main__":
#     print(ROOT_FOLDER)

# code_directory = Path(os.path.abspath(__file__)).parent
# project_directory = code_directory.parent
# working_directory = Path(os.getcwd())
# working_directory_parent = working_directory.parent
