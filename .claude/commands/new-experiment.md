# Create New Experiment

Scaffold a new isolated experiment directory from the V46 base notebook.

## Instructions

1. Parse the experiment spec from arguments:
   - `$ARGUMENTS` should contain the experiment key (e.g., "exp05_v46_control") and a brief description
   - If not provided, ask the user for: experiment key, hypothesis, and which cell changes to make

2. Determine the next experiment number by listing existing `experiments/exp*/` directories.

3. Create the experiment directory structure:
   ```
   experiments/<exp_key>/
   ├── kernel-metadata.json
   ├── README.md
   └── notebook.ipynb (generated via create_experiment_notebooks.py or manual copy)
   ```

4. Create `kernel-metadata.json` from template:
   ```json
   {
     "id": "r1cky7/aimo3-<exp_key_with_hyphens>",
     "title": "aimo3-<exp_key_with_hyphens>",
     "code_file": "notebook.ipynb",
     "language": "python",
     "kernel_type": "notebook",
     "is_private": true,
     "enable_gpu": true,
     "enable_internet": false,
     "machine_shape": "NvidiaH100",
     "model_sources": ["danielhanchen/gpt-oss-120b/transformers/default/1"],
     "dataset_sources": ["r1cky7/aimo-3-utils"],
     "competition_sources": ["ai-mathematical-olympiad-progress-prize-3"]
   }
   ```

5. Create `README.md` with:
   - Experiment name and hypothesis
   - Changes from V46 base (which cells are patched and how)
   - Expected outcome
   - Run command: `python3 scripts/kaggle_kernel_run.py --metadata experiments/<exp_key>/kernel-metadata.json --download-output always`

6. For the notebook:
   - If `scripts/create_experiment_notebooks.py` already has a spec for this experiment, run it to generate
   - Otherwise, copy `notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb` as base and apply the required patches
   - ALWAYS include the 3 shared reliability patches: `resolve_input_archive()`, `CFG.resolve_model_path()`, `resolve_test_csv_path()`

7. Remind the user to:
   - Review the notebook changes
   - Run with `/kaggle-run <exp_key>`
   - Update `docs/EXPERIMENT_TODO.md` with the new experiment row

## Arguments
$ARGUMENTS - Experiment key and description (e.g., "exp05_v46_control - V46 logic with only reliability patches")
