import os
import platform
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"


def choose_font() -> FontProperties:
    env_font = os.environ.get("THUTHESIS_PLOT_FONT")
    candidates = []
    if env_font:
        candidates.append(env_font)

    system = platform.system()
    if system == "Windows":
        candidates.extend(
            [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
            ]
        )
    elif system == "Darwin":
        candidates.extend(
            [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
            ]
        )

    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.exists():
            return FontProperties(fname=str(path))

    for family in [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]:
        try:
            path = font_manager.findfont(FontProperties(family=family), fallback_to_default=False)
        except Exception:
            continue
        if path and Path(path).exists():
            return FontProperties(fname=path)

    return FontProperties()


FONT = choose_font()


plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = [FONT.get_name()]


COLORS = {
    "none": "#6B7280",
    "rule": "#B7791F",
    "prompt": "#2C7A7B",
    "llm": "#2B6CB0",
    "align": "#2F855A",
    "env": "#2C7A7B",
    "remap": "#C53030",
}

HATCHES = {
    "None": "",
    "Rule-Only": "///",
    "Prompt-Policy": "\\\\\\",
    "LLM-Only": "xx",
    "Decision-Align": "...",
    "环境诱导删除": "///",
    "目标重映射": "\\\\\\",
    "Qwen3.5-Plus": "///",
    "MiniMax-M2.5": "...",
}


def apply_style(ax, ylabel: str):
    ax.set_ylim(0, 110)
    ax.set_ylabel(ylabel, fontproperties=FONT, fontsize=9.5)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis="both", labelsize=8.5, length=3, color="#6B7280")
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8, linestyle="--", dashes=(3, 3))
    ax.set_axisbelow(True)
    ax.set_facecolor("#FBFBFA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#4B5563")
    ax.spines["bottom"].set_color("#4B5563")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(FONT)


def annotate_bars(ax, bars, values):
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            2.5 if value == 0 else min(value + 2.5, 105),
            f"{value:.1f}%" if value % 1 else f"{int(value)}%",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#111827",
            fontproperties=FONT,
        )


def save(fig, name: str):
    fig.tight_layout(pad=0.55)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def bar_chart(name, labels, values, colors, ylabel):
    fig, ax = plt.subplots(figsize=(5.9, 3.25))
    bars = ax.bar(
        labels,
        values,
        color=colors,
        width=0.54,
        edgecolor="#1F2937",
        linewidth=0.75,
    )
    for bar, label in zip(bars, labels):
        bar.set_hatch(HATCHES.get(label, ""))
    apply_style(ax, ylabel)
    annotate_bars(ax, bars, values)
    save(fig, name)


def grouped_bar_chart(name, groups, series, ylabel):
    fig, ax = plt.subplots(figsize=(6.0, 3.25))
    width = 0.28
    x = list(range(len(groups)))
    for i, item in enumerate(series):
        offset = (i - (len(series) - 1) / 2) * width
        xs = [v + offset for v in x]
        bars = ax.bar(
            xs,
            item["values"],
            width=width,
            label=item["name"],
            color=item["color"],
            edgecolor="#1F2937",
            linewidth=0.75,
        )
        for bar in bars:
            bar.set_hatch(HATCHES.get(item["name"], ""))
        annotate_bars(ax, bars, item["values"])
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontproperties=FONT)
    apply_style(ax, ylabel)
    ax.legend(
        prop=FONT,
        frameon=False,
        fontsize=9,
        loc="upper left",
        bbox_to_anchor=(0.0, 1.10),
        ncols=len(series),
        handlelength=1.2,
        columnspacing=1.5,
    )
    save(fig, name)


def main():
    bar_chart(
        "chap05-qwen-attack-residual",
        ["None", "Rule-Only", "Prompt-Policy", "LLM-Only", "Decision-Align"],
        [74.4, 52.9, 50.0, 17.6, 0.0],
        [COLORS["none"], COLORS["rule"], COLORS["prompt"], COLORS["llm"], COLORS["align"]],
        "攻击残留率（%）",
    )
    grouped_bar_chart(
        "chap05-qwen-type-residual",
        ["Rule-Only", "Prompt-Policy", "LLM-Only", "Decision-Align"],
        [
            {"name": "环境诱导删除", "values": [0, 10, 0, 0], "color": COLORS["env"]},
            {"name": "目标重映射", "values": [75, 66.7, 25, 0], "color": COLORS["remap"]},
        ],
        "攻击残留率（%）",
    )
    bar_chart(
        "chap05-qwen-benign-intervention",
        ["Rule-Only", "LLM-Only", "Decision-Align"],
        [0.0, 5.9, 14.7],
        [COLORS["rule"], COLORS["llm"], COLORS["align"]],
        "显式干预率（%）",
    )
    bar_chart(
        "chap05-minimax-attack-residual",
        ["None", "Rule-Only", "Prompt-Policy", "LLM-Only", "Decision-Align"],
        [76.5, 52.9, 52.9, 35.3, 0.0],
        [COLORS["none"], COLORS["rule"], COLORS["prompt"], COLORS["llm"], COLORS["align"]],
        "攻击残留率（%）",
    )
    grouped_bar_chart(
        "chap05-simulated-detection-success",
        ["Aligned", "Ambiguous", "Misaligned", "Drift"],
        [
            {"name": "Qwen3.5-Plus", "values": [97, 25, 100, 100], "color": COLORS["llm"]},
            {"name": "MiniMax-M2.5", "values": [88, 10, 100, 100], "color": COLORS["align"]},
        ],
        "检测成功率（%）",
    )


if __name__ == "__main__":
    main()
