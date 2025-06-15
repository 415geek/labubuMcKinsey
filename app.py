import streamlit as st
import openai
import os

# 设置 API 密钥（需事先设置环境变量 OPENAI_API_KEY）
openai.api_key = os.getenv("OPENAI_API_KEY")

# 页面配置
st.set_page_config(page_title="Labubu × 麦肯锡 餐饮爆品预测模型", layout="wide")
st.title("🍽️ Labubu × 麦肯锡 餐饮爆品预测引擎")
st.caption("输入城市或菜品名，即可获得爆品预测 + 深度商业模型分析")

# 输入区域
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍请输入城市名或地区（支持中英文）", placeholder="如 San Francisco / 广州")
with col2:
    dish_name = st.text_input("🍜 你想分析的菜品名（可选）", placeholder="如 酸菜鱼 / Hot Pot")

# 语言与时间维度
col3, col4 = st.columns(2)
with col3:
    lang = st.radio("🌐 输出语言", ["中文", "English"], horizontal=True)
with col4:
    timeframe = st.radio("📆 时间维度", ["目前", "未来3个月", "未来6个月", "未来1年", "未来3年"], horizontal=True)

# 分析按钮
analyze_button = st.button("🔍 开始预测/分析")

# 模拟爆品预测逻辑（简化示例，可扩展为调用 GPT/外部API）
def predict_hot_dishes(location, timeframe, lang="中文"):
    dish_list = [
        "酸菜鱼", "麻辣香锅", "藤椒鸡", "黄焖鸡", "牛油火锅", 
        "香葱油拌面", "烤冷面", "螺蛳粉", "干锅花菜", "腊味煲仔饭"
    ]
    if lang == "English":
        dish_list = [
            "Sour Fish Soup", "Mala Hot Pot", "Green Pepper Chicken", "Yellow Braised Chicken",
            "Butter Hot Pot", "Scallion Oil Noodles", "Grilled Cold Noodles",
            "River Snail Rice Noodles", "Dry Pot Cauliflower", "Cured Meat Claypot Rice"
        ]
    return dish_list[:10]

# 分析菜品背后的商业模型
def analyze_dish_with_models(dish, lang="中文"):
    if lang == "中文":
        return f"""
🔍 **爆品分析报告：《{dish}》**

1. **SWOT分析**：
- 优势（Strengths）：口味独特，原料成本适中，社交平台传播性强。
- 劣势（Weaknesses）：标准化难度高，厨房操作复杂。
- 机会（Opportunities）：符合年轻人猎奇心理，适合短视频宣传。
- 威胁（Threats）：竞争者模仿速度快，区域接受度不同。

2. **4P营销模型**：
- 产品（Product）：突出菜品核心特色（如鲜、麻、香）。
- 价格（Price）：目标定价区间 $13-$18，结合城市消费水平。
- 渠道（Place）：适合中高端快餐 / 新中式正餐门店。
- 推广（Promotion）：通过抖音、小红书等平台打造“城市必吃爆款”。

3. **蓝海战略**：
- 当前地区尚无同类定位精准的爆品，适合率先布局打造差异化竞争力。

📊 **人效T.O.P.V**：高复购率 + 强曝光力 = 人效提升新引擎。
"""
    else:
        return f"""
🔍 **Hot Dish Analysis Report: {dish}**

1. **SWOT**:
- Strengths: Unique flavor, moderate cost, viral appeal.
- Weaknesses: Difficult to standardize, complex preparation.
- Opportunities: Strong appeal to Gen Z, ideal for TikTok marketing.
- Threats: Fast copycat risk, regional flavor preferences.

2. **4P**:
- Product: Emphasize spicy/savory flavor profile.
- Price: Target range $13–$18 based on area income.
- Place: Best for fast-casual or trendy Asian fusion restaurants.
- Promotion: Highlight via TikTok, Instagram Reels, Xiaohongshu.

3. **Blue Ocean Strategy**:
- Few direct competitors offering this niche—opportunity to dominate the segment.

📊 **T.O.P.V**: High repurchase + visibility = performance booster.
"""

# 主逻辑执行
if analyze_button:
    if dish_name:
        st.subheader("📊 爆品商业模型分析")
        st.markdown(analyze_dish_with_models(dish_name, lang))
    elif location:
        st.subheader("📈 爆品预测结果")
        result = predict_hot_dishes(location, timeframe, lang)
        for idx, item in enumerate(result, 1):
            with st.expander(f"{idx}. {item}"):
                st.markdown(analyze_dish_with_models(item, lang))
    else:
        st.warning("⚠️ 请至少输入一个城市或菜品名以开始分析。")
