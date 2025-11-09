import argparse, os
import pandas as pd
import matplotlib.pyplot as plt
from core import DTNSim
from routers import EpidemicRouter, SprayWaitRouter

def run(args):
    if args.routing == 'epidemic':
        router = EpidemicRouter()
    elif args.routing == 'spray':
        router = SprayWaitRouter(L=args.copies)
    else:
        raise ValueError("routing must be 'epidemic' or 'spray'")

    sim = DTNSim(n_nodes=args.nodes, width=args.area[0], height=args.area[1],
                 radio_range=args.range, max_speed=args.speed, routing=router,
                 seed=args.seed, ttl=args.ttl, gen_prob=args.gen_prob)
    sim.run(steps=args.steps)
    summary = sim.summary()

    os.makedirs('outputs', exist_ok=True)
    df = pd.DataFrame(sim.event_log, columns=['time','delivered_this_step','tx_this_step','total_buffer'])
    df.to_csv('outputs/events.csv', index=False)
    pd.DataFrame([summary]).to_csv('outputs/run_metrics.csv', index=False)

    plt.figure()
    plt.plot(df['time'], df['delivered_this_step'], label='delivered')
    plt.plot(df['time'], df['tx_this_step'], label='transmissions')
    plt.plot(df['time'], df['total_buffer'], label='buffer size')
    plt.legend(); plt.xlabel('Time (steps)'); plt.ylabel('Count'); plt.title(f'DTN Simulation ({args.routing})')
    plt.tight_layout(); plt.savefig('outputs/metrics.png', dpi=150)

    print('Summary:', summary)
    print('Saved outputs: outputs/run_metrics.csv, outputs/events.csv, outputs/metrics.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nodes', type=int, default=40)
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--range', dest='range', type=float, default=30.0)
    parser.add_argument('--area', nargs=2, type=float, default=[400, 400])
    parser.add_argument('--speed', type=float, default=2.5)
    parser.add_argument('--routing', type=str, default='epidemic', choices=['epidemic','spray'])
    parser.add_argument('--copies', type=int, default=8)
    parser.add_argument('--ttl', type=int, default=2000)
    parser.add_argument('--gen-prob', type=float, default=0.02)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    run(args)
