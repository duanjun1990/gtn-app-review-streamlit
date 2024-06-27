import pandas as pd
import plotly.express as px
import streamlit as st

# Load the CSV file
file_path = 'user_review.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)

# Convert 'created_at' to datetime
data['created_at'] = pd.to_datetime(data['created_at'], errors='coerce')

# Convert 'value' to numeric where possible, forcing errors to NaN
data['numeric_value'] = pd.to_numeric(data['value'], errors='coerce')

# Drop rows with NaN values in 'numeric_value' for calculations
data_numeric = data.dropna(subset=['numeric_value'])

# Extract month and year from 'created_at'
data['month_year'] = data['created_at'].dt.strftime('%Y年%m月')

# Map language codes to language names
language_mapping = {
    'zh': '中国語',
    'en': '英語',
    'vi': 'ベトナム語',
    'ko': '韓国語',
    'pt': 'ポルトガル語'
}

data['locale_name'] = data['locale'].map(language_mapping)

# Rename columns for detailed data display
data.rename(columns={
    'ticket_id': 'チケット番号',
    'text': '内容',
    'value': 'スコア',
    'created_at': '作成日時',
    'locale_name': '言語'
}, inplace=True)

# Function to create a hyperlink
def make_clickable(val):
    return f'<a href="https://admin.gtnapp.world/tickets/{val}">{val}</a>'

# Apply the function to 'チケット番号'
data['チケット番号'] = data['チケット番号'].apply(make_clickable)

# Streamlit app
st.title('GTNアプリユーザー評価')

# User selection for analysis type in the sidebar
st.sidebar.title("フィルター")
selected_month = st.sidebar.selectbox("月を選択してください", ["全月"] + list(data['month_year'].unique()))
selected_locale = st.sidebar.selectbox("言語を選択してください", ["全言語"] + list(data['言語'].unique()))

# Filter data based on selections
filtered_data = data.copy()
if selected_month != "全月":
    filtered_data = filtered_data[filtered_data['month_year'] == selected_month]

if selected_locale != "全言語":
    filtered_data = filtered_data[filtered_data['言語'] == selected_locale]

# Filter numeric data for calculations
filtered_numeric_data = filtered_data.dropna(subset=['numeric_value'])

# Exclude "ご自由にお書きください" for text average calculation in graphs
filtered_text_data = filtered_numeric_data[filtered_numeric_data['内容'] != 'ご自由にお書きください']

# Combined analysis
st.write(f"## {selected_month} の {selected_locale} のユーザー評価")

# Monthly and Locale analysis
monthly_avg = filtered_numeric_data.groupby('month_year')['numeric_value'].mean().reset_index()
locale_avg = filtered_numeric_data.groupby('言語')['numeric_value'].mean().reset_index()
text_avg = filtered_text_data.groupby('内容')['numeric_value'].mean().reset_index()

# Count analysis
monthly_count = filtered_data.groupby('month_year')['チケット番号'].nunique().reset_index()
locale_count = filtered_data.groupby('言語')['チケット番号'].nunique().reset_index()

if selected_month == "全月":
    # Plot monthly average score
    fig_month = px.line(monthly_avg, x='month_year', y='numeric_value', markers=True,
                        title='月別平均スコア',
                        labels={'month_year': '月', 'numeric_value': '平均スコア'})
    fig_month.update_traces(texttemplate='%{y:.2f}')
    fig_month.update_layout(yaxis_tickformat='.2f', margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_month)

    # Plot monthly count of unique tickets
    fig_month_count = px.bar(monthly_count, x='month_year', y='チケット番号',
                             title='月別チケット件数',
                             labels={'month_year': '月', 'チケット番号': '件数'})
    fig_month_count.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_month_count)

# Plot locale average score
fig_locale = px.bar(locale_avg, x='言語', y='numeric_value',
                    title=f'{selected_locale} の言語別平均スコア',
                    labels={'言語': '言語', 'numeric_value': '平均スコア'})
fig_locale.update_traces(texttemplate='%{y:.2f}', textposition='outside')
fig_locale.update_layout(yaxis_tickformat='.2f', margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_locale)

# Plot text average score excluding "ご自由にお書きください"
fig_text = px.bar(text_avg, x='内容', y='numeric_value',
                  title='各質問の平均スコア',
                  labels={'内容': '質問', 'numeric_value': '平均スコア'})
fig_text.update_traces(texttemplate='%{y:.2f}', textposition='outside')
fig_text.update_layout(yaxis_tickformat='.2f', margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig_text)

# Plot locale count of unique tickets
fig_locale_count = px.bar(locale_count, x='言語', y='チケット番号',
                          title=f'{selected_locale} の言語別チケット件数',
                          labels={'言語': '言語', 'チケット番号': '件数'})
fig_locale_count.update_layout(margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_locale_count)

# Detailed data with hyperlinks, including "ご自由にお書きください"
st.write("## 詳細データ")

# Remove unnecessary columns for detailed data display
detailed_data = filtered_data.drop(columns=['numeric_value', 'locale', 'month_year'])

# Replace NaN values with empty strings
detailed_data.fillna('', inplace=True)

# Convert dataframe to HTML
html_table = detailed_data.to_html(escape=False, index=False)

# Add CSS to center-align table headers
css = """
<style>
th {
    text-align: center;
}
</style>
"""

# Render HTML with CSS
st.write(css + html_table, unsafe_allow_html=True)