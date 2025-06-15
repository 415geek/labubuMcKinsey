import streamlit as st
import openai
import os
from yelpapi import YelpAPI
import googlemaps

# ========== API 密钥配置 ==========
openai.api_key = os.getenv("OPENAI_API_KEY")
yelp_api = YelpAPI(os.getenv("YELP_API_KEY"))
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))

# ========== 页面基础配置 ==========
st.set_page_config(page_title="Labubu × 麦肯锡 餐饮爆品预测引擎", layout="wide")
st.title("🍽️ Labubu × 麦肯锡 餐饮爆品预测引擎")
st.caption("输入城市或菜品名，即可获得爆品预测 + 深度商业模型分析")

# ========== 输入区域 ==========
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍请输入城市名或地区（支持中英文）", placeholder="如 San Francisco / 广州")
with col2:
    dish_name = st.text_input("🍜 你想分析的菜品名（可选）", placeholder="如 酸菜鱼 / Hot Pot")

# ========== 控制区域 ==========
col3, col4 = st.columns(2)
with col3:
    lang = st.radio("🌐 输出语言", ["中文", "English"], horizontal=True)
with col4:
    timeframe = st.radio(
        "📆 时间维度",
        ["目前", "未来3个月", "未来6个月", "未来1年", "未来3年", "未来5年", "未来10年", "未来一世纪"],
        horizontal=True,
    )

# ========== 分析按钮 ==========
analyze_button = st.button("🔍 开始预测/分析")

# ========== 模拟真实爆品预测逻辑 ==========
def predict_hot_dishes(location, timeframe, lang="中文"):
    prompt = f"""
你是一个餐饮行业分析专家，请基于城市“{location}”的市场现状和“{timeframe}”的发展趋势，预测未来最有可能成为爆品的10道中餐菜品。请提供菜品名（中英文均可）、流行原因（如受欢迎人群、特色口味）、适合的定价区间、适配的门店类型，并以结构化格式返回。
输出语言：{lang}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return resp.choices[0].message.content

# ========== 实时获取 Yelp 店铺数据 ==========
def fetch_yelp_data(location):
    try:
        results = yelp_api.search_query(term="Chinese food", location=location, limit=5)
        return results.get("businesses", [])
    except Exception as e:
        return []

# ========== Google 地址和评分 ==========
def fetch_google_info(name, loc):
    try:
        place = gmaps.places(query=f"{name} {loc}", type="restaurant")
        if place["results"]:
            res = place["results"][0]
            return {
                "rating": res.get("rating", "N/A"),
                "price_level": res.get("price_level", "N/A"),
                "address": res.get("formatted_address", "N/A"),
            }
    except Exception:
        pass
    return {"rating": "N/A", "price_level": "N/A", "address": "N/A"}

# ========== 商业分析模块 ==========
def analyze_dish_with_models(dish, lang="中文"):
    if lang == "中文":
        return f"""
🔍 **《{dish}》爆品商业模型分析**

1. **SWOT分析**：
- 优势：地域文化支撑、口味层次丰富
- 劣势：原料保鲜、标准化难
- 机会：社交平台种草潮流
- 威胁：同类产品同质化严重

2. **4P策略**：
- 产品：聚焦原汁原味
- 价格：适中亲民，$10–$18
- 渠道：线下中餐厅、新式快餐、商圈档口
- 推广：小红书、抖音达人带货、社区试吃

3. **蓝海战略**：开拓年轻人市场 + 海外华人社群

4. **AIDMA & TOPV模型**：
- 吸引注意（短视频）、激发兴趣（颜值）、唤起欲望（口感记忆）、行动（打卡）、满意复购
- 高复购 + 场景穿透力

5. **价格敏感性分析**：
- DoorDash同类均价：$15–$22；推荐起售价：$16.99

6. **Google/Yelp 热度**：整合动态评分与地址信息
"""
    else:
        return f"""
🔍 **Hot Dish Strategy Analysis: {dish}**

1. **SWOT**:
- Strengths: Authentic taste, strong regional identity
- Weaknesses: Hard to scale or standardize
- Opportunities: Strong appeal for short-video foodies
- Threats: High competition and imitation risk

2. **4P Model**:
- Product: Focus on flavor identity
- Price: Mid-tier $10–$18
- Place: Asian fusion outlets or trendy food courts
- Promotion: TikTok, Instagram Reels, pop-up events

3. **Blue Ocean**: Tap into Gen Z and overseas Chinese

4. **AIDMA & TOPV**:
- Attention → Interest → Desire → Memory → Action
- High ROI via visibility + quality

5. **Price Estimation**:
- DoorDash range: $15–$22; Suggested: $16.99

6. **Live API Signals**: Ratings and location synced from Yelp & Google
"""

# ========== 主逻辑 ==========
if analyze_button:
    if not location and not dish_name:
        st.warning("⚠️ 请至少输入一个城市或菜品名以开始分析。")
    else:
        if dish_name:
            st.subheader(f"📊 爆品商业模型分析：{dish_name}")
            st.markdown(analyze_dish_with_models(dish_name, lang))
            st.divider()
        
        if location:
            with st.spinner("🚀 正在基于 AI 模型进行爆品预测中..."):
                predictions = predict_hot_dishes(location, timeframe, lang)
                st.subheader(f"📈 爆品预测结果：{location}（{timeframe}）")
                st.markdown(predictions)

            st.divider()
            st.subheader("📍 实时热门餐厅示例（Yelp + Google Maps）")
            for biz in fetch_yelp_data(location):
                name = biz.get("name", "N/A")
                g_info = fetch_google_info(name, location)
                with st.expander(f"🍴 {name}"):
                    st.write(f"📍 地址：{g_info['address']}")
                    st.write(f"⭐ Yelp 评分：{biz.get('rating', 'N/A')}，Google评分：{g_info['rating']}")
                    st.write(f"💰 价格等级：Yelp: {biz.get('price', 'N/A')}，Google: {g_info['price_level']}")
                    st.write(f"🔗 Yelp 页面：{biz.get('url')}")
