"""DAT575 Lab 2: draw the link utilisation of the 8x8 mesh from BookSim's sent_flits_out file.

BookSim must be built with flow tracking (make DEFINE=-DTRACK_FLOWS) and run with
sent_flits_out=<file>. The file has one line per sample period, 5 outputs per router:
0 = +x (E), 1 = -x (W), 2 = +y (N), 3 = -y (S), 4 = eject. The warm-up lines are skipped.
Assumes the Lab 2 configuration: k = 8, sample_period = 10000, warmup_periods = 3.

usage: python3 link_heatmap.py out.png "title1" file1 ["title2" file2 ...]"""
import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
K, PERIOD, WARMUP, PORTS = 8, 10000, 3, 5
cmap = LinearSegmentedColormap.from_list("gr", ["#e5f5e0", "#a1d99b", "#fdd49e", "#fc8d59", "#d7301f", "#7f0000"])  # green to red, lightness falls monotonically (readable for colour-blind and in grey)
def load(f):
    rows = [list(map(int, l.strip().split(","))) for l in open(f) if l.strip()]
    rows = rows[WARMUP:] or rows
    v = [sum(r[i] for r in rows) / (len(rows) * PERIOD) for i in range(len(rows[0]))]
    return {(rt, p): v[rt * PORTS + p] for rt in range(K * K) for p in range(4)}
if len(sys.argv) < 4 or len(sys.argv) % 2 != 0:
    sys.exit('usage: python3 link_heatmap.py out.png "title1" file1 ["title2" file2 ...]')
out, args = sys.argv[1], sys.argv[2:]
panels = list(zip(args[0::2], args[1::2]))
cols = {4: 2, 6: 3, 10: 5}.get(len(panels), min(4, len(panels))); rws = (len(panels) + cols - 1) // cols
fig, axs = plt.subplots(rws, cols, figsize=(5.6 * cols, 6.0 * rws), facecolor="#fcfcfb")
axs = list(axs.flat) if len(panels) > 1 else [axs]
norm = Normalize(0, 1)
for ax in axs[len(panels):]: ax.axis("off")
d, off = 0.18, 0.09   # end gap, side offset so the two directions sit side by side
for ax, (title, f) in zip(axs, panels):
    u = load(f); links = []
    for rt in range(K * K):
        x, y = rt % K, rt // K
        for p, (dx, dy) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)]):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < K and 0 <= ny < K): continue
            val = u[(rt, p)]; links.append(val)
            ox, oy = (-dy * off, dx * off)       # offset to the left of travel direction
            ax.annotate("", xy=(nx - dx * d + ox, ny - dy * d + oy), xytext=(x + dx * d + ox, y + dy * d + oy),
                        arrowprops=dict(arrowstyle="-|>", color=cmap(norm(val)), lw=2.6, mutation_scale=9))
    for rt in range(K * K):
        ax.plot(rt % K, rt // K, "s", ms=7, color="#ffffff", mec="#b5b4ae", mew=0.8)
    mx, avg = max(links), sum(links) / len(links)
    ax.set_title(f"{title}\nbusiest link {mx:.2f}   average {avg:.2f}  (flits/cycle)", fontsize=12, loc="left", color="#0b0b0b")
    ax.set_xlim(-0.6, K - 0.4); ax.set_ylim(-0.6, K - 0.4); ax.set_aspect("equal"); ax.axis("off")
cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=list(axs), shrink=0.7, pad=0.02)
cb.set_label("link utilisation (flits/cycle)", color="#52514e")
fig.savefig(out, dpi=130, facecolor="#fcfcfb", bbox_inches="tight")
print(out)
