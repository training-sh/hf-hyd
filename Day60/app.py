import duckdb
import streamlit as st
from native_access import available_sources, connect_source, conditions

st.set_page_config(page_title='Day60 | Sales Explorer', layout='wide')
st.title('Sales Explorer')
st.caption('Day60 | DuckDB file scans | Linux and HDFS')
source = st.sidebar.selectbox('Data source', available_sources())
st.sidebar.caption('The same 5,000 fictional sales orders in different storage formats.')
if st.sidebar.button('Refresh data'):
    st.cache_data.clear()

@st.cache_data(ttl=60)
def options(source):
    with connect_source(source) as con:
        regions = [r[0] for r in con.execute('SELECT DISTINCT region FROM sales ORDER BY region').fetchall()]
        categories = [r[0] for r in con.execute('SELECT DISTINCT category FROM sales ORDER BY category').fetchall()]
        dates = con.execute('SELECT min(order_date)::DATE, max(order_date)::DATE FROM sales').fetchone()
        return regions, categories, dates

@st.cache_data(ttl=60)
def dashboard(source, regions, categories, dates, months):
    where, params = conditions(regions, categories, dates, months)
    with connect_source(source) as con:
        def run(sql):
            return con.execute(sql, params).df()
        kpis = run(f'SELECT count(*) orders, sum(revenue) revenue, sum(profit) profit, sum(quantity) units FROM sales WHERE {where}')
        daily = run(f'SELECT order_date, sum(revenue) revenue FROM sales WHERE {where} GROUP BY order_date ORDER BY order_date')
        regional = run(f'SELECT region, sum(revenue) revenue FROM sales WHERE {where} GROUP BY region ORDER BY revenue DESC')
        category = run(f'SELECT category, count(*) orders, round(sum(revenue),2) revenue, round(sum(profit),2) profit FROM sales WHERE {where} GROUP BY category ORDER BY revenue DESC')
        details = run(f'SELECT order_id, order_date, region, category, quantity, revenue, profit FROM sales WHERE {where} ORDER BY order_id LIMIT 500')
        plan = con.execute(f'EXPLAIN SELECT region, sum(revenue) FROM sales WHERE {where} GROUP BY region', params).fetchone()[1]
        return kpis.iloc[0], daily, regional, category, details, plan

try:
    all_regions, all_categories, date_range = options(source)
    regions = st.sidebar.multiselect('Regions', all_regions, default=all_regions)
    categories = st.sidebar.multiselect('Categories', all_categories, default=all_categories)
    dates = st.sidebar.date_input('Order dates', date_range)
    months = None
    if 'partitioned' in source or 'HDFS Parquet' in source:
        months = st.sidebar.multiselect('Partition months (2026)', list(range(1, 7)), default=list(range(1, 7)))
    if len(dates) != 2:
        st.info('Select both a start and end date.')
        st.stop()
    kpis, daily, regional, category, details, plan = dashboard(source, regions, categories, dates, months)
except (duckdb.Error, OSError, ValueError) as exc:
    st.error(f'Could not query {source}: {exc}')
    st.stop()
if kpis.orders == 0:
    st.info('No orders match these filters.')
    st.stop()
for col, label, value in zip(st.columns(4), ['Orders', 'Revenue (INR)', 'Profit (INR)', 'Units'],
                           [f'{int(kpis.orders):,}', f'{kpis.revenue:,.0f}', f'{kpis.profit:,.0f}', f'{int(kpis.units):,}']):
    col.metric(label, value)
left, right = st.columns(2)
with left:
    st.subheader('Daily revenue')
    st.line_chart(daily.set_index('order_date'))
with right:
    st.subheader('Revenue by region')
    st.bar_chart(regional.set_index('region'))
st.subheader('Category performance')
st.dataframe(category, hide_index=True, width='stretch')
st.subheader('Order preview')
st.caption('Up to 500 matching orders. Metrics include every matching order.')
st.dataframe(details, hide_index=True, width='stretch')
st.download_button('Download preview CSV', details.to_csv(index=False), 'sales_preview.csv', 'text/csv')
with st.expander('Query plan and data access'):
    st.code(plan)
    st.caption('DuckDB queries files directly and returns small result DataFrames. Partition month filters enable directory pruning. WebHDFS is a Python filesystem adapter, not the native HDFS extension.')
