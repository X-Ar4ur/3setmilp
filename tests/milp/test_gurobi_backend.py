import unittest
from itertools import product

from three_set_milp.core.bitvector import from_index_bits, to_index_bits
from three_set_milp.milp.gurobi_backend import (
    GurobiModel,
    GurobiUnavailableError,
    SolveStatus,
)
from three_set_milp.milp.transitions import (
    and_transition_is_valid,
    copy_transition_is_valid,
    sbox_transition_is_valid,
    valid_sbox_transitions,
    xor_transition_is_valid,
)
from three_set_milp.core.anf import output_monomial_anfs


def _gurobi_is_usable() -> tuple[bool, str]:
    try:
        model = GurobiModel("license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        return False, str(error)
    return True, ""


GUROBI_USABLE, GUROBI_REASON = _gurobi_is_usable()


@unittest.skipUnless(GUROBI_USABLE, GUROBI_REASON)
class GurobiBackendTests(unittest.TestCase):
    def test_copy_assignments(self) -> None:
        for input_bit, outputs in product((0, 1), product((0, 1), repeat=2)):
            model = GurobiModel("copy_test")
            input_variable = model.add_binary_vector("a", 1)
            output_variables = model.add_binary_vector("b", 2)
            model.add_copy(input_variable[0], output_variables)
            model.fix_vector(input_variable, input_bit)
            model.fix_vector(output_variables, from_index_bits(outputs))
            expected = copy_transition_is_valid(input_bit, outputs)
            self.assertEqual(model.solve() is SolveStatus.FEASIBLE, expected)

    def test_xor_and_assignments(self) -> None:
        for operation in ("xor", "and"):
            for inputs in product((0, 1), repeat=2):
                for output in (0, 1):
                    model = GurobiModel(f"{operation}_test")
                    input_variables = model.add_binary_vector("a", 2)
                    output_variable = model.add_binary_vector("b", 1)
                    if operation == "xor":
                        model.add_xor(input_variables, output_variable[0])
                        expected = xor_transition_is_valid(inputs, output)
                    else:
                        model.add_and(input_variables, output_variable[0])
                        expected = and_transition_is_valid(inputs, output)
                    model.fix_vector(input_variables, from_index_bits(inputs))
                    model.fix_vector(output_variable, output)
                    self.assertEqual(model.solve() is SolveStatus.FEASIBLE, expected)

    def test_sbox_assignments(self) -> None:
        truth_table = []
        for value in range(4):
            x0, x1 = to_index_bits(value, 2)
            truth_table.append(from_index_bits([x0, (x0 & x1) ^ x1]))
        monomial_anfs = output_monomial_anfs(truth_table, 2, 2)

        for input_value, output_value in product(range(4), repeat=2):
            model = GurobiModel("sbox_test")
            input_variables = model.add_binary_vector("a", 2)
            output_variables = model.add_binary_vector("b", 2)
            model.add_sbox(input_variables, output_variables, truth_table)
            model.fix_vector(input_variables, input_value)
            model.fix_vector(output_variables, output_value)
            expected = sbox_transition_is_valid(
                input_value, output_value, monomial_anfs
            )
            self.assertEqual(model.solve() is SolveStatus.FEASIBLE, expected)


if __name__ == "__main__":
    unittest.main()

