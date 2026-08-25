from __future__ import annotations

import math
import unittest

from elara_x_nrlmsis20 import constants as c


class NativeConstantsContractTests(unittest.TestCase):
    def test_precision_and_core_dimensions(self):
        self.assertEqual(c.rp, 8)
        self.assertEqual(c.nspec, 11)
        self.assertEqual(c.nd, 27)
        self.assertEqual(c.p, 4)
        self.assertEqual(c.nl, 23)
        self.assertEqual(c.nls, 9)

    def test_vector_dimensions(self):
        self.assertEqual(len(c.specmass), 10)
        self.assertEqual(len(c.lnvmr), 10)
        self.assertEqual(len(c.nodesTN), 30)
        self.assertEqual(len(c.nodesO1), 14)
        self.assertEqual(len(c.nodesNO), 14)
        self.assertEqual(len(c.wbeta), 24)
        self.assertEqual(len(c.wgamma), 24)

    def test_lnp0_preserves_fortran_default_real_promotion(self):
        self.assertEqual(c.lnP0, 11.515613555908203125)

    def test_fortran_reshape_semantics_are_preserved(self):
        self.assertEqual(c.c2tn[0], (1.0, 1.0, 1.0))
        self.assertEqual(c.c2tn[1], (-10.0, 0.0, 10.0))
        self.assertEqual(
            c.c1NO,
            ((1.5, 0.0), (-3.75, 15.0)),
        )

    def test_derived_index_offsets(self):
        self.assertEqual(c.ctimeind, 0)
        self.assertEqual(c.cintann, 7)
        self.assertEqual(c.ctide, 35)
        self.assertEqual(c.cspw, 185)
        self.assertEqual(c.csfx, 295)
        self.assertEqual(c.cextra, 300)
        self.assertEqual(c.cnonlin, 384)
        self.assertEqual(c.csfxmod, 384)
        self.assertEqual(c.cmag, 389)
        self.assertEqual(c.cut, 443)

    def test_derived_physical_constants_are_finite(self):
        for value in (c.g0divkB, c.Mbarg0divkB, c.HOA):
            self.assertTrue(math.isfinite(value))
            self.assertGreater(value, 0.0)


if __name__ == "__main__":
    unittest.main()
