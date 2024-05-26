import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging

MAX_WORDS_PER_HEADER_LINE = 8
FIGURE_WIDTH = 10
FIGURE_HEIGHT_PER_PLOT = 0.5


def split_title(title: str, max_words_per_line: int = MAX_WORDS_PER_HEADER_LINE) -> str:
    """Split title into multiple lines if it exceeds the max number of words per line."""
    title_lines = title.split(" ")
    title_lines = [
        " ".join(title_lines[i : i + max_words_per_line])
        for i in range(0, len(title_lines), max_words_per_line)
    ]
    return "\n".join(title_lines)


def plot_scales_with_adjusted_ref_labels_spacing(
    df_all: pd.DataFrame, analysis_name: str, save_path_png: str, save_path_pdf: str
) -> None:
    """Plot scales with adjusted reference label spacing."""
    try:
        num_plots = len(df_all)
        if num_plots <= 0:
            raise ValueError("The number of plots must be greater than zero.")

        # Create a figure and a grid spec
        fig = plt.figure(figsize=(FIGURE_WIDTH, num_plots * FIGURE_HEIGHT_PER_PLOT))
        gs = plt.GridSpec(num_plots, 3, width_ratios=[1, 0.5, 4])

        for i, row in df_all.iterrows():
            ax_name = fig.add_subplot(gs[i, 0])
            ax_value = fig.add_subplot(gs[i, 1])
            ax = fig.add_subplot(gs[i, 2])

            value = row["Value"]
            ref_min = row["Ref_Min"]
            ref_max = row["Ref_Max"]
            unit = row["Unit"]

            if pd.isna(ref_min) and pd.isna(ref_max):
                ax.text(
                    0.5,
                    0.5,
                    "Референсные значения не определены",
                    fontsize=8,
                    verticalalignment="center",
                    horizontalalignment="center",
                    transform=ax.transAxes,
                )
            elif ref_min == 0.0 and ref_max == 0.0:
                ax.text(
                    0.5,
                    0.5,
                    "Не обнаружено",
                    fontsize=8,
                    verticalalignment="center",
                    horizontalalignment="center",
                    transform=ax.transAxes,
                )
            else:
                scale_min = min(
                    ref_min - 0.2 * (ref_max - ref_min),
                    value - 0.2 * abs(value - ref_min),
                )
                scale_max = max(
                    ref_max + 0.2 * (ref_max - ref_min),
                    value + 0.2 * abs(value - ref_max),
                )

                gradient = np.zeros((1, 500, 3))
                gradient[0, 0:100, 0] = np.linspace(0.5, 0, 100)
                gradient[0, 0:100, 1] = 0
                gradient[0, 0:100, 2] = np.linspace(1, 1, 100)

                gradient[0, 100:200, 0] = 0
                gradient[0, 100:200, 1] = np.linspace(0, 1, 100)
                gradient[0, 100:200, 2] = 1

                gradient[0, 200:300, 0] = 0
                gradient[0, 200:300, 1] = 1
                gradient[0, 200:300, 2] = np.linspace(1, 0, 100)

                gradient[0, 300:400, 0] = np.linspace(0, 1, 100)
                gradient[0, 300:400, 1] = 1
                gradient[0, 300:400, 2] = 0

                gradient[0, 400:500, 0] = 1
                gradient[0, 400:500, 1] = np.linspace(1, 0, 100)
                gradient[0, 400:500, 2] = 0

                ax.imshow(
                    gradient,
                    aspect="auto",
                    extent=[scale_min, scale_max, 0, 1.5],
                    interpolation="bilinear",
                )
                ax.axvline(ref_min, color="black", linestyle="-", lw=2)
                ax.axvline(ref_max, color="black", linestyle="-", lw=2)

                ax.plot(
                    value,
                    3.2,
                    marker="v",
                    color="black",
                    markersize=12,
                    linestyle="None",
                )

                ax.set_xlim(scale_min, scale_max)
                ax.set_ylim(0, 3)

                ax.plot(
                    [ref_min, ref_min], [0, 1.5], color="black", linestyle="-", lw=2
                )
                ax.plot(
                    [ref_max, ref_max], [0, 1.5], color="black", linestyle="-", lw=2
                )

                ax.text(
                    ref_min,
                    -0.5,
                    f"{ref_min}",
                    fontsize=10,
                    verticalalignment="top",
                    horizontalalignment="center",
                    color="black",
                )
                ax.text(
                    ref_max,
                    -0.5,
                    f"{ref_max}",
                    fontsize=10,
                    verticalalignment="top",
                    horizontalalignment="center",
                    color="black",
                )

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.set_xticks([])
            ax.set_yticks([])

            ax_name.text(
                0.1,
                0.3,
                row["Name"],
                fontsize=8,
                verticalalignment="center",
                horizontalalignment="left",
            )
            ax_value.text(
                0.5,
                0.3,
                f"{value:.2f}",
                fontsize=10,
                verticalalignment="center",
                horizontalalignment="left",
            )
            if unit:
                ax_value.text(
                    1.5,
                    0.3,
                    f"{unit}",
                    fontsize=8,
                    verticalalignment="center",
                    horizontalalignment="left",
                )

            ax_name.axis("off")
            ax_value.axis("off")

        title_multiline = split_title(analysis_name)
        fig.suptitle(title_multiline, fontsize=16, y=0.98, va="center")
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        plt.savefig(save_path_png)
        plt.savefig(save_path_pdf)
        logging.info(f"Plots saved as {save_path_png} and {save_path_pdf}")
    except Exception:
        logging.error("An error occurred while plotting.", exc_info=True)
        raise
