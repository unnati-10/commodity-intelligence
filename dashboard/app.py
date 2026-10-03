import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GoldLens | MCX Gold Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "processed"

RESEARCH_FILE = DATA_DIR / "final_relative_value_research_dataset.csv"
RESULTS_FILE = DATA_DIR / "final_project_results.csv"

# ============================================================
# LOGO
# ============================================================
# Put your logo image inside the dashboard folder.
# Change ONLY this filename if your image has a different name.
LOGO_FILENAME = "goldlens_logo.png"
LOGO_FILE = BASE_DIR / "dashboard" / LOGO_FILENAME


# ============================================================
# DISPLAY MODE
# ============================================================

if "goldlens_light_mode" not in st.session_state:
    st.session_state.goldlens_light_mode = False


# ============================================================
# COLORS
# ============================================================

if st.session_state.goldlens_light_mode:

    BG = "#F4F8FC"
    BG2 = "#EAF1F8"
    CARD = "#FFFFFF"
    ELEVATED = "#F1F6FA"
    BORDER = "#C9D9E8"

    BLUE = "#1683C7"
    LIGHT_BLUE = "#3EA7E3"

    TEXT = "#10263B"
    SECONDARY = "#587188"

    GREEN = "#168A62"
    YELLOW = "#B47A00"
    RED = "#D64555"

else:

    BG = "#07111F"
    BG2 = "#0B1728"
    CARD = "#102238"
    ELEVATED = "#142A42"
    BORDER = "#1E3A56"

    BLUE = "#6EC6FF"
    LIGHT_BLUE = "#8DD5FF"

    TEXT = "#F2F7FC"
    SECONDARY = "#8FA7BC"

    GREEN = "#54D6A0"
    YELLOW = "#FFD166"
    RED = "#FF6B7A"


# ============================================================
# NATIVE STREAMLIT THEME CSS ONLY
# ============================================================

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {BG};
        }}

        [data-testid="stSidebar"] {{
            background-color: {BG2};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3 {{
            color: {TEXT} !important;
        }}

        p {{
            color: {SECONDARY};
        }}

        div[data-testid="stMetric"] {{
            background-color: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 15px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {SECONDARY} !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {TEXT} !important;
        }}

        .stSelectbox label,
        .stMultiSelect label,
        .stRadio label {{
            color: {TEXT} !important;
        }}

        hr {{
            border-color: {BORDER};
        }}

        .stButton button {{
            border-radius: 8px;
        }}

        /* GoldLens header */
        .goldlens-header {{
            width: 100%;
            display: flex;
            align-items: center;
            margin-bottom: 0.15rem;
        }}

        .goldlens-logo {{
            max-height: 58px;
            width: auto;
            object-fit: contain;
        }}

        .goldlens-mark {{
            color: #D9A441;
            font-size: 21px;
            line-height: 1;
            font-weight: 700;
        }}

        .goldlens-title {{
            color: #F2F7FC;
            font-size: 2.25rem;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}

        /* Command icon stays on the far right */
        div[data-testid="stPopover"] > button {{
            width: 34px !important;
            height: 34px !important;
            min-height: 34px !important;
            padding: 0 !important;
            border: 1px solid {BORDER} !important;
            background: {CARD} !important;
            color: {BLUE} !important;
            border-radius: 8px !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stPopover"] > button:hover {{
            border-color: {BLUE} !important;
            color: {TEXT} !important;
            background: {ELEVATED} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    research_df = None
    results_df = None

    if RESEARCH_FILE.exists():
        research_df = pd.read_csv(RESEARCH_FILE)

    if RESULTS_FILE.exists():
        results_df = pd.read_csv(RESULTS_FILE)

    return research_df, results_df


research_df, results_df = load_data()


# ============================================================
# CHECK FILE
# ============================================================

if research_df is None:

    st.error("Research dataset was not found.")

    st.write("Expected file:")

    st.code(
        str(RESEARCH_FILE),
        language="text"
    )

    st.stop()


# ============================================================
# DATE CLEANING
# ============================================================

research_df["Date"] = pd.to_datetime(
    research_df["Date"],
    errors="coerce"
)

research_df["Expiry Date Parsed"] = pd.to_datetime(
    research_df["Expiry Date Parsed"],
    errors="coerce"
)


# ============================================================
# PAIR CONFIG
# ============================================================

PAIR_CONFIG = {

    "GOLDTEN / GOLDGUINEA": {
        "spread": "TEN_vs_GUINEA",
        "spread_pct": "TEN_vs_GUINEA_%",
        "z": "TEN_vs_GUINEA_Z_ZScore",
        "signal": "TEN_vs_GUINEA_Signal",
        "price_a": "GOLDTEN",
        "price_b": "GOLDGUINEA",
    },

    "GOLDTEN / GOLDPETAL": {
        "spread": "TEN_vs_PETAL",
        "spread_pct": "TEN_vs_PETAL_%",
        "z": "TEN_vs_PETAL_Z_ZScore",
        "signal": "TEN_vs_PETAL_Signal",
        "price_a": "GOLDTEN",
        "price_b": "GOLDPETAL",
    },

    "GOLDGUINEA / GOLDPETAL": {
        "spread": "GUINEA_vs_PETAL",
        "spread_pct": "GUINEA_vs_PETAL_%",
        "z": "GUINEA_vs_PETAL_Z_ZScore",
        "signal": "GUINEA_vs_PETAL_Signal",
        "price_a": "GOLDGUINEA",
        "price_b": "GOLDPETAL",
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def number(value, decimals=3):

    value = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(value):
        return "—"

    return f"{value:.{decimals}f}"


def percentage(value, decimals=3):

    value = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(value):
        return "—"

    return f"{value:.{decimals}f}%"


def signal_color(signal):

    signal = str(signal).upper()

    if "EXTREME" in signal:
        return RED

    if "UNUSUAL" in signal:
        return YELLOW

    if "NORMAL" in signal:
        return GREEN

    return SECONDARY


def make_chart(
    df,
    x,
    y,
    title,
    y_title,
    zero_line=False
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="lines+markers",
            name=y_title,
            line=dict(
                color=BLUE,
                width=2.5
            ),
            marker=dict(
                size=6
            )
        )
    )

    if zero_line:

        fig.add_hline(
            y=0,
            line_dash="dot",
            line_color=SECONDARY,
            opacity=0.7
        )

    fig.update_layout(

        title=dict(
            text=title,
            font=dict(
                color=TEXT,
                size=17
            )
        ),

        paper_bgcolor=BG,

        plot_bgcolor=BG2,

        font=dict(
            color=SECONDARY
        ),

        margin=dict(
            l=45,
            r=20,
            t=55,
            b=45
        ),

        xaxis=dict(
            title="Date",
            gridcolor=BORDER
        ),

        yaxis=dict(
            title=y_title,
            gridcolor=BORDER
        ),

        hovermode="x unified",

        legend=dict(
            font=dict(
                color=SECONDARY
            )
        )
    )

    return fig


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("GOLDLENS")

    st.caption(
        "MCX GOLD INTELLIGENCE"
    )

    st.divider()

    page = st.radio(
        "Navigate",
        [
            "Market Overview",
            "Contract Explorer",
            "Signal Monitor",
            "Validation",
            "Methodology"
        ]
    )

    st.divider()

    st.caption(
        "Historical relative-pricing research"
    )

    st.caption(
        "Normalize → Align → Detect → Validate"
    )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_spacer, header_right = st.columns([3, 6, 1])

with header_left:

    if LOGO_FILE.exists():

        st.image(
            str(LOGO_FILE),
            width=185
        )

    else:

        st.markdown(
            """
            <div class="goldlens-header">
                <div>
                    <span class="goldlens-mark">◈</span>
                    <span class="goldlens-title">GoldLens</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with header_right:

    with st.popover("⌘", help="GoldLens Command Center"):

        st.markdown("### Command Center")
        st.caption("GoldLens application controls")

        st.divider()

        st.write("**Appearance**")

        display_mode = st.radio(
            "Mode",
            ["Dark", "Light"],
            horizontal=True,
            key="goldlens_display_mode"
        )

        if display_mode == "Light":
            st.info("Light mode selected. Full chart colors remain optimized for the research terminal.")
        else:
            st.caption("Dark terminal mode is active.")

        st.divider()

        st.write("**Application**")

        if st.button("↻ Restart / Refresh", key="restart_goldlens"):
            st.cache_data.clear()
            st.rerun()

        if st.button("⌕ Reset View", key="reset_goldlens_view"):
            st.session_state.clear()
            st.rerun()

        st.divider()

        st.write("**Research Environment**")
        st.caption("Historical MCX gold relative-pricing analysis")

        st.write("**Pipeline**")
        st.caption("Normalize → Align → Detect → Validate")

        st.divider()

        st.caption("GoldLens • Research Interface")

st.caption(
    "See the spread. Understand the signal."
)


# ============================================================
# MARKET OVERVIEW
# ============================================================

if page == "Market Overview":

    st.header("Market Overview")

    dates = research_df["Date"].dropna()

    if not dates.empty:

        start_date = dates.min()
        end_date = dates.max()

    else:

        start_date = None
        end_date = None


    # --------------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------------

    total_observations = len(research_df)

    total_pairs = 3

    total_extreme = 0
    total_unusual = 0

    for config in PAIR_CONFIG.values():

        signal_column = config["signal"]

        if signal_column in research_df.columns:

            signals = (
                research_df[signal_column]
                .astype(str)
                .str.upper()
            )

            total_extreme += signals.str.contains(
                "EXTREME",
                na=False
            ).sum()

            total_unusual += signals.str.contains(
                "UNUSUAL",
                na=False
            ).sum()


    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Observations",
            f"{total_observations:,}"
        )

    with col2:

        st.metric(
            "Pairs",
            total_pairs
        )

    with col3:

        st.metric(
            "Extreme Signals",
            f"{total_extreme:,}"
        )

    with col4:

        st.metric(
            "Unusual Signals",
            f"{total_unusual:,}"
        )


    st.divider()


    # --------------------------------------------------------
    # PERIOD
    # --------------------------------------------------------

    if start_date is not None:

        st.subheader("Research Period")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Start",
                start_date.strftime("%d %b %Y")
            )

        with c2:

            st.metric(
                "End",
                end_date.strftime("%d %b %Y")
            )


    st.divider()


    # --------------------------------------------------------
    # PAIR SUMMARY
    # --------------------------------------------------------

    st.subheader("Relative Pricing Pairs")

    pair_summary = []

    for pair_name, config in PAIR_CONFIG.items():

        signals = (
            research_df[config["signal"]]
            .astype(str)
            .str.upper()
        )

        extreme = signals.str.contains(
            "EXTREME",
            na=False
        ).sum()

        unusual = signals.str.contains(
            "UNUSUAL",
            na=False
        ).sum()

        pair_summary.append(
            {
                "Contract Pair": pair_name,
                "Observations": len(research_df),
                "Extreme": int(extreme),
                "Unusual": int(unusual),
            }
        )

    pair_summary_df = pd.DataFrame(
        pair_summary
    )

    st.dataframe(
        pair_summary_df,
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    st.subheader("How GoldLens Works")

    a, b, c, d = st.columns(4)

    with a:

        st.markdown("### 01")

        st.write("**Normalize**")

        st.caption(
            "Convert contract prices into a comparable "
            "pure-gold price."
        )

    with b:

        st.markdown("### 02")

        st.write("**Align**")

        st.caption(
            "Compare contracts using aligned expiry dates."
        )

    with c:

        st.markdown("### 03")

        st.write("**Detect**")

        st.caption(
            "Measure spreads and identify unusual "
            "historical observations."
        )

    with d:

        st.markdown("### 04")

        st.write("**Validate**")

        st.caption(
            "Evaluate the signal framework using "
            "walk-forward validation."
        )


# ============================================================
# CONTRACT EXPLORER
# ============================================================

elif page == "Contract Explorer":

    st.header("Contract Explorer")

    st.caption(
        "Detailed historical view of one selected contract pair."
    )


    # --------------------------------------------------------
    # PAIR
    # --------------------------------------------------------

    selected_pair = st.selectbox(
        "Select Contract Pair",
        list(PAIR_CONFIG.keys())
    )

    config = PAIR_CONFIG[selected_pair]


    # --------------------------------------------------------
    # EXPIRY
    # --------------------------------------------------------

    expiry_values = (
        research_df["Expiry Date Parsed"]
        .dropna()
        .sort_values()
        .unique()
    )

    if len(expiry_values) == 0:

        st.warning(
            "No expiry dates are available."
        )

        st.stop()


    expiry_options = [
        pd.Timestamp(x)
        for x in expiry_values
    ]


    selected_expiry = st.selectbox(
        "Select Exact Expiry",
        expiry_options,
        format_func=lambda x:
            x.strftime("%d %b %Y")
    )


    expiry_df = research_df[
        research_df["Expiry Date Parsed"]
        == selected_expiry
    ].copy()


    if expiry_df.empty:

        st.warning(
            "No data found for this expiry."
        )

        st.stop()


    # --------------------------------------------------------
    # OBSERVATION DATE
    # --------------------------------------------------------

    observation_dates = (
        expiry_df["Date"]
        .dropna()
        .sort_values()
        .unique()
    )


    selected_date = st.selectbox(
        "Select Observation Date",
        [
            pd.Timestamp(x)
            for x in observation_dates
        ],
        index=len(observation_dates) - 1,
        format_func=lambda x:
            x.strftime("%d %b %Y")
    )


    current_rows = expiry_df[
        expiry_df["Date"]
        == selected_date
    ].copy()


    if current_rows.empty:

        st.warning(
            "No observation found."
        )

        st.stop()


    current = current_rows.iloc[0]


    # ========================================================
    # CURRENT OBSERVATION
    # ========================================================

    st.divider()

    st.header("Current Observation")

    st.caption(
        f"{selected_pair} • "
        f"Expiry {selected_expiry.strftime('%d %b %Y')} • "
        f"Observation {selected_date.strftime('%d %b %Y')}"
    )


    spread_value = pd.to_numeric(
        current.get(config["spread"]),
        errors="coerce"
    )

    spread_pct = pd.to_numeric(
        current.get(config["spread_pct"]),
        errors="coerce"
    )

    z_value = pd.to_numeric(
        current.get(config["z"]),
        errors="coerce"
    )

    signal = str(
        current.get(
            config["signal"],
            "UNKNOWN"
        )
    )

    liquidity = str(
        current.get(
            "Liquidity_Class",
            "UNKNOWN"
        )
    )


    # --------------------------------------------------------
    # BIG OBSERVATION CARDS
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Relative Spread",
            number(spread_value)
        )

        st.caption(
            "Percentage difference: "
            + percentage(spread_pct)
        )

    with c2:

        st.metric(
            "Rolling Z-Score",
            number(z_value)
        )

        st.caption(
            "Distance from rolling historical mean"
        )


    c3, c4 = st.columns(2)

    with c3:

        st.metric(
            "Signal Status",
            signal
        )

        st.caption(
            "Historical classification"
        )

    with c4:

        st.metric(
            "Liquidity Class",
            liquidity
        )

        st.caption(
            "Based on pair-level minimum activity"
        )


    # --------------------------------------------------------
    # SIGNAL INTERPRETATION
    # --------------------------------------------------------

    st.write("")

    signal_upper = signal.upper()

    if "EXTREME" in signal_upper:

        st.error(
            "EXTREME DISLOCATION\n\n"
            "The observed relative spread reached an extreme "
            "level under the project's rolling z-score framework."
        )

    elif "UNUSUAL" in signal_upper:

        st.warning(
            "UNUSUAL DISLOCATION\n\n"
            "The observed relative spread moved into an unusual "
            "historical range under the project's signal framework."
        )

    elif "NORMAL" in signal_upper:

        st.success(
            "NORMAL\n\n"
            "The relative spread remained within the project's "
            "normal historical range."
        )

    else:

        st.info(
            "INSUFFICIENT HISTORY\n\n"
            "There is not enough rolling history to classify "
            "this observation."
        )


    # ========================================================
    # NORMALIZED PRICES
    # ========================================================

    st.divider()

    st.subheader("Normalized Contract Prices")

    chart_df = expiry_df.sort_values(
        "Date"
    ).copy()


    fig_price = go.Figure()


    fig_price.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df[config["price_a"]],
            mode="lines+markers",
            name=config["price_a"],
            line=dict(
                color=BLUE,
                width=2.5
            ),
            marker=dict(size=6)
        )
    )


    fig_price.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df[config["price_b"]],
            mode="lines+markers",
            name=config["price_b"],
            line=dict(
                color=LIGHT_BLUE,
                width=2.5
            ),
            marker=dict(size=6)
        )
    )


    fig_price.update_layout(

        paper_bgcolor=BG,

        plot_bgcolor=BG2,

        font=dict(
            color=SECONDARY
        ),

        margin=dict(
            l=45,
            r=20,
            t=30,
            b=45
        ),

        xaxis=dict(
            title="Observation Date",
            gridcolor=BORDER
        ),

        yaxis=dict(
            title="Normalized Pure Gold Price",
            gridcolor=BORDER
        ),

        hovermode="x unified"
    )


    st.plotly_chart(
        fig_price,
        use_container_width=True
    )


    # ========================================================
    # SPREAD + Z SCORE
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        fig_spread = make_chart(
            chart_df,
            "Date",
            config["spread"],
            "Relative Spread",
            "Spread",
            zero_line=True
        )

        st.plotly_chart(
            fig_spread,
            use_container_width=True
        )


    with c2:

        fig_z = make_chart(
            chart_df,
            "Date",
            config["z"],
            "Rolling Z-Score",
            "Z-Score",
            zero_line=True
        )

        fig_z.add_hline(
            y=2,
            line_dash="dash",
            line_color=YELLOW,
            opacity=0.6
        )

        fig_z.add_hline(
            y=-2,
            line_dash="dash",
            line_color=YELLOW,
            opacity=0.6
        )

        fig_z.add_hline(
            y=3,
            line_dash="dash",
            line_color=RED,
            opacity=0.6
        )

        fig_z.add_hline(
            y=-3,
            line_dash="dash",
            line_color=RED,
            opacity=0.6
        )

        st.plotly_chart(
            fig_z,
            use_container_width=True
        )


    # ========================================================
    # OBSERVATION DETAILS
    # ========================================================

    st.divider()

    st.subheader("Observation Details")


    price_a = pd.to_numeric(
        current.get(config["price_a"]),
        errors="coerce"
    )

    price_b = pd.to_numeric(
        current.get(config["price_b"]),
        errors="coerce"
    )

    min_volume = pd.to_numeric(
        current.get("Minimum_Volume"),
        errors="coerce"
    )

    min_oi = pd.to_numeric(
        current.get("Minimum_OI"),
        errors="coerce"
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            config["price_a"],
            number(price_a)
        )


    with c2:

        st.metric(
            config["price_b"],
            number(price_b)
        )


    with c3:

        st.metric(
            "Minimum Volume",
            number(min_volume, 0)
        )


    with c4:

        st.metric(
            "Minimum OI",
            number(min_oi, 0)
        )


    # ========================================================
    # COST SENSITIVITY
    # ========================================================

    st.divider()

    st.header("Cost Sensitivity")

    st.caption(
        "Hypothetical research-cost analysis from the "
        "walk-forward validation results."
    )


    if results_df is None or results_df.empty:

        st.info(
            "Cost sensitivity cannot be displayed because "
            "final_project_results.csv is missing."
        )

    else:

        cost_pair_map = {

            "GOLDTEN / GOLDGUINEA":
                "TEN_vs_GUINEA",

            "GOLDTEN / GOLDPETAL":
                "TEN_vs_PETAL",

            "GOLDGUINEA / GOLDPETAL":
                "GUINEA_vs_PETAL"
        }


        result_pair = cost_pair_map[
            selected_pair
        ]


        matching_rows = results_df[
            results_df["Pair"]
            .astype(str)
            .str.strip()
            == result_pair
        ]


        if matching_rows.empty:

            st.info(
                "No validation cost results were found "
                "for this contract pair."
            )

        else:

            cost_row = matching_rows.iloc[0]


            value_005 = pd.to_numeric(
                cost_row.get(
                    "Validation_0.05_Cost_Mean_Net_Contraction",
                    np.nan
                ),
                errors="coerce"
            )


            value_010 = pd.to_numeric(
                cost_row.get(
                    "Validation_0.10_Cost_Mean_Net_Contraction",
                    np.nan
                ),
                errors="coerce"
            )


            if (
                pd.notna(value_005)
                and pd.notna(value_010)
            ):

                cost_change = (
                    value_010
                    - value_005
                )

            else:

                cost_change = np.nan


            # ------------------------------------------------
            # COST METRICS
            # ------------------------------------------------

            c1, c2, c3 = st.columns(3)


            with c1:

                st.metric(
                    "0.05% Cost",
                    percentage(value_005)
                )

                st.caption(
                    "Mean net contraction"
                )


            with c2:

                st.metric(
                    "0.10% Cost",
                    percentage(value_010)
                )

                st.caption(
                    "Mean net contraction"
                )


            with c3:

                if pd.notna(cost_change):

                    st.metric(
                        "Cost Impact",
                        f"{cost_change:+.3f}%"
                    )

                else:

                    st.metric(
                        "Cost Impact",
                        "—"
                    )

                st.caption(
                    "Change from 0.05% to 0.10%"
                )


            # ------------------------------------------------
            # COST CHART
            # ------------------------------------------------

            if (
                pd.notna(value_005)
                and pd.notna(value_010)
            ):

                cost_chart_df = pd.DataFrame(
                    {
                        "Cost Assumption": [
                            "0.05%",
                            "0.10%"
                        ],
                        "Net Contraction": [
                            value_005,
                            value_010
                        ]
                    }
                )


                fig_cost = go.Figure()


                fig_cost.add_trace(
                    go.Bar(
                        x=cost_chart_df[
                            "Cost Assumption"
                        ],

                        y=cost_chart_df[
                            "Net Contraction"
                        ],

                        text=[
                            f"{x:.3f}%"
                            for x in cost_chart_df[
                                "Net Contraction"
                            ]
                        ],

                        textposition="outside",

                        marker_color=BLUE
                    )
                )


                fig_cost.add_hline(
                    y=0,
                    line_dash="dot",
                    line_color=SECONDARY
                )


                fig_cost.update_layout(

                    title=dict(
                        text="Validation Cost Sensitivity",
                        font=dict(
                            color=TEXT,
                            size=17
                        )
                    ),

                    paper_bgcolor=BG,

                    plot_bgcolor=BG2,

                    font=dict(
                        color=SECONDARY
                    ),

                    margin=dict(
                        l=45,
                        r=20,
                        t=55,
                        b=45
                    ),

                    xaxis=dict(
                        title="Hypothetical Cost",
                        gridcolor=BORDER
                    ),

                    yaxis=dict(
                        title="Mean Net Contraction (%)",
                        gridcolor=BORDER
                    ),

                    showlegend=False
                )


                st.plotly_chart(
                    fig_cost,
                    use_container_width=True
                )


            st.info(
                "These cost levels are hypothetical research "
                "assumptions used for sensitivity analysis. "
                "They are not actual brokerage, tax, bid-ask "
                "or execution-cost estimates."
            )


# ============================================================
# SIGNAL MONITOR
# ============================================================

elif page == "Signal Monitor":

    st.header("Signal Monitor")

    st.caption(
        "Browse historical relative-pricing observations."
    )


    selected_pair = st.selectbox(
        "Select Contract Pair",
        list(PAIR_CONFIG.keys())
    )


    config = PAIR_CONFIG[
        selected_pair
    ]


    signal_options = [
        "NORMAL",
        "UNUSUAL DISLOCATION",
        "EXTREME DISLOCATION",
        "INSUFFICIENT HISTORY"
    ]


    selected_signals = st.multiselect(
        "Signal Filter",
        signal_options,
        default=signal_options
    )


    monitor_df = research_df[
        [
            "Date",
            "Expiry Date Parsed",
            config["spread"],
            config["spread_pct"],
            config["z"],
            config["signal"],
            "Liquidity_Class"
        ]
    ].copy()


    monitor_df = monitor_df.rename(
        columns={
            config["spread"]:
                "Relative Spread",

            config["spread_pct"]:
                "Spread %",

            config["z"]:
                "Z-Score",

            config["signal"]:
                "Signal",

            "Liquidity_Class":
                "Liquidity"
        }
    )


    if selected_signals:

        monitor_df = monitor_df[
            monitor_df["Signal"]
            .astype(str)
            .isin(selected_signals)
        ]


    monitor_df = monitor_df.sort_values(
        "Date",
        ascending=False
    )


    display_df = monitor_df.copy()


    display_df["Date"] = (
        display_df["Date"]
        .dt.strftime("%d %b %Y")
    )


    display_df["Expiry Date Parsed"] = (
        display_df["Expiry Date Parsed"]
        .dt.strftime("%d %b %Y")
    )


    st.write(
        f"Showing {len(display_df):,} observations."
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# VALIDATION
# ============================================================

elif page == "Validation":

    st.header("Validation")

    st.caption(
        "Walk-forward evaluation of the historical signal framework."
    )


    if results_df is None or results_df.empty:

        st.error(
            "final_project_results.csv was not found."
        )

        st.stop()


    st.subheader(
        "Pair-Level Validation Results"
    )


    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    st.subheader(
        "Validation Contraction Rate"
    )


    validation_chart = results_df.copy()


    fig = go.Figure()


    fig.add_trace(
        go.Bar(

            x=validation_chart["Pair"],

            y=validation_chart[
                "Validation_Contraction_Rate_%"
            ],

            text=[
                f"{x:.1f}%"
                for x in validation_chart[
                    "Validation_Contraction_Rate_%"
                ]
            ],

            textposition="outside",

            marker_color=BLUE
        )
    )


    fig.update_layout(

        paper_bgcolor=BG,

        plot_bgcolor=BG2,

        font=dict(
            color=SECONDARY
        ),

        margin=dict(
            l=45,
            r=20,
            t=30,
            b=70
        ),

        xaxis=dict(
            gridcolor=BORDER
        ),

        yaxis=dict(
            title="Validation Contraction Rate (%)",
            gridcolor=BORDER
        ),

        showlegend=False
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.divider()


    st.subheader(
        "Research Interpretation"
    )


    st.info(
        "The development period is used to establish the "
        "rolling historical framework, while later observations "
        "are evaluated as validation data. The available research "
        "period is short, so the results should be treated as "
        "exploratory historical analysis rather than evidence "
        "of persistent future behaviour."
    )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "Methodology":

    st.header("Methodology")

    st.caption(
        "The analytical pipeline behind GoldLens."
    )


    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    st.subheader(
        "01 — Normalize"
    )

    st.write(
        "Raw contract prices are converted into a comparable "
        "pure-gold price using quotation weight and purity."
    )


    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    st.subheader(
        "02 — Align"
    )

    st.write(
        "Contracts are compared using aligned expiry dates "
        "so that the relative-pricing comparison is meaningful."
    )


    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    st.subheader(
        "03 — Measure"
    )

    st.write(
        "Pairwise relative spreads and percentage differences "
        "are calculated between normalized contract prices."
    )


    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    st.subheader(
        "04 — Detect"
    )

    st.write(
        "Rolling z-scores are used to identify observations "
        "that are unusually far from recent historical behaviour."
    )


    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    st.subheader(
        "05 — Validate"
    )

    st.write(
        "Walk-forward development and validation periods "
        "are used to evaluate the historical signal framework."
    )


    st.divider()


    # --------------------------------------------------------
    # CONTRACT TABLE
    # --------------------------------------------------------

    st.subheader(
        "Contract Specifications"
    )


    contract_df = pd.DataFrame(
        {
            "Contract": [
                "GOLDM",
                "GOLDTEN",
                "GOLDGUINEA",
                "GOLDPETAL"
            ],

            "Quotation": [
                "₹ / 10 g",
                "₹ / 10 g",
                "₹ / 8 g",
                "₹ / 1 g"
            ],

            "Purity": [
                "995",
                "999",
                "999",
                "999"
            ]
        }
    )


    st.dataframe(
        contract_df,
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    # --------------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------------

    st.subheader(
        "Research Limitations"
    )


    st.write(
        "• The available dataset covers a limited historical period."
    )

    st.write(
        "• Historical signals do not guarantee future behaviour."
    )

    st.write(
        "• Volume is not the same as executable market depth."
    )

    st.write(
        "• Settlement or close prices are not automatically "
        "executable fill prices."
    )

    st.write(
        "• Cost assumptions are hypothetical research assumptions."
    )

    st.write(
        "• GoldLens is an analytical research interface, "
        "not a trading recommendation."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GOLDLENS • MCX Gold Relative Pricing Intelligence"
)

st.caption(
    "Historical research interface • Educational use"
)