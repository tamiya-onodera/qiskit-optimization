# This code is part of Qiskit.
#
# (C) Copyright IBM 2020, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Stable Set """

import unittest
from test import QiskitOptimizationTestCase
import numpy as np
from qiskit import BasicAer
from qiskit.circuit.library import EfficientSU2
from qiskit.utils import algorithm_globals, QuantumInstance
from qiskit.algorithms import NumPyMinimumEigensolver, VQE
from qiskit.algorithms.optimizers import L_BFGS_B
from qiskit_optimization.applications.ising import stable_set
from qiskit_optimization.applications.ising.common import random_graph, sample_most_likely


class TestStableSet(QiskitOptimizationTestCase):
    """Stable Set Ising tests."""

    def setUp(self):
        super().setUp()
        self.seed = 8123179
        algorithm_globals.random_seed = self.seed
        self.num_nodes = 5
        self.w = random_graph(self.num_nodes, edge_prob=0.5)
        self.qubit_op, self.offset = stable_set.get_operator(self.w)

    def test_stable_set(self):
        """ Stable set test """
        algo = NumPyMinimumEigensolver()
        result = algo.compute_minimum_eigenvalue(self.qubit_op, aux_operators=[])
        x = sample_most_likely(result.eigenstate)
        self.assertAlmostEqual(result.eigenvalue.real, -39.5)
        self.assertAlmostEqual(result.eigenvalue.real + self.offset, -38.0)
        ising_sol = stable_set.get_graph_solution(x)
        np.testing.assert_array_equal(ising_sol, [1, 1, 0, 1, 1])
        self.assertEqual(stable_set.stable_set_value(x, self.w), (4, False))

    def test_stable_set_vqe(self):
        """ VQE Stable set  test """
        q_i = QuantumInstance(BasicAer.get_backend('statevector_simulator'),
                              seed_simulator=algorithm_globals.random_seed,
                              seed_transpiler=algorithm_globals.random_seed)
        result = VQE(EfficientSU2(reps=3, entanglement='linear'),
                     L_BFGS_B(maxfun=6000),
                     quantum_instance=q_i).compute_minimum_eigenvalue(self.qubit_op)
        x = sample_most_likely(result.eigenstate)
        self.assertAlmostEqual(result.eigenvalue, -39.5)
        self.assertAlmostEqual(result.eigenvalue + self.offset, -38.0)
        ising_sol = stable_set.get_graph_solution(x)
        np.testing.assert_array_equal(ising_sol, [1, 1, 0, 1, 1])
        self.assertEqual(stable_set.stable_set_value(x, self.w), (4.0, False))


if __name__ == '__main__':
    unittest.main()
