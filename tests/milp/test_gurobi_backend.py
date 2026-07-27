import unittest
from itertools import product

from three_set_milp.ciphers.present import PRESENT_SBOX
from three_set_milp.ciphers.rectangle import RECTANGLE_SBOX
from three_set_milp.core.bitvector import from_index_bits, to_index_bits
from three_set_milp.milp.gurobi_backend import (
    GurobiModel,
    GurobiUnavailableError,
    SolveStatus,
)
from three_set_milp.milp.transitions import (
    and_transition_is_valid,
    copy_transition_is_valid,
    valid_sbox_transitions,
    xor_transition_is_valid,
)


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
        valid = valid_sbox_transitions(truth_table, 2, 2)

        for input_value, output_value in product(range(4), repeat=2):
            model = GurobiModel("sbox_test")
            input_variables = model.add_binary_vector("a", 2)
            output_variables = model.add_binary_vector("b", 2)
            model.add_sbox(input_variables, output_variables, truth_table)
            model.fix_vector(input_variables, input_value)
            model.fix_vector(output_variables, output_value)
            expected = (input_value, output_value) in valid
            self.assertEqual(model.solve() is SolveStatus.FEASIBLE, expected)

    def test_compact_paper_sbox_assignments(self) -> None:
        """用 Gurobi 穷举附录 C 的 PRESENT/RECTANGLE 紧凑模型。"""
        for truth_table in (PRESENT_SBOX, RECTANGLE_SBOX):
            valid = valid_sbox_transitions(truth_table, 4, 4)
            model = GurobiModel("compact_sbox_test")
            input_variables = model.add_binary_vector("a", 4)
            output_variables = model.add_binary_vector("b", 4)
            model.add_sbox(input_variables, output_variables, truth_table)
            input_fixer = model.add_vector_fixer(
                input_variables, name="input_fix"
            )
            output_fixer = model.add_vector_fixer(
                output_variables, name="output_fix"
            )
            model.model.update()

            for input_value, output_value in product(range(16), repeat=2):
                model.set_vector_fixer(input_fixer, input_value)
                model.set_vector_fixer(output_fixer, output_value)
                expected = (input_value, output_value) in valid
                self.assertEqual(
                    model.solve() is SolveStatus.FEASIBLE,
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
