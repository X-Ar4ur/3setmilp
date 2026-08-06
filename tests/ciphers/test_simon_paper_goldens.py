"""主论文第 5.1 节 SIMON32 两个局部黄金检查点。"""

import unittest

from three_set_milp.ciphers.simon import SIMON32, format_paper_state

from experiments.audit_simon32_paper_goldens import (
    L2,
    L3,
    L4,
    paper_bit_mapping,
    q_1_15_golden,
    q_1_16_golden,
)


class Simon32PaperGoldenTests(unittest.TestCase):
    def test_paper_rightmost_bit_maps_to_internal_16(self) -> None:
        mapping = paper_bit_mapping()

        self.assertEqual(mapping["rightmost_paper_position"], 31)
        self.assertEqual(mapping["rightmost_internal_m"], 16)
        balanced_paper_positions = {17, 24, 31}
        balanced_internal = {
            entry["internal_m"]
            for entry in mapping["positions"]
            if entry["paper_position"] in balanced_paper_positions
        }
        self.assertEqual(balanced_internal, {16, 23, 30})

    def test_q_1_15_exact_contributions_and_cancellation(self) -> None:
        result = q_1_15_golden()

        self.assertTrue(all(result["checks"].values()))
        counts = {
            entry["vector"]["paper_bits"]: entry["count"]
            for entry in result["occurrences"]
        }
        self.assertEqual(counts[format_paper_state(L2, SIMON32)], 2)
        self.assertEqual(
            {entry["paper_bits"] for entry in result["odd_after_mod2"]},
            {
                format_paper_state(L3, SIMON32),
                format_paper_state(L4, SIMON32),
            },
        )

    def test_q_1_16_rule4_reduce_and_swap_stages(self) -> None:
        result = q_1_16_golden()

        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(len(result["rule4_raw_additions"]), 1)
        self.assertEqual(result["rule4_raw_additions"][0]["key_internal_index"], 31)
        self.assertEqual(len(result["k_after_reduce0"]), 1)
        self.assertEqual(len(result["l_after_reduce1"]), 1)


if __name__ == "__main__":
    unittest.main()
