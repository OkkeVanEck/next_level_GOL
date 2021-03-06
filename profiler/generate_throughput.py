"""
Generate figures for throughput plots.
"""
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import glob


def load_results():
    rows = []

    # Load results in variables.
    for v in versions:
        fs = glob.glob(f"results/{results_folder}/{v}_*.out")

        for run_fp in fs:
            with open(run_fp, "r") as fp:
                lines = fp.readlines()
                rows.append({"version": v, "type": "init", "value": float(lines[1][12:17])})
                rows.append({"version": v, "type": "wrap", "value": float(lines[2][12:17])})
                rows.append({"version": v, "type": "step", "value": float(lines[3][12:17])})
                rows.append({"version": v, "type": "swap", "value": float(lines[4][12:17])})
                rows.append({"version": v, "type": "gif", "value": float(lines[5][12:17])})
                rows.append({"version": v, "type": "final", "value": float(lines[6][12:17])})

                # For pthreads code, we take the actual time as total, which makes the throughput 1 row lower.
                # Including version 7.0, because it is special (and does have latency hiding without pthreads).
                if int(v[1:2]) >= 6:
                    rows.append({"version": v, "type": "total", "value": float(lines[9][11:16])})
                    rows.append({"version": v, "type": "throughput", "value": float(lines[11][12:21])})
                else:
                    rows.append({"version": v, "type": "total", "value": float(lines[8][11:16])})
                    rows.append({"version": v, "type": "throughput", "value": float(lines[10][12:21])})

    values = pd.DataFrame(rows)

    return values


def gen_throughput():
    # Fetch DatFrame with measured values.
    df = load_results()

    # Create DataFrame with mean values and normalize.
    df_mean = df.pivot_table(index="version",
                             columns="type",
                             values="value",
                             aggfunc="mean")

    # Create DataFrame with normalized performance numbers.
    df = pd.DataFrame({"Version": versions,
                       "throughput": df_mean["throughput"]})

    sns.set(style="white")
    ax = sns.barplot(x="Version", y="throughput", data=df, color="#4878D0")

    # Compose values per 1000.
    for rec in ax.containers[0]:
        txt = str(round(rec.get_height(), -6))[:-8] + "M"
        ax.text(x=rec.get_x() + rec.get_width() / 2, y=rec.get_height()+.5,
                s=txt, ha="center")

    # Add info to plot.
    plt.title("Throughput per version", fontsize=16)
    plt.xlabel("Version", labelpad=0)
    plt.ylabel("Throughput (pixels/second)")
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt_ax = plt.gca()
    plt_ax.tick_params(axis="both", which="major", pad=0)

    # Compose ylabel per 1000.
    ylbls = ax.get_yticklabels()
    new_labels = []
    for ylbl in ylbls:
        new_labels.append(str(round(float(ylbl.get_text()), -6))[:-8] + "M")
    ax.set_yticklabels(new_labels)

    # Save and show plot.
    plt.savefig(f"figures/throughput/{results_folder}_throughput_{'-'.join(versions)}.png")
    plt.show()


if __name__ == "__main__":
    # Get results folder and versions from command line.
    args = sys.argv
    results_folder = args[1]
    versions = args[2:]

    # Check for existence of results folder.
    if not os.path.isdir(f"results/{results_folder}"):
        print(f"Given results folder '{results_folder}' does not exist..")
        exit(1)

    # Check for existence of all version results.
    for ver in versions:
        files = glob.glob(f"results/{results_folder}/{ver}_*")
        if len(files) == 0:
            print(f"Results for version '{ver}' do not exist..")
            exit(1)

    # Generate throughput plot with the given versions.
    gen_throughput()
