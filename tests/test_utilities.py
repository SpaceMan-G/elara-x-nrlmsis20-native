from __future__ import annotations

import math
import unittest

from elara_x_nrlmsis20.utilities import alt2gph, bspline, dilog, gph2alt


def _fixture_eta(nodes, nd):
    eta = {(j, k): 0.0 for k in range(2, 7) for j in range(31)}
    for k in range(2, 7):
        for j in range(0, nd - k + 2):
            eta[j, k] = 1.0 / (nodes[j + k - 1] - nodes[j])
    return eta


class NativeUtilitiesContractTests(unittest.TestCase):
    def test_altitude_geopotential_round_trip(self):
        for lat in (-90.0, -45.0, 0.0, 45.0, 90.0):
            for alt in (0.0, 50.0, 100.0, 400.0, 1000.0):
                gph = alt2gph(lat, alt)
                recovered = gph2alt(lat, gph)
                self.assertTrue(math.isfinite(gph))
                self.assertAlmostEqual(recovered, alt, delta=0.001)

    def test_bspline_boundary_index_contract(self):
        nodes = (-10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 80.0, 120.0, 170.0)
        nd = 10
        eta = _fixture_eta(nodes, nd)

        low_s, low_i = bspline(nodes[0], nodes, nd, 6, eta)
        high_s, high_i = bspline(nodes[nd], nodes, nd, 6, eta)

        self.assertEqual(low_i, -1)
        self.assertEqual(high_i, nd)
        self.assertTrue(all(value == 0.0 for value in low_s.values()))
        self.assertTrue(all(value == 0.0 for value in high_s.values()))

    def test_bspline_preserves_fortran_logical_indices(self):
        nodes = (-10.0, -5.0, 0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 80.0, 120.0, 170.0)
        nd = 10
        eta = _fixture_eta(nodes, nd)
        s, i = bspline(25.0, nodes, nd, 6, eta)

        self.assertEqual(set(s), {(l, k) for k in range(2, 7) for l in range(-5, 1)})
        self.assertEqual(i, 5)
        self.assertTrue(all(math.isfinite(value) for value in s.values()))
        self.assertTrue(all(value >= 0.0 for value in s.values()))
        self.assertAlmostEqual(s[-1, 2], 0.5, places=15)
        self.assertAlmostEqual(s[0, 2], 0.5, places=15)

    def test_dilog_reference_properties(self):
        self.assertEqual(dilog(0.0), 0.0)
        self.assertTrue(math.isfinite(dilog(0.5)))
        self.assertTrue(math.isfinite(dilog(0.99)))
        self.assertLess(dilog(0.1), dilog(0.5))
        self.assertLess(dilog(0.5), dilog(0.99))

    def test_public_utility_functions_are_callable(self):
        for fn in (alt2gph, gph2alt, bspline, dilog):
            self.assertTrue(callable(fn))


if __name__ == "__main__":
    unittest.main()
