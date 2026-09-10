import json
import random
import requests
import streamlit as st

import json
import random
import requests
import streamlit as st

# 自动过滤掉可能误入的非ASCII字符（如隐藏空格、特殊符号）
BIN_ID = str(st.secrets["JSONBIN_BIN_ID"]).strip().encode("ascii", "ignore").decode("ascii")
API_KEY = str(st.secrets["JSONBIN_API_KEY"]).strip().encode("ascii", "ignore").decode("ascii")

HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY,
    "X-Bin-Versioning": "false",
}
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY,
    "X-Bin-Versioning": "false",
}

def load_data():
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            data = res.json().get("record", [])
            return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"加载云端数据失败: {e}")
    return []

def save_data(data):
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        requests.put(url, headers=HEADERS, json=data)
    except Exception as e:
        st.error(f"同步到云端失败: {e}")

st.title("🧠 算法题目随机复习助手")

if "problems" not in st.session_state:
    st.session_state.problems = load_data()

with st.form("add_form", clear_on_submit=True):
    st.subheader("添加喜欢的题目")
    title = st.text_input("题目名称/描述", placeholder="例如：LeetCode 1. 两数之和")
    url = st.text_input("题目链接", placeholder="https://leetcode.cn/problems/...")
    tag = st.text_input("标签分类", placeholder="例如：动态规划 / 二分")
    submitted = st.form_submit_button("添加题目")
    
    if submitted and title and url:
        st.session_state.problems.append({
            "title": title, 
            "url": url, 
            "tag": tag.strip() if tag else "未分类",
            "count": 0
        })
        save_data(st.session_state.problems)
        st.success("添加成功并已同步至云端！")
        st.rerun()

st.divider()
st.subheader("🎲 随机复习")

all_tags = ["全部"] + list(set(p.get("tag", "未分类") for p in st.session_state.problems))
selected_tag = st.selectbox("选择复习的标签分类", all_tags)

if st.button("随机抽一题复习", type="primary"):
    if st.session_state.problems:
        if selected_tag == "全部":
            pool = st.session_state.problems
        else:
            pool = [p for p in st.session_state.problems if p.get("tag", "未分类") == selected_tag]
            
        if pool:
            picked = random.choice(pool)
            for p in st.session_state.problems:
                if p["url"] == picked["url"]:
                    p["count"] = p.get("count", 0) + 1
                    break
            save_data(st.session_state.problems)
            
            st.markdown(f"### 👉 抽中题目：[{picked['title']}]({picked['url']})  `{picked.get('tag', '未分类')}`  *(已复习 {picked.get('count', 0)} 次)*", unsafe_allow_html=True)
        else:
            st.warning(f"标签【{selected_tag}】下还没有题目！")
    else:
        st.warning("题库空啦，请先添加题目！")

st.divider()
st.subheader(f"📚 已收录题库 ({len(st.session_state.problems)})")
if st.session_state.problems:
    for i, p in enumerate(st.session_state.problems):
        col1, col2 = st.columns([5, 1])
        with col1:
            tag_str = f"[{p.get('tag', '未分类')}]" if p.get('tag') else ""
            count_str = f"🔥 {p.get('count', 0)}次"
            st.markdown(f"- {tag_str} [{p['title']}]({p['url']})  —  *{count_str}*")
        with col2:
            if st.button("删除", key=f"del_{i}"):
                st.session_state.problems.pop(i)
                save_data(st.session_state.problems)
                st.rerun()
