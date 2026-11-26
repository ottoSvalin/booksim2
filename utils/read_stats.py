#!/usr/bin/env python3
"""
Plot latency and throughput curves from BookSim sweep logs.

A sweep log is the console output of utils/sweep.sh (or of several BookSim runs
appended to one file). Every run with print_csv_results = 1 prints a line

    results:<class>,<traffic>,<use_read_write>,<injection_rate>,...

and this script reads those lines. Fields used (0-indexed):
    3  = offered injection rate (packets/node/cycle, the injection_rate you set)
    5  = average packet latency (cycles)
    20 = average accepted rate (packets/node/cycle)
    26 = average accepted rate (flits/node/cycle)

Each log file becomes one curve, labelled with its file name.

Usage:
    utils/sweep.sh src/booksim runfiles/baseline_mesh8x8.cfg > mesh.log
    python3 utils/read_stats.py mesh.log
    python3 utils/read_stats.py mesh.log torus.log --out compare.png
    python3 utils/read_stats.py mesh.log --plot latency
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

F_OFFERED = 3
F_AVG_LATENCY = 5
F_ACCEPTED_PACKETS = 20
F_ACCEPTED_FLITS = 26


def split_csv(line):
    """Split on commas, except inside brackets (e.g. hotspot({{0,1},{1,1}}))."""
    fields, depth, current = [], 0, ""
    for ch in line:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == "," and depth == 0:
            fields.append(current)
            current = ""
        else:
            current += ch
    fields.append(current)
    return fields


def read_log(path):
    """Return a list of (offered, latency, accepted_packets, accepted_flits), sorted by offered.

    A rate that appears more than once keeps its first result.
    """
    points = {}
    with open(path) as fh:
        for line in fh:
            if not line.startswith("results:"):
                continue
            fields = split_csv(line.strip())
            if len(fields) <= F_ACCEPTED_FLITS:
                continue
            offered = float(fields[F_OFFERED])
            if offered in points:
                continue
            points[offered] = (offered,
                               float(fields[F_AVG_LATENCY]),
                               float(fields[F_ACCEPTED_PACKETS]),
                               float(fields[F_ACCEPTED_FLITS]))
    return [points[k] for k in sorted(points)]


def print_table(label, points):
    print(f"\n{label}")
    print(f"{'offered':>10} {'latency':>10} {'accepted':>10}")
    for offered, latency, accepted, _ in points:
        print(f"{offered:>10.4f} {latency:>10.1f} {accepted:>10.4f}")


def plot(curves, ymax=None, which="both"):
    show_latency = which in ("latency", "both")
    show_throughput = which in ("throughput", "both")
    columns = 2 if which == "both" else 1
    fig, axes = plt.subplots(1, columns, figsize=(6.5 * columns, 5), squeeze=False)
    axes = list(axes[0])
    ax_lat = axes[0] if show_latency else None
    ax_thr = axes[-1] if show_throughput else None

    lowest_latency = None
    max_offered = 0.0
    for label, points in curves:
        offered = [p[0] for p in points]
        latency = [p[1] for p in points]
        accepted = [p[2] for p in points]
        if ax_lat:
            ax_lat.plot(offered, latency, marker="o", label=label)
        if ax_thr:
            ax_thr.plot(offered, accepted, marker="o", label=label)
        lowest_latency = min(latency) if lowest_latency is None else min(lowest_latency, min(latency))
        max_offered = max(max_offered, max(offered))

    if ax_lat:
        # Latency explodes past saturation; cut the axis so the low-load part stays readable.
        if ymax is None and lowest_latency:
            ymax = 4 * lowest_latency
        if ymax:
            ax_lat.set_ylim(0, ymax)
        ax_lat.set_xlim(left=0)
        ax_lat.set_title("Latency vs. offered load")
        ax_lat.set_xlabel("Offered load (packets/node/cycle)")
        ax_lat.set_ylabel("Average packet latency (cycles)")

    if ax_thr:
        # Accepted = offered until the network saturates.
        ax_thr.plot([0, max_offered], [0, max_offered], color="grey", linestyle="--",
                    linewidth=0.8, label="accepted = offered")
        ax_thr.set_xlim(left=0)
        ax_thr.set_ylim(bottom=0)
        ax_thr.set_title("Accepted vs. offered load")
        ax_thr.set_xlabel("Offered load (packets/node/cycle)")
        ax_thr.set_ylabel("Accepted throughput (packets/node/cycle)")

    for ax in axes:
        ax.grid(True, linewidth=0.4)
        ax.legend()
    fig.tight_layout()
    return fig


def main():
    parser = argparse.ArgumentParser(description="Plot BookSim latency and throughput curves.")
    parser.add_argument("logs", nargs="+", help="sweep log files, one curve each")
    parser.add_argument("--labels", help="comma-separated curve labels (default: file names)")
    parser.add_argument("--out", default="latency_throughput.png", help="output image")
    parser.add_argument("--plot", choices=["latency", "throughput", "both"], default="both",
                        help="which graph to draw (default: both)")
    parser.add_argument("--ymax", type=float,
                        help="latency axis limit (default: 4x the lowest latency)")
    args = parser.parse_args()

    labels = args.labels.split(",") if args.labels else []
    curves = []
    for i, path in enumerate(args.logs):
        points = read_log(path)
        label = labels[i] if i < len(labels) else os.path.splitext(os.path.basename(path))[0]
        if not points:
            print(f"Warning: no 'results:' lines in {path} (is print_csv_results = 1?)")
            continue
        print_table(label, points)
        curves.append((label, points))

    if not curves:
        sys.exit(1)

    fig = plot(curves, args.ymax, args.plot)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=150)
    print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()
