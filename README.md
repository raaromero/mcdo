# Monte Carlo Simulation Package

A Python package for performing Monte Carlo simulations.

## Installation

### For development (editable install):
```bash
pip install -e .
```

### With development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

```python
from monte_carlo import MonteCarloSimulator

# Create a simulator
simulator = MonteCarloSimulator(n_simulations=10000)

# Run simulations
results = simulator.run(your_function, *args, **kwargs)
```

## Structure

```
.
├── monte_carlo/        # Main package directory
│   ├── __init__.py
│   └── core.py        # Core simulation functionality
├── notebooks/         # Jupyter notebooks for examples
├── setup.py          # Package installation script
└── README.md         # This file
```
