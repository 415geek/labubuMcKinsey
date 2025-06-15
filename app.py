import streamlit as st
import openai
import random
import os

# Set OpenAI API key securely (via env variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page setup
st.set_page_config(layout="wide")
st.title("Labubu & 麦肯锡餐饮爆品预测模型")
st.markdown("请输入城市或邮编，并选择时间维度以获取分析结果")

# Language toggle
lang = st.radio("语言 / Language", ["中文", "English"], horizontal=True)

# Location input
location = st.text_input("请输入城市或邮编：" if lang == "中文" else "Enter a city or postal code:")

# Timeframe button selection
st.markdown("时间维度选择" if lang == "中文" else "Timeframe Selection")
timeframe = st.radio(
    "", 
    ["目前", "未来3个月", "未来半年", "未来1年", "未来3年", "未来5年", "未来一世纪"],
    horizontal=True
)

# Dish input
dish_name = st.text_input("请输入菜品名（中英文均可）：" if lang == "中文" else "Enter a dish name to analyze:")

# Simulated DoorDash data
def simulate_doordash_popularity(dish, loc):
    return {
        "order_volume": random.randint(100, 800),
        "avg_rating": round(random.uniform(3.8, 4.9), 1),
        "platform_trend": "上升" if random.random() > 0.5 else "稳定"
    }

# GPT-based Business Model Analysis
def analyze_dish_commercially(dish, loc, timeframe, lang):
    models = [
        "T.O.P.V 模型", "3C 战略", "波特五力", "价值链", "AIDMA", "7S 模型", "4P 营销", "MECE 原则",
        "SWOT", "长尾理论", "二八法则", "STP 分析", "PEST", "6W2H", "FAST", "GROW", "MVP 模型",
        "P/MF 产品市场契合度", "波士顿矩阵", "蓝海战略"
    ]
    prompt_cn = f"""
请基于以下 20 种商业分析模型：{', '.join(models)}，
对“{dish}”这道菜在“{loc}”地区“{timeframe}”这个时间维度的爆品潜力进行全面、通俗且结构化的分析，
结合当地人群口味、经济能力、消费习惯、热度趋势等因素。
输出语言为中文。
"""
    prompt_en = f"""
Using the following 20 business strategy frameworks: {', '.join(models)},
please analyze the market potential of the dish '{dish}' in '{loc}' during the timeframe '{timeframe}'.
Your answer should be well-structured, insightful, and easy to understand for restaurant owners.
Output language: English.
"""
    prompt = prompt_cn if lang == "中文" else prompt_en

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ GPT分析失败：{str(e)}"

# Display section
if dish_name:
    with st.spinner("正在生成分析报告..." if lang == "中文" else "Generating analysis report..."):
        result = analyze_dish_commercially(dish_name, location, timeframe, lang)
        dd_pop = simulate_doordash_popularity(dish_name, location)

        st.subheader("📊 商业模型分析" if lang == "中文" else "📊 Business Model Analysis")
        st.markdown(result, unsafe_allow_html=True)

        st.subheader("📈 平台热度模拟" if lang == "中文" else "📈 Simulated Platform Popularity")
        st.markdown(
            f"""
- {'月订单量' if lang == "中文" else 'Monthly Orders'}: {dd_pop['order_volume']}
- {'平均评分' if lang == "中文" else 'Avg Rating'}: {dd_pop['avg_rating']}
- {'趋势' if lang == "中文" else 'Trend'}: {dd_pop['platform_trend']}
"""
        )
