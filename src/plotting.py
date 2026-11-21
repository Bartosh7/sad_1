from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns

COUNTRY_ORDER = ["Polska", "Finlandia", "Francja"]

PALETTE = {
    "Polska": "#D55E00",
    "Francja": "#0072B2",
    "Finlandia": "#009E73",
}

MARKERS = {
    "Polska": "o",
    "Francja": "s",
    "Finlandia": "^",
}


def set_plot_style():
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)


def _save_figure(fig, save_path: Path | str | None):
    if save_path is None:
        return
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")


def plot_trend(
    df,
    title: str,
    ylabel: str,
    ylim: tuple[float, float] | None = None,
    ref_line: float | None = None,
    ref_label: str | None = None,
    ref_text_pos: tuple[float, float] | None = None,
    highlight_period: tuple[float, float] | None = (2020, 2022),
    highlight_label: str = "Okres 2020–2022 (COVID-19)",
    annotate_last: bool = True,
    save_path: Path | str | None = None,
):
    fig, ax = plt.subplots(figsize=(10, 5.5))

    if highlight_period is not None:
        ax.axvspan(
            highlight_period[0],
            highlight_period[1],
            color="gray",
            alpha=0.12,
            label=highlight_label,
        )

    if ref_line is not None:
        ax.axhline(ref_line, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
        if ref_label:
            x_pos, y_pos = ref_text_pos if ref_text_pos else (df["year"].min() - 0.2, ref_line - 1.2)
            ax.text(
                x_pos,
                y_pos,
                ref_label,
                fontsize=8.5,
                color="black",
                alpha=0.8,
                ha="left",
                va="top",
            )

    sns.lineplot(
        data=df,
        x="year",
        y="value",
        hue="country",
        hue_order=COUNTRY_ORDER,
        style="country",
        style_order=COUNTRY_ORDER,
        palette=PALETTE,
        markers=MARKERS,
        dashes=False,
        markersize=7,
        linewidth=2.2,
        ax=ax,
    )

    years = sorted(df["year"].unique())
    if annotate_last:
        last_year = max(years)
        for _, row in df[df["year"] == last_year].iterrows():
            ax.annotate(
                f"{row['value']:.1f}",
                xy=(row["year"], row["value"]),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=PALETTE.get(row["country"], "black"),
            )
        ax.set_xlim(min(years) - 0.4, max(years) + 1.1)

    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel("Rok")
    ax.set_ylabel(ylabel)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)

    if ylim is not None:
        ax.set_ylim(*ylim)

    legend_title = "Kraj / Okres" if highlight_period is not None else "Kraj"
    ax.legend(title=legend_title, frameon=True)
    sns.despine()
    plt.tight_layout()

    _save_figure(fig, save_path)
    return fig, ax


def plot_distribution(
    df,
    title: str,
    ylabel: str,
    ylim: tuple[float, float] | None = None,
    ref_line: float | None = None,
    ref_label: str = "Punkt odniesienia",
    legend_loc: str = "lower right",
    save_path: Path | str | None = None,
):
    fig, ax = plt.subplots(figsize=(10, 5.5))

    if ref_line is not None:
        ax.axhline(ref_line, color="#333333", linestyle="-.", linewidth=1.3, alpha=0.85, zorder=1)

    sns.boxplot(
        data=df,
        x="country",
        y="value",
        order=COUNTRY_ORDER,
        hue="country",
        hue_order=COUNTRY_ORDER,
        palette=PALETTE,
        width=0.45,
        legend=False,
        boxprops={"alpha": 0.35},
        showfliers=False,
        showmeans=True,
        meanline=True,
        meanprops={"linestyle": "--", "color": "#222222", "linewidth": 1.6, "zorder": 5},
        medianprops={"linestyle": "-", "color": "#222222", "linewidth": 1.8, "zorder": 5},
        ax=ax,
    )

    sns.stripplot(
        data=df,
        x="country",
        y="value",
        order=COUNTRY_ORDER,
        hue="country",
        hue_order=COUNTRY_ORDER,
        palette=PALETTE,
        size=6.5,
        jitter=0.08,
        edgecolor="white",
        linewidth=0.8,
        legend=False,
        ax=ax,
    )

    legend_handles = [
        Line2D([0], [0], color="#222222", linestyle="-", linewidth=1.8, label="Mediana"),
        Line2D([0], [0], color="#222222", linestyle="--", linewidth=1.8, label="Średnia"),
    ]
    if ref_line is not None:
        legend_handles.append(
            Line2D([0], [0], color="#333333", linestyle="-.", linewidth=1.3, label=ref_label)
        )

    ax.legend(handles=legend_handles, frameon=True, loc=legend_loc)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)

    if ylim is not None:
        ax.set_ylim(*ylim)

    sns.despine()
    plt.tight_layout()

    _save_figure(fig, save_path)
    return fig, ax


def plot_yoy_changes(
    df,
    title: str,
    ylabel: str = "Zmiana rok do roku",
    highlight_period: tuple[float, float] | None = (2019.5, 2022.5),
    highlight_label: str = "Okres 2020–2022 (COVID-19)",
    label_threshold: float = 0.0,
    save_path: Path | str | None = None,
):
    df_yoy = df.sort_values(["country", "year"]).copy()
    df_yoy["yoy_diff"] = df_yoy.groupby("country")["value"].diff()
    df_yoy = df_yoy.dropna(subset=["yoy_diff"])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)

    for ax, country in zip(axes, COUNTRY_ORDER):
        sub = df_yoy[df_yoy["country"] == country]
        color = PALETTE[country]

        if highlight_period is not None:
            ax.axvspan(
                highlight_period[0],
                highlight_period[1],
                color="gray",
                alpha=0.14,
                zorder=1,
                label=highlight_label,
            )

        ax.axhline(0, color="#222222", linewidth=1.1, zorder=2)

        bars = ax.bar(
            sub["year"],
            sub["yoy_diff"],
            color=color,
            alpha=0.85,
            width=0.68,
            edgecolor="white",
            linewidth=0.5,
            zorder=3,
        )

        for bar, val in zip(bars, sub["yoy_diff"]):
            if abs(val) >= label_threshold:
                xytext = (0, 3) if val >= 0 else (0, -4)
                va = "bottom" if val >= 0 else "top"
                ax.annotate(
                    f"{val:+.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, val),
                    xytext=xytext,
                    textcoords="offset points",
                    ha="center",
                    va=va,
                    fontsize=6.5,
                    fontweight="bold",
                    color=color,
                )

        ax.set_title(country, fontweight="bold", color=color, pad=10)
        ax.set_xlabel("Rok")

        years = sorted(sub["year"].unique())
        ax.set_xticks(years[::2])
        ax.tick_params(axis="x", rotation=45)
        sns.despine(ax=ax)

    axes[0].set_ylabel(ylabel)

    ymin, ymax = axes[0].get_ylim()
    margin = (ymax - ymin) * 0.12
    axes[0].set_ylim(ymin - margin, ymax + margin)

    if title:
        fig.suptitle(title, fontweight="bold", y=1.05)

    if highlight_period is not None:
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.96),
            frameon=False,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.93])
    else:
        plt.tight_layout()

    _save_figure(fig, save_path)
    return fig, axes