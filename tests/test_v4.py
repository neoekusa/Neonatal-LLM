"""Regression checks for the corrected study and its reviewer-facing tables."""
import csv
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _model_labels import standardize_model_label
from _paths import OUTPUTS_DIR, SCORE_SOURCE, raw_paths
from analysis_data import load_long_analysis_df
from inference_v4 import PRIMARY, fit_gee, reference_code


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_long_analysis_df()

    def test_authoritative_score_source(self):
        with patch.dict(os.environ, {"NEO_SCORES_CSV": "", "NEO_TAXONOMY_CSV": ""}):
            scores, taxonomy = raw_paths()
            self.assertEqual(scores, ROOT / "data/raw/ydus_llm_scores.csv")
            self.assertEqual(taxonomy, ROOT / "data/raw/taxonomy_annotations.csv")
            with patch("_paths.SCORE_SOURCE", SCORE_SOURCE.with_name("missing.csv")):
                with self.assertRaises(FileNotFoundError):
                    raw_paths()
            with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"NEO_SCORES_CSV": tmp}):
                with self.assertRaisesRegex(ValueError, "in the repository"):
                    raw_paths()
        manifest = json.loads((OUTPUTS_DIR / "run_manifest.json").read_text())
        self.assertEqual(manifest["input_files"], {"scores": "data/raw/ydus_llm_scores.csv",
                                                   "taxonomy": "data/raw/taxonomy_annotations.csv"})

    def test_study_label_and_collision(self):
        earlier_header = "ChatGPT-4o".removesuffix("o")
        self.assertEqual(standardize_model_label(earlier_header), "ChatGPT-4o")
        self.assertEqual(standardize_model_label("ChatGPT-4.1"), "ChatGPT-4.1")
        scores, taxonomy = raw_paths()
        with scores.open(encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scores.csv"
            # Exercise a collision between the verbatim and corrected spellings.
            rows[0].append("ChatGPT-4o" if earlier_header in rows[0] else earlier_header)
            for row in rows[1:]:
                row.append("A")
            with path.open("w", newline="") as f:
                csv.writer(f).writerows(rows)
            with self.assertRaisesRegex(ValueError, "distinct model"):
                load_long_analysis_df(path, taxonomy)

    def test_scores_match_every_recorded_response(self):
        self.assertEqual(self.df.Number.nunique(), 127)
        self.assertEqual(self.df.Model.nunique(), 20)
        self.assertEqual(len(self.df), 2540)
        self.assertEqual(self.df.Failure.sum(), 351)
        source = pd.read_csv(raw_paths()[0], encoding="utf-8-sig", keep_default_na=False).set_index("Number")
        keys = source.pop("RealAnswer")
        expected = source.eq(keys, axis="index").astype(int)
        expected.columns = [standardize_model_label(label) for label in expected]
        published = pd.read_csv(OUTPUTS_DIR / "question_correctness.csv").set_index("question")
        pd.testing.assert_frame_equal(published.sort_index(axis=1), expected.sort_index(axis=1), check_names=False)

    def test_original_keys_and_source_labels(self):
        source = pd.read_csv(raw_paths()[0], encoding="utf-8-sig").set_index("Number")
        for header in ["ChatGPT-5.4", "ChatGPT-5.4 Thinking"]:
            panel = self.df.loc[self.df.Model.eq(header)].set_index("Number")
            pd.testing.assert_series_equal(panel.Answer, source[header], check_names=False)
            pd.testing.assert_series_equal(panel.RealAnswer, source.RealAnswer)
        self.assertEqual(reference_code(self.df).Model.cat.categories[0], "ChatGPT-4o")

    def test_primary_is_question_clustered_with_robust_interval(self):
        fit = fit_gee(reference_code(self.df), PRIMARY)
        self.assertEqual(fit.cov_type, "robust")
        self.assertEqual(len(fit.model.group_labels), 127)
        term = "Complexity[T.High]"
        estimate = np.exp([fit.params[term], *fit.conf_int().loc[term]])
        np.testing.assert_allclose(estimate, [7.58533, 1.76768, 32.54956], atol=0.0001)

    def test_complete_support_tables_and_rank_diagnostic(self):
        for file, total, occupied, singletons in [("primary_strata", 60, 25, 4),
                                                  ("full_strata", 2880, 63, 40)]:
            tab = pd.read_csv(OUTPUTS_DIR / f"{file}.csv")
            self.assertEqual((len(tab), sum(tab.questions > 0), sum(tab.questions == 1)),
                             (total, occupied, singletons))
            self.assertEqual((tab.questions.sum(), tab.responses.sum(), tab.incorrect.sum()), (127, 2540, 351))
            self.assertTrue(tab.loc[tab.questions == 0, "observed_failure"].isna().all())
        fits = pd.read_csv(OUTPUTS_DIR / "gee_model_fit.csv").set_index("model")
        self.assertTrue(fits.questions.eq(self.df.Number.nunique()).all())
        self.assertEqual(fits.loc["full_taxonomy", "design_rank"], 17)
        self.assertTrue(pd.isna(fits.loc["full_taxonomy", "qic"]))
        self.assertEqual(set(fits.index), {"primary", "full_taxonomy", "simplified", "llm_fixed_effects",
                                           "collapsed_exploratory"})

    def test_clinical_risk_test_excludes_the_risk_assessment_task(self):
        tests = pd.read_csv(OUTPUTS_DIR / "sensitivity_wald.csv")
        collapsed = tests.loc[tests.model.eq("collapsed_exploratory")].set_index("factor")
        self.assertEqual(collapsed.loc["Risk", "df"], self.df.Risk.nunique() - 1)
        self.assertEqual(collapsed.loc["Task", "df"], self.df.Task.nunique() - 1)
        self.assertAlmostEqual(collapsed.loc["Risk", "wald_chi2"], 0.593824, places=5)
        self.assertAlmostEqual(collapsed.loc["Task", "wald_chi2"], 0.500296, places=5)


if __name__ == "__main__":
    unittest.main()
