"""Run the reproducible core analysis from raw data.

The distributed scripts remain the source of each table/model. This file only
imports them in the dependency order needed to regenerate the core outputs.
"""

from analysis_data import validate_raw_data

import compare_all_model_qic
import make_cognitive_complexity_comparison
import make_collapsed_exploratory_sensitivity_outputs
import make_consensus_hard_table
import make_joint_wald_comparison_table
import make_marginal_complexity_outputs
import rebuild_full_exploratory_remember
import regenerate_primary_submission_outputs
import run_clean_gee_lpm_analysis


STEPS = [
    ("primary outputs", regenerate_primary_submission_outputs.main),
    ("simplified GEE/LPM", run_clean_gee_lpm_analysis.main),
    ("primary vs simplified comparison", make_cognitive_complexity_comparison.main),
    ("QIC/QICu comparison", compare_all_model_qic.main),
    ("expanded exploratory GEE", rebuild_full_exploratory_remember.main),
    ("collapsed exploratory sensitivity", make_collapsed_exploratory_sensitivity_outputs.main),
    ("joint Wald comparison", make_joint_wald_comparison_table.main),
    ("marginal complexity outputs", make_marginal_complexity_outputs.main),
    ("consensus hard table", make_consensus_hard_table.main),
]


def main():
    audit = validate_raw_data()
    print(f"Using scores: {audit.scores_path}")
    print(f"Using taxonomy: {audit.taxonomy_path}")
    print(f"Raw data: {audit.n_questions} questions, {audit.n_models} models")
    print(audit.processing_needed)
    for label, step in STEPS:
        print(f"\n=== {label} ===")
        step()


if __name__ == "__main__":
    main()
