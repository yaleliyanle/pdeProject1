# Tutorial 1 environment setup

Use Python 3.9 or newer. From the repository root, run:

```bash
python -m pip install -r tutorial1/requirements.txt
python -c "import numpy, scipy, matplotlib; print('OK'); print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('matplotlib', matplotlib.__version__)"
```

The scaffold sanity check is:

```bash
python tutorial1/rk4_stability_region.py
```

It writes `tutorial1/figures/stability_regions.png`. Generated figures and numerical
outputs are ignored by Git, as required by the tutorial instructions.
