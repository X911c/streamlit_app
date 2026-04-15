import math
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


# --------------------------
# 关键修复：解决中文乱码
# --------------------------
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 页面配置
st.set_page_config(page_title="元素人格测试仪", page_icon="🧪", layout="centered")
st.title("🧪 元素人格测试仪")

# 输入代号
name = st.text_input("输入你的代号：", "见习炼金术士")
st.divider()

# --------------------------
# 提问环节（火/水/风/雷四维+进度条）
# --------------------------
st.header("📝 请回答以下问题")
st.caption("你的选择会决定火/水/风/雷属性分值，完成后点击匹配按钮")

# 四维题目列表（原有5题 + 新增5题，共10题）
questions = [
    {
        "q": "1. 面对新挑战，你会？",
        "options": [
            ("立刻冲上去尝试，不怕失败", "fire", 3),
            ("先观察情况，再谨慎行动", "water", 2),
            ("随缘尝试，不行就换方向", "wind", 2),
            ("精准预判，一击制胜", "thunder", 3),
            ("尽量避开，选择熟悉的事", "none", 0)
        ]
    },
    {
        "q": "2. 情绪激动时，你更倾向于？",
        "options": [
            ("直接表达感受，甚至有点冲动", "fire", 3),
            ("先冷静下来，慢慢梳理情绪", "water", 3),
            ("换个环境散心，很快恢复平静", "wind", 2),
            ("瞬间平复，绝不被情绪左右", "thunder", 2),
            ("压抑自己，假装没事", "none", -1)
        ]
    },
    {
        "q": "3. 做决定时，你通常？",
        "options": [
            ("凭直觉快速判断", "fire", 2),
            ("反复权衡利弊后再选", "water", 2),
            ("跟着当下感觉走，灵活调整", "wind", 3),
            ("瞬间决策，绝不犹豫", "thunder", 3),
            ("犹豫不决，需要他人建议", "none", -1)
        ]
    },
    {
        "q": "4. 周末你更想度过？",
        "options": [
            ("出门探险/运动，充满活力", "fire", 2),
            ("宅家看书/泡澡，安静放松", "water", 2),
            ("随机逛城市/探店，拥抱未知", "wind", 3),
            ("挑战极限运动，突破自我", "thunder", 2),
            ("和朋友聚会聊天，热闹社交", "none", 1)
        ]
    },
    {
        "q": "5. 你觉得自己更像？",
        "options": [
            ("火焰：热烈直接，行动力强", "fire", 4),
            ("水流：温柔包容，情绪稳定", "water", 4),
            ("风：自由随性，不喜束缚", "wind", 4),
            ("惊雷：迅猛凌厉，一击制胜", "thunder", 4),
            ("树：沉稳扎根，也向往阳光", "none", 2)
        ]
    },
    # ==================== 新增5道元素人格题 ====================
    {
        "q": "6. 朋友遇到麻烦，你会？",
        "options": [
            ("立刻帮忙，直接行动解决", "fire", 3),
            ("耐心倾听，慢慢安抚情绪", "water", 3),
            ("陪他散心，转移注意力", "wind", 2),
            ("一针见血指出问题，快速解决", "thunder", 3),
            ("不知道怎么做，默默陪着", "none", 0)
        ]
    },
    {
        "q": "7. 你更喜欢的沟通方式是？",
        "options": [
            ("直接坦率，有话直说", "fire", 2),
            ("温和委婉，照顾对方感受", "water", 2),
            ("轻松随意，想到什么说什么", "wind", 3),
            ("简洁干脆，不拖泥带水", "thunder", 3),
            ("很少主动，习惯倾听", "none", -1)
        ]
    },
    {
        "q": "8. 面对计划被打乱，你会？",
        "options": [
            ("立刻调整，重新开始行动", "fire", 2),
            ("冷静分析，重新制定方案", "water", 2),
            ("无所谓，顺其自然就好", "wind", 3),
            ("瞬间做出新判断，继续推进", "thunder", 3),
            ("感到烦躁，不想继续", "none", -1)
        ]
    },
    {
        "q": "9. 你更欣赏哪种特质？",
        "options": [
            ("热情勇敢，充满干劲", "fire", 3),
            ("温柔善良，内心强大", "water", 3),
            ("洒脱自在，不受拘束", "wind", 3),
            ("果断锐利，执行力极强", "thunder", 3),
            ("踏实稳重，一步一个脚印", "none", 1)
        ]
    },
    {
        "q": "10. 压力大时你会？",
        "options": [
            ("用运动/发泄释放压力", "fire", 2),
            ("独处沉淀，慢慢自我消化", "water", 2),
            ("出门走走，让心情随风放松", "wind", 3),
            ("集中精力快速解决压力源", "thunder", 3),
            ("逃避拖延，假装压力不存在", "none", -1)
        ]
    }
]

# 遍历题目，初始无默认选项
answers = {}
for i, q in enumerate(questions):
    ans = st.radio(q["q"], [opt[0] for opt in q["options"]], key=f"q{i}", index=None)
    answers[q["q"]] = ans

# 进度条展示
answered_count = sum(1 for ans in answers.values() if ans is not None)
progress = st.progress(answered_count / len(questions), text=f"答题进度：{answered_count}/{len(questions)}")

# --------------------------
# 分数计算（火/水/风/雷四维）
# --------------------------
def calc_scores(answers, questions):
    fire = 0
    water = 0
    wind = 0
    thunder = 0
    for q in questions:
        ans = answers[q["q"]]
        if ans is None:
            continue
        for opt in q["options"]:
            if opt[0] == ans:
                if opt[1] == "fire":
                    fire += opt[2]
                elif opt[1] == "water":
                    water += opt[2]
                elif opt[1] == "wind":
                    wind += opt[2]
                elif opt[1] == "thunder":
                    thunder += opt[2]
    # 归一化到0-10区间
    fire = max(0, min(10, fire))
    water = max(0, min(10, water))
    wind = max(0, min(10, wind))
    thunder = max(0, min(10, thunder))
    return fire, water, wind, thunder

# --------------------------
# 四维模板定义（新增雷系模板）
# --------------------------
profiles = {
    "🔥 烈焰型": [10, 3, 5, 4],       # 高火、低水、中风、中雷
    "💧 潮汐型": [3, 10, 5, 4],       # 低火、高水、中风、中雷
    "🌪️ 逐风型": [5, 3, 10, 4],       # 中火、低水、高风、中雷
    "⚡ 惊雷型": [9, 4, 9, 10],       # 高火、中水、高风、高雷（新增雷系核心模板）
    "⚖️ 平衡游侠": [7, 7, 7, 7],      # 四维均衡
    "🔥💧 炎汐使者": [8, 8, 4, 5],    # 火水双高、低风、中雷
    "💧🌪️ 风汐行者": [4, 8, 8, 5],    # 水风双高、低火、中雷
    "🔥⚡ 炎雷使者": [9, 4, 5, 9],    # 火雷双高、低水、中风
    "🌪️⚡ 风雷行者": [5, 4, 9, 9]     # 风雷双高、低水、中火
}

# 性格解读（新增雷系）
interpretations = {
    "🔥 烈焰型": "你像火焰一样热烈直接，行动力拉满，敢想敢做，充满感染力！面对挑战从不退缩，但有时会因急躁而忽略细节。🔥 专属buff：「热血冲锋」——做任何事都能瞬间进入状态！",
    "💧 潮汐型": "你像水流一样温柔包容，情绪稳定，善于倾听与思考。遇事冷静从容，但有时会因过于谨慎而错失机会。💧 专属buff：「冷静洞察」——总能在混乱中找到最优解！",
    "🌪️ 逐风型": "你像风一样自由随性，不喜束缚，热爱变化与未知。适应力极强，但有时会因太随性而缺乏坚持。🌪️ 专属buff：「百变随心」——任何环境都能快速找到乐趣！",
    "⚡ 惊雷型": "你像惊雷一样迅猛凌厉，爆发力拉满，反应极快，做事雷厉风行！擅长抓住转瞬即逝的机会，精准预判一击制胜。⚡ 专属buff：「雷霆一击」——关键时刻总能一击制胜！",
    "⚖️ 平衡游侠": "你四维属性均衡，既保有行动力又不失沉稳，能在冲动与理性间找到完美平衡。⚖️ 专属buff：「全能适应」——任何场景都能从容应对！",
    "🔥💧 炎汐使者": "你是火与水的交融，既有热血行动力，又有冷静思考力，是天生的领导者。🔥💧 专属buff：「刚柔并济」——既能冲锋也能兜底！",
    "💧🌪️ 风汐行者": "你是水与风的结合，温柔又自由，善于倾听也敢于探索，是天生的倾听者与冒险家。💧🌪️ 专属buff：「灵动治愈」——既能安抚他人也能拥抱变化！",
    "🔥⚡ 炎雷使者": "你是火与雷的碰撞，热情又凌厉，行动力与爆发力拉满，永远快人一步。🔥⚡ 专属buff：「烈火惊雷」——无人能挡的开拓之力！",
    "🌪️⚡ 风雷行者": "你是风与雷的结合，自由又迅猛，适应力与爆发力双高，永远在变化中抓住机会。🌪️⚡ 专属buff：「风雷万钧」——来去自如，一击制敌！"
}

# 分享文案（新增雷系）
share_templates = {
    "🔥 烈焰型": f"🔥【元素人格测试结果】🔥\n我是「烈焰型」人格！\n热烈直接，行动力拉满，敢想敢做，永远冲在挑战第一线！\n✨ 标签：感染力拉满 / 不怕失败 / 偶尔急躁但永远热血\n#元素人格测试仪 #烈焰型人格",
    "💧 潮汐型": f"💧【元素人格测试结果】💧\n我是「潮汐型」人格！\n温柔包容，情绪稳定，冷静从容，永远在思考后再行动！\n✨ 标签：沉稳可靠 / 善于倾听 / 偶尔谨慎但永远清醒\n#元素人格测试仪 #潮汐型人格",
    "🌪️ 逐风型": f"🌪️【元素人格测试结果】🌪️\n我是「逐风型」人格！\n自由随性，不喜束缚，永远热爱未知与变化！\n✨ 标签：适应力极强 / 热爱冒险 / 偶尔随性但永远鲜活\n#元素人格测试仪 #逐风型人格",
    "⚡ 惊雷型": f"⚡【元素人格测试结果】⚡\n我是「惊雷型」人格！\n迅猛凌厉，爆发力拉满，做事雷厉风行，永远快人一步！\n✨ 标签：反应超快 / 爆发力强 / 偶尔急躁但永远凌厉\n#元素人格测试仪 #惊雷型人格",
    "⚖️ 平衡游侠": f"⚖️【元素人格测试结果】⚖️\n我是「平衡游侠」人格！\n动静皆宜，进退有度，在热血与理性间找到完美平衡！\n✨ 标签：全能适应 / 均衡自在 / 永远从容不迫\n#元素人格测试仪 #平衡游侠人格",
    "🔥💧 炎汐使者": f"🔥💧【元素人格测试结果】🔥💧\n我是「炎汐使者」人格！\n刚柔并济，既能冲锋也能兜底，是天生的领导者！\n✨ 标签：领导力拉满 / 热血冷静 / 永远可靠\n#元素人格测试仪 #炎汐使者人格",
    "💧🌪️ 风汐行者": f"💧🌪️【元素人格测试结果】💧🌪️\n我是「风汐行者」人格！\n灵动治愈，既能安抚他人也能拥抱未知，是天生的倾听者与冒险家！\n✨ 标签：温柔自由 / 治愈力拉满 / 永远鲜活\n#元素人格测试仪 #风汐行者人格",
    "🔥⚡ 炎雷使者": f"🔥⚡【元素人格测试结果】🔥⚡\n我是「炎雷使者」人格！\n烈火惊雷，行动力与爆发力双拉满，永远无人能挡！\n✨ 标签：开拓力拉满 / 迅猛凌厉 / 永远热血\n#元素人格测试仪 #炎雷使者人格",
    "🌪️⚡ 风雷行者": f"🌪️⚡【元素人格测试结果】🌪️⚡\n我是「风雷行者」人格！\n风雷万钧，自由又迅猛，永远在变化中抓住机会！\n✨ 标签：适应力拉满 / 一击制敌 / 永远鲜活\n#元素人格测试仪 #风雷行者人格"
}

# 趣味彩蛋（新增雷系）
easter_eggs = {
    "🔥 烈焰型": "💡 小提示：下次做决定前，先深呼吸3秒，急躁会让你错过细节哦！",
    "💧 潮汐型": "💡 小提示：偶尔也可以「冲动」一次，生活会更有惊喜！",
    "🌪️ 逐风型": "💡 小提示：试着为一件事坚持30天，你会发现不一样的自己！",
    "⚡ 惊雷型": "💡 小提示：你的爆发力是超能力，记得用在关键的地方，别浪费在小事上！",
    "⚖️ 平衡游侠": "💡 小提示：你的平衡感是超能力，继续保持这份从容吧！",
    "🔥💧 炎汐使者": "💡 小提示：你天生适合带领团队，大胆站出来吧！",
    "💧🌪️ 风汐行者": "💡 小提示：你的温柔与自由是最珍贵的礼物，别弄丢了！",
    "🔥⚡ 炎雷使者": "💡 小提示：你的开拓力超棒，记得偶尔停下看看风景哦！",
    "🌪️⚡ 风雷行者": "💡 小提示：你的适应力是超能力，继续保持这份灵动吧！"
}

st.divider()

if answered_count == 10:
    if st.button("✨ 开始最终匹配", type="primary", use_container_width=True):
        fire_score, water_score, wind_score, thunder_score = calc_scores(answers, questions)
        user = [fire_score, water_score, wind_score, thunder_score]

        # --------------------------
        # 标准任务：计算并显示所有模板的四维距离
        # --------------------------
        st.subheader("📏 与各模板的四维距离")
        dist_dict = {}
        for title, coords in profiles.items():
            dist = math.sqrt(
                (user[0]-coords[0])**2 +
                (user[1]-coords[1])**2 +
                (user[2]-coords[2])**2 +
                (user[3]-coords[3])**2
            )
            dist_dict[title] = round(dist, 2)
            st.write(f"{title}：{dist:.2f}")

        # --------------------------
        # 进阶任务：找最小距离并显示
        # --------------------------
        min_dist = min(dist_dict.values())
        best_matches = [title for title, d in dist_dict.items() if d == min_dist]

        st.balloons()
        # 挑战任务：处理两个模板一样近的情况
        if len(best_matches) == 1:
            best_match = best_matches[0]
            st.success(f"🎉 {name}，你最接近的模板是：{best_match}")
            st.info(f"✅ 最小匹配距离：{min_dist:.2f}（数值越小越匹配）")
        else:
            match_str = "、".join(best_matches)
            st.success(f"🎉 {name}，你同时接近多个模板：{match_str}")
            st.info(f"✅ 共同最小匹配距离：{min_dist:.2f}（数值越小越匹配）")

        # --------------------------
        # 修复乱码：四维雷达图（火/水/风/雷）
        # --------------------------
        st.subheader("📊 你的元素属性雷达图")
        labels = ["火属性", "水属性", "风属性", "雷属性"]
        scores = [fire_score, water_score, wind_score, thunder_score]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, scores, color="#ff4b4b", linewidth=2, linestyle="solid")
        ax.fill(angles, scores, color="#ff4b4b", alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylim(0, 10)
        ax.set_yticks([])
        st.pyplot(fig)

        # 性格解读（支持多模板）
        st.subheader("📖 性格解读")
        for match in best_matches:
            st.markdown(f"**{match}**：{interpretations[match]}")
            st.info(easter_eggs[match])

        # 一键分享（支持多模板）
        st.divider()
        st.subheader("📤 一键分享你的结果")
        if len(best_matches) == 1:
            share_text = share_templates[best_match].replace("我是", f"{name}，我是")
        else:
            share_text = f"⚡【元素人格测试结果】⚡\n{name}，我同时匹配了「{'、'.join(best_matches)}」人格！\n多元特质拉满，既能热血冲锋，也能冷静从容！\n✨ 标签：多元全能 / 适配力拉满 / 永远不被定义\n#元素人格测试仪 #多元人格"
        st.code(share_text, language="text")
        st.info("👆 选中上方文案，复制即可分享到朋友圈/小红书~")
else:
    st.button("✨ 开始最终匹配", type="secondary", use_container_width=True, disabled=True)
    st.warning(f"请完成全部10道题后再匹配！当前已答：{answered_count}/10")