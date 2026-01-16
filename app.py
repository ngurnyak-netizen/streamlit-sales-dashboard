import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------
# Настройки страницы (адаптивная ширина)
# --------------------
st.set_page_config(
    page_title="Анализ продаж e-commerce",
    layout="wide"
)

# Убираем лишний верхний отступ Streamlit
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------
# Загрузка данных
# --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("online_retail.csv", encoding="ISO-8859-1")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df

df = load_data()

# --------------------
# Заголовок
# --------------------
st.title("Анализ продаж интернет-магазина")
st.markdown(
    "Дашборд для анализа выручки и заказов с возможностью фильтрации по периоду и странам"
)

# --------------------
# Фильтры
# --------------------
st.sidebar.header("Фильтры")

min_date = df["InvoiceDate"].min()
max_date = df["InvoiceDate"].max()

date_range = st.sidebar.date_input(
    "Период",
    [min_date, max_date]
)

# Сначала фильтруем по дате
filtered_by_date = df[
    (df["InvoiceDate"].dt.date >= date_range[0]) &
    (df["InvoiceDate"].dt.date <= date_range[1])
]

# Вычисляем Top-N стран по выручке
max_countries = df["Country"].nunique()
top_n = st.sidebar.slider(
    "Количество стран для графика", min_value=1, max_value=max_countries, value=5    # топ n стран в выручке
)

country_sums = filtered_by_date.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
top_countries_list = country_sums.head(top_n).index.tolist()

# Обновляем multiselect стран, чтобы оставались только Top-N
countries = st.sidebar.multiselect(
    "Страна",
    options=sorted(top_countries_list),
    default=sorted(top_countries_list)
)

# Фильтруем окончательно по выбранным странам
filtered_df = filtered_by_date[filtered_by_date["Country"].isin(countries)]
# --------------------
# KPI
# --------------------
total_revenue = filtered_df["Revenue"].sum()
orders_count = filtered_df["InvoiceNo"].nunique()
avg_order_value = total_revenue / orders_count if orders_count > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Общая выручка", f"{total_revenue:,.0f}")
col2.metric("Количество заказов", f"{orders_count}")
col3.metric("Средний чек", f"{avg_order_value:,.2f}")
st.markdown("---")

# --------------------
# Подготовка данных для графиков
# --------------------
# Динамика выручки
time_df = (
    filtered_df
    .set_index("InvoiceDate")
    .resample("ME")["Revenue"]
    .sum()
    / 1_000
)

# Топ стран по выручке
country_df = (
    filtered_df
    .groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    / 1_000
)

# Графики
# --------------------
st.subheader("Динамика и структура выручки")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Динамика выручки по времени, тыс.**", unsafe_allow_html=True)

    if time_df.empty:
        st.warning("Нет данных для выбранных стран и периода")
    else:
        fig1, ax1 = plt.subplots()
        ax1.plot(time_df.index, time_df.values, marker="o", label="Выручка")
        ax1.set_xlabel("Период", fontsize=9)
        ax1.set_ylabel("Выручка, тыс.", fontsize=9)

        ax1.tick_params(axis="both", labelsize=7)
        plt.xticks(rotation=45)
        ax1.grid(axis='y', linestyle='--', alpha=0.5)  # полупрозрачная сетка
        
        # Подписи значений
        for x, y in zip(time_df.index, time_df.values):
            ax1.annotate(
                f"{y:,.0f}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 4),
                ha="center",
                fontsize=7
            )

        st.pyplot(fig1)
        

with col_right:
    st.markdown(f"**Топ-{top_n} стран по выручке, тыс.**", unsafe_allow_html=True)

    if country_df.empty:
        st.warning("Нет данных для выбранных стран и периода")
    else:
        fig2, ax2 = plt.subplots()
        country_df.plot(kind="bar", ax=ax2, color="skyblue")
        ax2.set_xlabel("Страна", fontsize=9)
        ax2.set_ylabel("Выручка, тыс.", fontsize=9)

        ax2.tick_params(axis="both", labelsize=7)
        plt.xticks(rotation=45)
        ax2.grid(axis='y', linestyle='--', alpha=0.5)  # полупрозрачная сетка

        # Подписи значений
        for i, value in enumerate(country_df.values):
            ax2.text(
                i,
                value,
                f"{value:,.0f}",
                ha="center",
                va="bottom",
                fontsize=7
            )

        st.pyplot(fig2)



