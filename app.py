import streamlit as st
import openai
import os

# ✅ 推荐使用 openai>=1.0.0 版本方式初始化客户端
from openai import OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Labubu × 麦肯锡 餐饮爆品预测模型", layout="wide")
st.title("🍽️ Labubu × 麦肯锡 餐饮爆品预测引擎")
st.caption("输入城市或菜品名，即可获得爆品预测 + 深度商业模型分析")

# 📍 输入区域
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍请输入城市名或地区（支持中英文）", placeholder="如 San Francisco / 广州")
with col2:
    dish_name = st.text_input("🍜 你想分析的菜品名（可选）", placeholder="如 酸菜鱼 / Hot Pot")

# 🌐 输出语言 & 📆 时间维度
col3, col4 = st.columns(2)
with col3:
    lang = st.radio("🌐 输出语言", ["中文", "English"], horizontal=True)
with col4:
    timeframe = st.radio("📆 时间维度", ["目前", "未来3个月", "未来6个月", "未来1年", "未来3年", "未来5年", "未来10年", "未来一世纪"], horizontal=False)

# 🔘 开始按钮
analyze_button = st.button("🔍 开始预测/分析")

# 💡 调用 OpenAI 进行爆品预测
@st.cache_data(show_spinner=False)
def predict_hot_dishes(location, timeframe, lang="中文"):
    prompt = f"""
你是餐饮市场顾问。请结合以下信息：
- 地区：{location}
- 时间：{timeframe}
预测该地区未来可能爆火的10道菜品，并列出其菜名。
输出语言为：{lang}
"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        content = resp.choices[0].message.content.strip()
        return [line.strip("\n0123456789.- ") for line in content.split("\n") if line.strip()]
    except Exception as e:
        return [f"❌ 爆品预测失败：{e}"]

# 📊 商业模型分析模块
@st.cache_data(show_spinner=False)
def analyze_dish_with_models(dish, lang="中文"):
    prompt = f"""
你是商业分析专家，请使用以下模型对菜品「{dish}」进行商业分析：
- SWOT分析
- 4P营销模型
- 蓝海战略
- T.O.P.V人效模型
- 其它常用模型如 PEST、AIDMA、波特五力、STP 等
输出语言：{lang}
内容尽量真实、专业、有深度，适合餐饮创业者阅读。
"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ 商业模型分析失败：{e}"

# 🎯 主执行逻辑
if analyze_button:
    if dish_name:
        st.subheader("📊 爆品商业模型分析")
        with st.spinner("正在生成深度分析报告..."):
            st.markdown(analyze_dish_with_models(dish_name, lang))

    elif location:
        st.subheader(f"📈 {location} 地区的潜在爆品预测（{timeframe}）")
        with st.spinner("AI 正在预测潜力菜品..."):
            predictions = predict_hot_dishes(location, timeframe, lang)
            for idx, item in enumerate(predictions, 1):
                with st.expander(f"{idx}. {item}"):
                    st.markdown(analyze_dish_with_models(item, lang))

    else:
        st.warning("⚠️ 请至少输入一个城市或菜品名以开始分析。")
