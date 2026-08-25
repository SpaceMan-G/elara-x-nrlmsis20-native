from __future__ import annotations
import hashlib
from pathlib import Path
import unittest

EXPECTED = {'__init__.py': 'c07f60411df49c5b1203c68342f96d09541a2bbd86ebd7763889aea233b3fab6', 'api.py': 'f92aa6c854bdf65b0cecd3053034ae212c4c72c82d0ee80d96f4adc9bfcf13f9', 'constants.py': '3c97e85f5ea891e200dcce38d8efe6ec25fcff1c06697a6109b1f37b1055f5ca', 'density.py': 'fede84c5e8d0f2845289e538bf0f26da9e4317f3e4445d3ba043ce2f429459f7', 'horizontal.py': '1113030999565ccec233f8b0e95afa8562f58099510e99bfe4fe8f3a704c1bff', 'legacy_interface.py': 'b87481bbf999b70ac441daae645c485a3a47edbbb4fe58714599ef8b1294d39c', 'model.py': 'bb49106ad0f4f5292540a5cff110a5ba27828ea0067a9bd80d4471266c68d8b4', 'parameters.py': '5b5302c2f6ec092d064c83c81f245d6b6cb6a4ae32d692499f20b350782ff8b3', 'resources.py': 'eb6d32980be7d3c224d78d68ee7b4b1878364f6c349edd816876cb0958299660', 'temperature.py': 'd82408d265322e124597b6db6964f48a1ebe5b68a974ce8e512105eda420edcf', 'utilities.py': '3383b0e9123b7ffe6d0459bf2a63845e04862699325da325820f60f8e066177a'}
FORBIDDEN = ['msis2.0_test.F90', 'msis2.0_test_in.txt', 'msis2.0_test_ref_dp.txt', 'msis2.1_test.F90', 'msis2.1_test_in.txt', 'msis2.1_test_ref_dp.txt', 'msis20.parm', 'msis21.parm', 'msis_calc.F90', 'msis_constants.F90', 'msis_dfn.F90', 'msis_gfn.F90', 'msis_gtd8d.F90', 'msis_init.F90', 'msis_tfn.F90', 'msis_utils.F90']
FORTRAN = ['.f', '.f03', '.f08', '.f90', '.f95', '.for']

class RepositoryContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_exact_extracted_source_identities(self):
        base = self.root / "src" / "elara_x_nrlmsis20"
        actual = {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in EXPECTED}
        self.assertEqual(EXPECTED, actual)

    def test_no_restricted_payload_or_fortran(self):
        hits = []
        for path in self.root.rglob("*"):
            if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts) or not path.is_file():
                continue
            if path.name in FORBIDDEN or path.suffix.lower() in FORTRAN:
                hits.append(path.relative_to(self.root).as_posix())
        self.assertEqual([], hits)

    def test_no_private_absolute_path_or_excluded_model(self):
        hits = []
        private_home = b"/users/" + b"giuseppejoulianou/"
        private_workspace = b"elara_x_" + b"package_workspace"
        excluded_model = b"dtm" + b"2020"
        for path in self.root.rglob("*"):
            if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts) or not path.is_file():
                continue
            data = path.read_bytes().lower()
            if private_home in data or private_workspace in data or excluded_model in data:
                hits.append(path.relative_to(self.root).as_posix())
        self.assertEqual([], hits)

if __name__ == "__main__":
    unittest.main()
