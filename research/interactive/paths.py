import pathlib
import sys
#logger = logging.getLogger(__name__)

ROOT_FOLDER = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(1, str(ROOT_FOLDER / "src"))

from disruptsc import paths as _paths

PARAMETER_FOLDER = ROOT_FOLDER / "config" / "parameters"
OUTPUT_FOLDER = ROOT_FOLDER / "output"
TMP_FOLDER = ROOT_FOLDER / "tmp"
INPUT_FOLDER = _paths.INPUT_FOLDER
get_data_root = _paths.get_data_root
get_data_path = _paths.get_data_path
# if __file__ == "__main__":
#     print(ROOT_FOLDER)

# code_directory = Path(os.path.abspath(__file__)).parent
# project_directory = code_directory.parent
# working_directory = Path(os.getcwd())
# working_directory_parent = working_directory.parent
