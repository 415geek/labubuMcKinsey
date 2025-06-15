import os
import streamlit as st
import numpy as np
from yelpapi import YelpAPI
import googlemaps
from openai import OpenAI
from pytrends.request import TrendReq
import re

# ---------------------------- 中英文地名支持 ----------------------------
CITY_MAP = {
    "旧金山": "San Francisco",
    "湾区": "San Francisco Bay Area",
    "洛杉矶": "Los Angeles",
    "纽约": "New York",
    "芝加哥": "Chicago",
    "西雅图": "Seattle",
    "波士顿": "Boston",
    "圣地亚哥": "San Diego",
    "圣何塞": "San Jose",
    "奥克兰": "Oakland",
    "加州": "California",
}

def is_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def normalize_location(user_input, openai_client=None):
    user_input = user_input.strip()
    if user_input in CITY_MAP:
        return CITY_MAP[user_input]
    if is_chinese(user_input) and openai_client:
        try:
            prompt = f"请将以下中文城市名称翻译为英文用于地图搜索：{user_input}"
            resp = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":prompt}],
                temperature=0,
                max_tokens=20
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"翻译失败，使用原始输入：{e}")
    return user_input

# ---------------------------- API 初始化 ----------------------------
def load_clients():
    yk, gk, ok = st.secrets["YELP_API_KEY"], st.secrets["GOOGLE_API_KEY"], st.secrets["OPENAI_API_KEY"]
    yelp = YelpAPI(yk)
    gmaps = googlemaps.Client(key=gk)
    client = OpenAI(api_key=ok)
    return yelp, gmaps, client

yelp_api, gmaps, openai_client = load_clients()

# ---------------------------- 核心函数 ----------------------------
def analyze_sentiment_with_gpt(texts):
    prompt = "请将下面每条评论按正面(+1)、中性(0)、负面(-1)分类，并输出平均值：\n"
    for t in texts:
        prompt += f"- {t}\n"
    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        return float(resp.choices[0].message.content.strip())
    except:
        return 0.0

def fetch_yelp(location, openai_client=None):
    normalized_location = normalize_location(location, openai_client)
    st.info(f"📍 使用的地名: {normalized_location}")
    try:
        result = yelp_api.search_query(term="restaurants", location=normalized_location, limit=10)
        return result.get('businesses', [])
    except Exception as e:
        st.error(f"❌ Yelp API 请求失败：{e}")
        return []
def fetch_google_reviews(name, loc):
    reviews = []
    resp = gmaps.places(query=f"{name} in {loc}", type="restaurant")
    for r in resp.get('results', [])[:3]:
        det = gmaps.place(place_id=r['place_id'], fields=['reviews'])
        reviews += [rev['text'] for rev in det.get('result', {}).get('reviews', [])]
    return reviews

def fetch_trend_score(term, geo="US"):
    py = TrendReq()
    py.build_payload([term], geo=geo, timeframe='today 12-m')
    df = py.interest_over_time()
    return float(df[term].mean()) if not df.empty else 0.0

def fetch_regional_econ(loc):
    return {"income": 80000, "population": 500000}

def predict_hot_dishes(businesses, reviews_list, loc):
    econ = fetch_regional_econ(loc)
    candidates = ["麻辣烫","云吞面","冰粉"]
    results = []
    for texts in reviews_list:
        senti = analyze_sentiment_with_gpt(texts)
        for dish in candidates:
            trend = fetch_trend_score(dish[:4], geo=loc[:2].upper())
            score = 0.4*senti + 0.3*trend + 0.2*(econ["income"]/1e5) + 0.1*min(len(texts)/100,1)
            results.append((dish, round(score,3), round(senti,2), round(trend,2)))
    unique = {d[0]: d for d in results}
    return sorted(unique.values(), key=lambda x: x[1], reverse=True)[:3]

def swot(dish, senti, trend, econ):
    return {
        "Strengths": f"情感分 {senti:.2f}，趋势热度 {trend:.1f}",
        "Weaknesses": "供应链稳定性需评估",
        "Opportunities": f"地区人均收入 {econ['income']} 带来消费潜力",
        "Threats": "竞品可能跟进加速"
    }

def four_p(dish):
    return {
        "Product": f"{dish} 本地现制现卖 + 口味适应",
        "Price": "中端定价 + 外卖套餐优惠",
        "Place": "堂食+外卖双渠道",
        "Promotion": "社交媒体+网红带动"
    }

def pest():
    return {
        "Politics": "食品安全监管严格",
        "Economy": "消费回暖",
        "Social": "健康解暑趋势",
        "Technology": "外卖与智能餐饮加速"
    }

# ---------------------------- Streamlit 页面 ----------------------------
st.title("labubu & 麦肯锡 餐饮爆品预测模型")
loc = st.text_input("请输入城市或邮编")
timeframe = st.selectbox("时间维度", ["目前","未来3月","半年","1年","3年","5年","100年"])
if st.button("预测爆品"):
    if not loc:
        st.error("请填写地区")
    else:
        data = fetch_yelp(loc, openai_client=openai_client)
        reviews = [fetch_google_reviews(b['name'], loc) for b in data]
        top = predict_hot_dishes(data, reviews, loc)
        econ = fetch_regional_econ(loc)
        st.markdown("### 🔥 爆品建议 Top3")
        for dish, score, senti, trend in top:
            if st.button(dish):
                st.subheader(f"{dish} 深度分析")
                st.write(f"📈 综合评分：{score}")
                st.write("#### SWOT 分析")
                for k,v in swot(dish,senti,trend,econ).items():
                    st.write(f"- **{k}**：{v}")
                st.write("#### 4P 策略")
                for k,v in four_p(dish).items():
                    st.write(f"- **{k}**：{v}")
                st.write("#### PEST 分析")
                for k,v in pest().items():
                    st.write(f"- **{k}**：{v}")
                st.write(f"💬 GPT 平均情感分：{senti:.2f}")
                st.write(f"🔍 Google 趋势得分：{trend:.1f}")
