# Raw data

The v4 pipeline reads two repository files.

- [ydus_llm_scores.csv](ydus_llm_scores.csv) contains the original key in `RealAnswer` and 20 recorded responses per question.
- [taxonomy_annotations.csv](taxonomy_annotations.csv) contains one consensus classification for each of the same 127 questions.

The run manifest records their paths and SHA-256 hashes. To select other inputs explicitly, set `NEO_SCORES_CSV` and `NEO_TAXONOMY_CSV` to files within the repository. [Run manifest](../../outputs/v4/run_manifest.json)
