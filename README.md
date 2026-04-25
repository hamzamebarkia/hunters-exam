# Hunter Exam Survival Optimizer

This repository contains the simulation engine and analysis tools for the 287th Hunter Exam, as requested by Chairman Netero.

## Contents
- `simulation.py`: The core simulation engine that predicts survival probabilities based on applicant and phase JSON files.
- `data_generator.py`: A script to generate the `applicants.json` and `phases.json` mock datasets.
- `Survival_Path_Report.txt`: The optimal sequence of decisions made to survive all phases of the exam.
- `Strategy_Document.txt`: Detailed explanation of the simulation algorithm, detecting wildcards/ringers, and handling trust.
- `visualize.py`: Script to generate a visual representation of survival rates.
- `survival_visualization.png`: A graph showing the number of active applicants at each phase.

## Usage
Run the simulation:
```bash
python simulation.py
```

Generate the visualization:
```bash
python visualize.py
```

## Hidden Inscription
"In the sea of faces, the one who watches the watchers watches themselves most. Trust is a mirror—what you see depends on who holds it. The wild one is not wild to themselves. And the false face? It cracks first when no one is looking. Conserve when others burn. Burn when others rest. The final phase remembers who arrived fresh and who arrived broken."
