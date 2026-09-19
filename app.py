import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # used only for the World Map choropleth


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Global Defence Dashboard",
    page_icon="🌍",
    layout="wide"
)

sns.set_theme(style="whitegrid")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("global_firepower_2026_core.csv")

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Remove duplicate rows
    df = df.drop_duplicates()

    return df


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 Global Defence Dashboard")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📑 Navigation",
    [
        "🏠 Overview",
        "✈️ Air Power",
        "🪖 Land Power",
        "⚓ Naval Power",
        "💰 Defence Spending",
        "🌍 World Map",
        "📊 Data Explorer"
    ]
)

st.sidebar.markdown("---")


# ============================================================
# COUNTRY FILTER
# ============================================================

if "country" in df.columns:

    countries = sorted(
        df["country"].dropna().unique().tolist()
    )

    selected_countries = st.sidebar.multiselect(
        "🌎 Select Countries",
        countries,
        default=[]
    )

else:
    selected_countries = []


# Top N
top_n = st.sidebar.slider(
    "Top N Countries",
    min_value=5,
    max_value=30,
    value=10
)


# ============================================================
# FILTER DATA
# ============================================================

if selected_countries:

    filtered_df = df[
        df["country"].isin(selected_countries)
    ].copy()

else:

    filtered_df = df.copy()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def numeric_value(dataframe, column):

    if column in dataframe.columns:

        return pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

    return pd.Series(
        [0] * len(dataframe),
        index=dataframe.index
    )


def bar_chart(data, x_col, y_col, title, horizontal=False,
              xlabel=None, ylabel=None, palette="viridis"):
    """Render a seaborn bar chart inside Streamlit."""

    fig, ax = plt.subplots(figsize=(10, 5))

    if horizontal:
        sns.barplot(
            data=data, x=y_col, y=x_col,
            hue=x_col, palette=palette, legend=False, ax=ax
        )
    else:
        sns.barplot(
            data=data, x=x_col, y=y_col,
            hue=x_col, palette=palette, legend=False, ax=ax
        )
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    ax.set_title(title)
    ax.set_xlabel(xlabel if xlabel else (y_col if horizontal else x_col))
    ax.set_ylabel(ylabel if ylabel else (x_col if horizontal else y_col))

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def scatter_chart(data, x_col, y_col, title, size_col=None,
                   hue_col="country", xlabel=None, ylabel=None):
    """Render a seaborn scatter chart inside Streamlit."""

    fig, ax = plt.subplots(figsize=(10, 6))

    scatter_kwargs = dict(
        data=data, x=x_col, y=y_col,
        hue=hue_col, ax=ax, legend=False
    )

    if size_col is not None:
        scatter_kwargs["size"] = size_col
        scatter_kwargs["sizes"] = (20, 400)

    sns.scatterplot(**scatter_kwargs)

    ax.set_title(title)
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def pie_chart(labels, values, title):
    """Render a matplotlib pie chart inside Streamlit."""

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=sns.color_palette("viridis", len(values))
    )
    ax.set_title(title)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def stacked_bar_chart(data, x_col, y_cols, title):
    """Render a stacked bar chart using matplotlib."""

    fig, ax = plt.subplots(figsize=(10, 6))

    bottom = pd.Series([0] * len(data), index=data.index)
    colors = sns.color_palette("viridis", len(y_cols))

    for col, color in zip(y_cols, colors):
        ax.bar(data[x_col], data[col], bottom=bottom, label=col, color=color)
        bottom = bottom + data[col]

    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel("Count")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.title("🌍 Global Defence Dashboard")

    st.markdown(
        """
        ### Global Military Power Analysis

        This dashboard provides a data-driven analysis of
        military power, personnel, defence spending, air power,
        land power and naval capabilities across countries.
        """
    )

    st.markdown("---")

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌎 Countries", len(filtered_df))

    if "Defense_Budget_USD_Billion" in filtered_df.columns:
        budget = numeric_value(filtered_df, "Defense_Budget_USD_Billion").sum()
        col2.metric("💰 Defence Budget", f"${budget:,.2f} B")
    else:
        col2.metric("💰 Defence Budget", "N/A")

    if "Active_Personnel" in filtered_df.columns:
        personnel = numeric_value(filtered_df, "Active_Personnel").sum()
        col3.metric("👥 Active Personnel", f"{personnel:,.0f}")
    else:
        col3.metric("👥 Active Personnel", "N/A")

    if "Total_Aircraft" in filtered_df.columns:
        aircraft = numeric_value(filtered_df, "Total_Aircraft").sum()
        col4.metric("✈️ Total Aircraft", f"{aircraft:,.0f}")
    else:
        col4.metric("✈️ Total Aircraft", "N/A")

    # --------------------------------------------------------
    # SECOND KPI ROW
    # --------------------------------------------------------

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    if "Tanks" in filtered_df.columns:
        tanks = numeric_value(filtered_df, "Tanks").sum()
        col1.metric("🪖 Tanks", f"{tanks:,.0f}")

    if "Total_Naval_Fleet" in filtered_df.columns:
        naval = numeric_value(filtered_df, "Total_Naval_Fleet").sum()
        col2.metric("⚓ Naval Fleet", f"{naval:,.0f}")

    if "Submarines" in filtered_df.columns:
        submarines = numeric_value(filtered_df, "Submarines").sum()
        col3.metric("🌊 Submarines", f"{submarines:,.0f}")

    if "Aircraft_Carriers" in filtered_df.columns:
        carriers = numeric_value(filtered_df, "Aircraft_Carriers").sum()
        col4.metric("🚢 Aircraft Carriers", f"{carriers:,.0f}")

    # --------------------------------------------------------
    # MILITARY POWER RANKING
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("🏆 Military Power Ranking")

    if "power_index" in filtered_df.columns:

        ranking_df = filtered_df.copy()
        ranking_df["power_index"] = numeric_value(ranking_df, "power_index")
        ranking_df = ranking_df.dropna(subset=["power_index"])
        ranking_df = ranking_df.sort_values(
            "power_index", ascending=False
        ).head(top_n).sort_values("power_index", ascending=True)

        bar_chart(
            ranking_df, "country", "power_index",
            "Military Power Index", horizontal=True
        )

    # --------------------------------------------------------
    # DEFENCE BUDGET
    # --------------------------------------------------------

    st.subheader("💰 Defence Budget Ranking")

    if "Defense_Budget_USD_Billion" in filtered_df.columns:

        budget_df = filtered_df.copy()
        budget_df["Defense_Budget_USD_Billion"] = numeric_value(
            budget_df, "Defense_Budget_USD_Billion"
        )
        budget_df = budget_df.sort_values(
            "Defense_Budget_USD_Billion", ascending=False
        ).head(top_n)

        bar_chart(
            budget_df, "country", "Defense_Budget_USD_Billion",
            "Defence Budget by Country"
        )

    # --------------------------------------------------------
    # ACTIVE PERSONNEL
    # --------------------------------------------------------

    st.subheader("👥 Active Military Personnel")

    if "Active_Personnel" in filtered_df.columns:

        personnel_df = filtered_df.copy()
        personnel_df["Active_Personnel"] = numeric_value(
            personnel_df, "Active_Personnel"
        )
        personnel_df = personnel_df.sort_values(
            "Active_Personnel", ascending=False
        ).head(top_n)

        bar_chart(
            personnel_df, "country", "Active_Personnel",
            "Active Military Personnel"
        )

    # --------------------------------------------------------
    # BUDGET VS POWER INDEX
    # --------------------------------------------------------

    st.subheader("📊 Defence Budget vs Military Power")

    required = ["Defense_Budget_USD_Billion", "power_index"]

    if all(col in filtered_df.columns for col in required):

        scatter_df = filtered_df.copy()
        scatter_df["Defense_Budget_USD_Billion"] = numeric_value(
            scatter_df, "Defense_Budget_USD_Billion"
        )
        scatter_df["power_index"] = numeric_value(scatter_df, "power_index")

        if "Active_Personnel" in scatter_df.columns:
            scatter_df["Active_Personnel"] = numeric_value(
                scatter_df, "Active_Personnel"
            )
        else:
            scatter_df["Active_Personnel"] = 1

        scatter_chart(
            scatter_df, "Defense_Budget_USD_Billion", "power_index",
            "Defence Budget vs Military Power Index",
            size_col="Active_Personnel",
            xlabel="Defence Budget (USD Billion)",
            ylabel="Military Power Index"
        )


# ============================================================
# PAGE 2 — AIR POWER
# ============================================================

elif page == "✈️ Air Power":

    st.title("✈️ Air Power Analysis")
    st.markdown("Analysis of military aircraft and helicopter capabilities.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    if "Total_Aircraft" in filtered_df.columns:
        value = numeric_value(filtered_df, "Total_Aircraft").sum()
        col1.metric("✈️ Total Aircraft", f"{value:,.0f}")

    if "Fighter_Interceptor_Aircraft" in filtered_df.columns:
        value = numeric_value(filtered_df, "Fighter_Interceptor_Aircraft").sum()
        col2.metric("🛩️ Fighters", f"{value:,.0f}")

    if "Helicopters" in filtered_df.columns:
        value = numeric_value(filtered_df, "Helicopters").sum()
        col3.metric("🚁 Helicopters", f"{value:,.0f}")

    if "Attack_Helicopters" in filtered_df.columns:
        value = numeric_value(filtered_df, "Attack_Helicopters").sum()
        col4.metric("💥 Attack Helicopters", f"{value:,.0f}")

    # --------------------------------------------------------
    # TOTAL AIRCRAFT
    # --------------------------------------------------------

    st.subheader("✈️ Total Aircraft")

    if "Total_Aircraft" in filtered_df.columns:

        chart_df = filtered_df.copy()
        chart_df["Total_Aircraft"] = numeric_value(chart_df, "Total_Aircraft")
        chart_df = chart_df.sort_values(
            "Total_Aircraft", ascending=False
        ).head(top_n)

        bar_chart(chart_df, "country", "Total_Aircraft", "Total Military Aircraft")

    # --------------------------------------------------------
    # FIGHTERS
    # --------------------------------------------------------

    st.subheader("🛩️ Fighter / Interceptor Aircraft")

    if "Fighter_Interceptor_Aircraft" in filtered_df.columns:

        chart_df = filtered_df.copy()
        chart_df["Fighter_Interceptor_Aircraft"] = numeric_value(
            chart_df, "Fighter_Interceptor_Aircraft"
        )
        chart_df = chart_df.sort_values(
            "Fighter_Interceptor_Aircraft", ascending=False
        ).head(top_n)

        bar_chart(
            chart_df, "country", "Fighter_Interceptor_Aircraft",
            "Fighter / Interceptor Aircraft"
        )

    # --------------------------------------------------------
    # HELICOPTERS
    # --------------------------------------------------------

    st.subheader("🚁 Helicopters")

    if "Helicopters" in filtered_df.columns:

        chart_df = filtered_df.copy()
        chart_df["Helicopters"] = numeric_value(chart_df, "Helicopters")
        chart_df = chart_df.sort_values(
            "Helicopters", ascending=False
        ).head(top_n)

        bar_chart(chart_df, "country", "Helicopters", "Military Helicopters")

    # --------------------------------------------------------
    # ATTACK HELICOPTERS
    # --------------------------------------------------------

    st.subheader("💥 Attack Helicopters")

    if "Attack_Helicopters" in filtered_df.columns:

        chart_df = filtered_df.copy()
        chart_df["Attack_Helicopters"] = numeric_value(
            chart_df, "Attack_Helicopters"
        )
        chart_df = chart_df.sort_values(
            "Attack_Helicopters", ascending=False
        ).head(top_n)

        bar_chart(chart_df, "country", "Attack_Helicopters", "Attack Helicopters")

    # --------------------------------------------------------
    # AIRCRAFT COMPOSITION
    # --------------------------------------------------------

    st.subheader("🥧 Air Power Composition")

    composition_columns = [
        "Fighter_Interceptor_Aircraft",
        "Transport_Aircraft",
        "Helicopters",
        "Attack_Helicopters"
    ]

    available = [c for c in composition_columns if c in filtered_df.columns]

    if available:

        composition = filtered_df[available].sum()
        composition = pd.to_numeric(composition, errors="coerce").dropna()

        if composition.sum() > 0:
            pie_chart(
                composition.index, composition.values,
                "Selected Countries — Air Power Composition"
            )


# ============================================================
# PAGE 3 — LAND POWER
# ============================================================

elif page == "🪖 Land Power":

    st.title("🪖 Land Power Analysis")
    st.markdown("Analysis of major land-based military assets.")
    st.markdown("---")

    land_columns = [
        "Tanks",
        "Armored_Fighting_Vehicles",
        "Self_Propelled_Artillery",
        "Towed_Artillery",
        "Rocket_Projectors_MLRS"
    ]

    available_land = [c for c in land_columns if c in filtered_df.columns]

    land_df = filtered_df.copy()
    land_df["Total_Land_Combat_Assets"] = 0

    for col in available_land:
        land_df["Total_Land_Combat_Assets"] += numeric_value(land_df, col).fillna(0)

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    if "Tanks" in land_df.columns:
        col1.metric("🪖 Tanks", f"{numeric_value(land_df, 'Tanks').sum():,.0f}")

    if "Armored_Fighting_Vehicles" in land_df.columns:
        col2.metric(
            "🚙 Armored Fighting Vehicles",
            f"{numeric_value(land_df, 'Armored_Fighting_Vehicles').sum():,.0f}"
        )

    if "Self_Propelled_Artillery" in land_df.columns:
        col3.metric(
            "💣 Self-Propelled Artillery",
            f"{numeric_value(land_df, 'Self_Propelled_Artillery').sum():,.0f}"
        )

    col4.metric(
        "🪖 Total Land Assets",
        f"{land_df['Total_Land_Combat_Assets'].sum():,.0f}"
    )

    # --------------------------------------------------------
    # LAND POWER CHARTS
    # --------------------------------------------------------

    chart_columns = [
        ("Tanks", "🪖 Tanks"),
        ("Armored_Fighting_Vehicles", "🚙 Armored Fighting Vehicles"),
        ("Self_Propelled_Artillery", "💣 Self-Propelled Artillery"),
        ("Towed_Artillery", "🎯 Towed Artillery"),
        ("Rocket_Projectors_MLRS", "🚀 MLRS / Rocket Projectors"),
        ("Total_Land_Combat_Assets", "🪖 Total Land Combat Assets")
    ]

    for column, title in chart_columns:

        if column in land_df.columns:

            chart_df = land_df[["country", column]].copy()
            chart_df[column] = numeric_value(chart_df, column)
            chart_df = chart_df.sort_values(column, ascending=False).head(top_n)

            st.subheader(title)
            bar_chart(chart_df, "country", column, title)

    # --------------------------------------------------------
    # LAND POWER TABLE
    # --------------------------------------------------------

    st.subheader("📋 Land Power Details")

    display_columns = ["country"] + [
        c for c in land_columns if c in land_df.columns
    ]
    display_columns.append("Total_Land_Combat_Assets")

    st.dataframe(land_df[display_columns], use_container_width=True)


# ============================================================
# PAGE 4 — NAVAL POWER
# ============================================================

elif page == "⚓ Naval Power":

    st.title("⚓ Naval Power Analysis")
    st.markdown("Analysis of naval fleet strength and composition.")
    st.markdown("---")

    naval_columns = [
        "Naval_Fleet_Ships",
        "Total_Naval_Fleet",
        "Aircraft_Carriers",
        "Submarines",
        "Destroyers",
        "Frigates",
        "Corvettes",
        "Patrol_Vessels"
    ]

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    if "Total_Naval_Fleet" in filtered_df.columns:
        col1.metric(
            "⚓ Naval Fleet",
            f"{numeric_value(filtered_df, 'Total_Naval_Fleet').sum():,.0f}"
        )

    if "Aircraft_Carriers" in filtered_df.columns:
        col2.metric(
            "🚢 Aircraft Carriers",
            f"{numeric_value(filtered_df, 'Aircraft_Carriers').sum():,.0f}"
        )

    if "Submarines" in filtered_df.columns:
        col3.metric(
            "🌊 Submarines",
            f"{numeric_value(filtered_df, 'Submarines').sum():,.0f}"
        )

    if "Destroyers" in filtered_df.columns:
        col4.metric(
            "⚓ Destroyers",
            f"{numeric_value(filtered_df, 'Destroyers').sum():,.0f}"
        )

    # --------------------------------------------------------
    # NAVAL CHARTS
    # --------------------------------------------------------

    chart_columns = [
        ("Total_Naval_Fleet", "⚓ Total Naval Fleet"),
        ("Aircraft_Carriers", "🚢 Aircraft Carriers"),
        ("Submarines", "🌊 Submarines"),
        ("Destroyers", "⚓ Destroyers"),
        ("Frigates", "⚓ Frigates"),
        ("Corvettes", "⚓ Corvettes"),
        ("Patrol_Vessels", "🚤 Patrol Vessels")
    ]

    for column, title in chart_columns:

        if column in filtered_df.columns:

            chart_df = filtered_df[["country", column]].copy()
            chart_df[column] = numeric_value(chart_df, column)
            chart_df = chart_df.sort_values(column, ascending=False).head(top_n)

            st.subheader(title)
            bar_chart(chart_df, "country", column, title)

    # --------------------------------------------------------
    # NAVAL COMPOSITION
    # --------------------------------------------------------

    st.subheader("⚓ Naval Fleet Composition")

    composition_columns = [
        "Aircraft_Carriers",
        "Submarines",
        "Destroyers",
        "Frigates",
        "Corvettes",
        "Patrol_Vessels"
    ]

    available = [c for c in composition_columns if c in filtered_df.columns]

    if available:

        composition_df = filtered_df[available].copy()

        for col in available:
            composition_df[col] = numeric_value(composition_df, col).fillna(0)

        composition_df["country"] = filtered_df["country"]
        composition_df = composition_df.head(top_n)

        stacked_bar_chart(
            composition_df, "country", available, "Naval Fleet Composition"
        )

    # --------------------------------------------------------
    # NAVAL TABLE
    # --------------------------------------------------------

    st.subheader("📋 Naval Power Details")

    display_columns = [c for c in naval_columns if c in filtered_df.columns]

    if display_columns:
        st.dataframe(
            filtered_df[["country"] + display_columns],
            use_container_width=True
        )


# ============================================================
# PAGE 5 — DEFENCE SPENDING
# ============================================================

elif page == "💰 Defence Spending":

    st.title("💰 Defence Spending Analysis")
    st.markdown("Analysis of defence expenditure and economic capacity.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    if "Defense_Budget_USD_Billion" in filtered_df.columns:
        total_budget = numeric_value(
            filtered_df, "Defense_Budget_USD_Billion"
        ).sum()
        col1.metric("💰 Total Defence Budget", f"${total_budget:,.2f} B")

    if "Defense_Budget_Per_Capita" in filtered_df.columns:
        avg_per_capita = numeric_value(
            filtered_df, "Defense_Budget_Per_Capita"
        ).mean()
        col2.metric("👤 Avg. Budget / Capita", f"${avg_per_capita:,.2f}")

    if "Military_Expenditure_GDP_Percent" in filtered_df.columns:
        avg_gdp = numeric_value(
            filtered_df, "Military_Expenditure_GDP_Percent"
        ).mean()
        col3.metric("📈 Avg. Military Expenditure", f"{avg_gdp:.2f}% GDP")

    if "GDP_PPP" in filtered_df.columns:
        gdp = numeric_value(filtered_df, "GDP_PPP").sum()
        col4.metric("🌎 Total GDP PPP", f"{gdp:,.2f}")

    # --------------------------------------------------------
    # DEFENCE BUDGET
    # --------------------------------------------------------

    if "Defense_Budget_USD_Billion" in filtered_df.columns:

        st.subheader("💰 Defence Budget by Country")

        budget_df = filtered_df[["country", "Defense_Budget_USD_Billion"]].copy()
        budget_df["Defense_Budget_USD_Billion"] = numeric_value(
            budget_df, "Defense_Budget_USD_Billion"
        )
        budget_df = budget_df.sort_values(
            "Defense_Budget_USD_Billion", ascending=False
        ).head(top_n)

        bar_chart(budget_df, "country", "Defense_Budget_USD_Billion", "Defence Budget")

    # --------------------------------------------------------
    # BUDGET PER CAPITA
    # --------------------------------------------------------

    if "Defense_Budget_Per_Capita" in filtered_df.columns:

        st.subheader("👤 Defence Budget Per Capita")

        percap_df = filtered_df[["country", "Defense_Budget_Per_Capita"]].copy()
        percap_df["Defense_Budget_Per_Capita"] = numeric_value(
            percap_df, "Defense_Budget_Per_Capita"
        )
        percap_df = percap_df.sort_values(
            "Defense_Budget_Per_Capita", ascending=False
        ).head(top_n)

        bar_chart(
            percap_df, "country", "Defense_Budget_Per_Capita",
            "Defence Budget Per Capita"
        )

    # --------------------------------------------------------
    # MILITARY EXPENDITURE % GDP
    # --------------------------------------------------------

    if "Military_Expenditure_GDP_Percent" in filtered_df.columns:

        st.subheader("📈 Military Expenditure as % of GDP")

        gdp_df = filtered_df[
            ["country", "Military_Expenditure_GDP_Percent"]
        ].copy()
        gdp_df["Military_Expenditure_GDP_Percent"] = numeric_value(
            gdp_df, "Military_Expenditure_GDP_Percent"
        )
        gdp_df = gdp_df.sort_values(
            "Military_Expenditure_GDP_Percent", ascending=False
        ).head(top_n)

        bar_chart(
            gdp_df, "country", "Military_Expenditure_GDP_Percent",
            "Military Expenditure (% of GDP)"
        )

    # --------------------------------------------------------
    # BUDGET VS POWER INDEX
    # --------------------------------------------------------

    if (
        "Defense_Budget_USD_Billion" in filtered_df.columns
        and "power_index" in filtered_df.columns
    ):

        st.subheader("📊 Defence Budget vs Power Index")

        scatter_df = filtered_df.copy()
        scatter_df["Defense_Budget_USD_Billion"] = numeric_value(
            scatter_df, "Defense_Budget_USD_Billion"
        )
        scatter_df["power_index"] = numeric_value(scatter_df, "power_index")

        scatter_chart(
            scatter_df, "Defense_Budget_USD_Billion", "power_index",
            "Defence Budget vs Military Power Index"
        )


# ============================================================
# PAGE 6 — WORLD MAP (Plotly choropleth — only page using Plotly)
# ============================================================

elif page == "🌍 World Map":

    st.title("🌍 Global Defence Power Map")

    st.markdown(
        "Interactive geographical visualization of defence capabilities."
    )

    st.markdown("---")

    map_options = {
        "Military Power Index": "power_index",
        "Defence Budget (USD Billion)": "Defense_Budget_USD_Billion",
        "Active Military Personnel": "Active_Personnel",
        "Total Aircraft": "Total_Aircraft",
        "Tanks": "Tanks",
        "Armored Fighting Vehicles": "Armored_Fighting_Vehicles",
        "Total Naval Fleet": "Total_Naval_Fleet",
        "Submarines": "Submarines"
    }

    available_options = {
        name: column for name, column in map_options.items()
        if column in df.columns
    }

    selected_map = st.selectbox(
        "Select indicator for the map:",
        list(available_options.keys())
    )

    selected_column = available_options[selected_map]

    # Use complete dataset for map
    map_df = df[["country", selected_column]].copy()

    map_df[selected_column] = pd.to_numeric(
        map_df[selected_column], errors="coerce"
    )

    map_df = map_df.dropna(subset=[selected_column])

    # --------------------------------------------------------
    # WORLD MAP
    # --------------------------------------------------------

    fig_map = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color=selected_column,
        hover_name="country",
        color_continuous_scale="Viridis",
        projection="natural earth",
        title=f"{selected_map} by Country"
    )

    fig_map.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=60, b=0)
    )

    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        showocean=True,
        showcountries=True,
        countrycolor="gray"
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # --------------------------------------------------------
    # MAP DATA
    # --------------------------------------------------------

    st.subheader("🗺️ Map Data")

    st.dataframe(
        map_df.sort_values(selected_column, ascending=False),
        use_container_width=True
    )


# ============================================================
# PAGE 7 — DATA EXPLORER
# ============================================================

elif page == "📊 Data Explorer":

    st.title("📊 Data Explorer")
    st.markdown("Explore, filter and download the defence dataset.")
    st.markdown("---")

    search = st.text_input("🔎 Search country")

    explorer_df = df.copy()

    if search:
        explorer_df = explorer_df[
            explorer_df["country"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    selected_columns = st.multiselect(
        "Select columns to display",
        df.columns.tolist(),
        default=df.columns.tolist()
    )

    if selected_columns:
        explorer_df = explorer_df[selected_columns]

    st.subheader(f"📋 Dataset — {len(explorer_df)} rows")

    st.dataframe(explorer_df, use_container_width=True, height=600)

    csv = explorer_df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv,
        file_name="filtered_defence_data.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")
st.sidebar.caption("Global Defence Dashboard | 2026")