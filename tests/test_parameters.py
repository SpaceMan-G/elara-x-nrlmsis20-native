from __future__ import annotations

import math
from pathlib import Path
import struct
import tempfile
import unittest

from elara_x_nrlmsis20 import parameters as p


class NativeParametersContractTests(unittest.TestCase):
    def setUp(self):
        # Reset the parameter-space flag so each test starts from a known state.
        p.haveparmspace = False
        p.initflag = False

    def _synthetic_parameter_file(self, directory: str) -> Path:
        path = Path(directory) / "synthetic.parm"
        values = [
            float(col * p.maxnbf + row) / 1000.0
            for col in range(131)
            for row in range(p.maxnbf)
        ]
        path.write_bytes(struct.pack(f"<{len(values)}d", *values))
        return path

    def test_parameter_space_contract(self):
        p.initparmspace()
        self.assertEqual(p.nvertparm, 131)
        expected = {
            "TN": (0, 23), "PR": (0, 23), "N2": (0, 9), "O2": (0, 9),
            "O1": (0, 17), "HE": (0, 9), "H1": (0, 9), "AR": (0, 9),
            "N1": (0, 9), "OA": (0, 9), "NO": (0, 17),
        }
        for name, bounds in expected.items():
            subset = getattr(p, name)
            self.assertEqual((subset.bl, subset.nl), bounds)
            self.assertEqual(subset.beta.shape, (512, bounds[1] - bounds[0] + 1))

    def test_parameter_loader_uses_fortran_column_major_layout(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._synthetic_parameter_file(td)
            p.initparmspace()
            p.loadparmset(path)
            self.assertEqual(p.TN.beta[37, 0], 0.037)
            self.assertEqual(p.TN.beta[37, 23], (23 * 512 + 37) / 1000.0)
            self.assertEqual(p.PR.beta[37, 0], (24 * 512 + 37) / 1000.0)
            self.assertEqual(p.N2.beta[37, 0], (25 * 512 + 37) / 1000.0)
            self.assertEqual(p.NO.beta[37, 17], (130 * 512 + 37) / 1000.0)

    def test_reciprocal_node_arrays_and_modulation_flags(self):
        p.initparmspace()
        self.assertAlmostEqual(p.etaTN[0, 2], 1.0 / 5.0, places=15)
        self.assertAlmostEqual(p.etaO1[0, 4], 1.0 / 15.0, places=15)
        self.assertAlmostEqual(p.etaNO[0, 4], 1.0 / 22.5, places=15)
        self.assertTrue(all(p.zsfx[i] for i in (9, 10, 13, 14, 17, 18)))
        self.assertTrue(all(p.tsfx[i] for i in range(p.ctide, p.cspw)))
        self.assertTrue(all(p.psfx[i] for i in range(p.cspw, p.cspw + 60)))

    def test_legacy_switch_rounding_and_retrieval(self):
        p.swg[:] = [True] * p.maxnbf
        values = [1.0] * 25
        values[8] = -1.0
        values[3] = 1.25
        p.tselec(values)
        self.assertEqual(p.tretrv(), tuple(p._f32(v) for v in values))
        self.assertEqual(p.swleg[3], p._f32(1.25))
        self.assertEqual(p.swc[3], p._f32(0.0))
        self.assertFalse(p.swg[p.cmag])
        self.assertTrue(p.swg[p.cmag + 1])

    def test_direct_switch_gfn_takes_precedence(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._synthetic_parameter_file(td)
            direct = [(i % 7) == 0 for i in range(p.maxnbf)]
            legacy = [0.0] * 25
            p.msisinit(
                parmpath=str(path.parent) + "/",
                parmfile=path.name,
                switch_gfn=direct,
                switch_legacy=legacy,
            )
            self.assertEqual(p.swg, direct)

    def test_mass_density_disabled_forces_mass_flags_off(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._synthetic_parameter_file(td)
            species = [False] * 10
            species[1] = True
            species[3] = True
            p.msisinit(
                parmpath=str(path.parent) + "/",
                parmfile=path.name,
                lspec_select=species,
                lmass_include=[True] * 10,
            )
            self.assertTrue(p.initflag)
            self.assertFalse(p.specflag[0])
            self.assertEqual(p.massflag, [False] * 10)
            self.assertEqual(p.masswgt, [0.0] * 10)

    def test_parameter_file_size_is_strict(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.parm"
            bad.write_bytes(b"\x00" * 64)
            p.initparmspace()
            with self.assertRaises(ValueError):
                p.loadparmset(bad)


if __name__ == "__main__":
    unittest.main()
