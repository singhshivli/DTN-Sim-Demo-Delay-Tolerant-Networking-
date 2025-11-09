# DTN-Sim-Demo: Delay-Tolerant Networking (DTN) Store-Carry-Forward Simulator

**Topic:** Delay-Tolerant Networking (DTN) in Challenged Environments  
**Author:** Nirbhay (Ritick Pandey)  
**Domain:** Computer Networks (less-used topic)

This project simulates **store-carry-forward** routing for intermittently connected networks.
It includes:
- **Epidemic Routing**
- **Spray-and-Wait (binary)**

The simulator outputs:
- `outputs/run_metrics.csv` — overall metrics
- `outputs/events.csv` — per-step delivery/transmissions/buffer
- `outputs/metrics.png` — quick plot

## Quick Start (Mac)
```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Epidemic example
python simulate.py --nodes 60 --steps 1500 --range 40 --routing epidemic --area 500 500 --gen-prob 0.01

# Spray-and-Wait with 8 copies
python simulate.py --nodes 60 --steps 1500 --range 40 --routing spray --copies 8 --area 500 500 --gen-prob 0.01
