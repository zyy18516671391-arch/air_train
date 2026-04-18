import streamlit as st
import math

st.set_page_config(layout="wide", page_title="空铁市场分担率计算系统")
st.title("🚄✈️ 空铁市场分担率计算系统")


# =====================================
# 核心计算逻辑封装函数
# =====================================
def render_calculator(default_city1, default_city2, uid):
    """
    渲染完整的计算器模块
    :param default_city1: 默认出发城市
    :param default_city2: 默认到达城市
    :param uid: 唯一标识符（用于区分不同页面的组件ID）
    """

    # 1️⃣ 出行时间成本计算 (保留UI，仅作参考展示)
    st.header("1️⃣ 单位时间价值 (VOT) ")

    st.info(
        "💡 **说明**：此模块用于测算城市群平均时间价值。在 SPSS 效用计算中，由于回归系数已包含时间偏好，不再需要将时长乘以 VOT，此处仅作经济学参考。")

    col_city1, col_city2, col_work = st.columns(3)
    with col_city1:
        city1 = st.text_input("出发城市", default_city1, key=f"city1_{uid}", autocomplete="off")
        income1 = float(st.text_input(f"{city1} 人均可支配收入", value="", placeholder="0", key=f"inc1_{uid}", autocomplete="off") or 0)
    with col_city2:
        city2 = st.text_input("到达城市", default_city2, key=f"city2_{uid}", autocomplete="off")
        income2 = float(st.text_input(f"{city2} 人均可支配收入", value="", placeholder="0", key=f"inc2_{uid}", autocomplete="off") or 0)
    with col_work:
        work_hours = float(st.text_input("年工作小时数", "1984", key=f"work_{uid}", autocomplete="off"))

    avg_income = (income1 + income2) / 2
    unit_time_cost = avg_income / work_hours if work_hours > 0 else 0

    st.markdown(f"平均收入: **{avg_income:.2f} 元** ｜ 单位时间价值 (VOT): **{unit_time_cost:.2f} 元/小时**")
    st.divider()

    # 2️⃣ 指标计算
    st.header("2️⃣ 核心出行属性录入")

    col1, col2 = st.columns(2)

    # 疲劳度原始计算与映射函数 (内嵌)
    def fatigue_raw(t, alpha, beta, L):
        return L / (1.0 + alpha * math.exp(-beta * t))

    def map_to_survey_scale(f_raw):
        f_min, f_max = 0.3, 1.2
        f_mapped = 1.0 + (f_raw - f_min) * 2.0 / (f_max - f_min)
        return max(1.0, min(3.0, f_mapped))

    # ================= 民航 =================
    with col1:
        st.subheader("✈️ 民航 (Air)")
        with st.container(border=True):
            # -------- 经济性 --------
            st.markdown("**💰 经济性 (票价)**")
            price_air = float(st.text_input("单程票价 (元)", value="", placeholder="0", key=f"price_air_{uid}", autocomplete="off") or 0)

            # -------- 快速性 --------
            st.markdown("**⏱️ 快速性 (纯运行)**")
            t2_air = float(st.text_input("纯飞行时间 t2 (h)", value="", placeholder="0", key=f"t2_air_{uid}", autocomplete="off") or 0)

            # -------- 便捷性 --------
            st.markdown("**🚶 便捷性 (站外综合时间)**")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                t1_air = float(st.text_input("安检候机 t1 (h)", value="", placeholder="0", key=f"t1_air_{uid}", autocomplete="off") or 0)
                a1_air = float(st.text_input("出发接驳 a1 (h)", value="", placeholder="0", key=f"acc1_air_{uid}", autocomplete="off") or 0)
            with col_a2:
                t3_air = float(st.text_input("离开机场 t3 (h)", value="", placeholder="0", key=f"t3_air_{uid}", autocomplete="off") or 0)
                a2_air = float(st.text_input("到达接驳 a2 (h)", value="", placeholder="0", key=f"acc2_air_{uid}", autocomplete="off") or 0)

            access_air_total = t1_air + t3_air + a1_air + a2_air
            st.caption(f"↳ 站外综合耗时：{access_air_total:.2f} h")

            # -------- 舒适性 --------
            st.markdown("**💺 舒适性 (疲劳度)**")
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                L_air = float(st.text_input("极限 L", "15", key=f"L_air_{uid}", autocomplete="off"))
            with col_f2:
                alpha_air = float(st.text_input("参数 α", "69", key=f"alpha_air_{uid}", autocomplete="off"))
            with col_f3:
                beta_air = float(st.text_input("参数 β", "0.25", key=f"beta_air_{uid}", autocomplete="off"))

            f_raw_air = fatigue_raw(t2_air, alpha_air, beta_air, L_air)
            comfort_air_mapped = map_to_survey_scale(f_raw_air)
            st.caption(f"↳ 原始得分: {f_raw_air:.3f} ➔ **映射等级: {comfort_air_mapped:.2f} 级**")

    # ================= 高铁 =================
    with col2:
        st.subheader("🚄 高铁 (Train)")
        with st.container(border=True):
            # -------- 经济性 --------
            st.markdown("**💰 经济性 (票价)**")
            price_train = float(st.text_input("单程票价 (元)", value="", placeholder="0", key=f"price_train_{uid}", autocomplete="off") or 0)

            # -------- 快速性 --------
            st.markdown("**⏱️ 快速性 (纯运行)**")
            t2_train = float(st.text_input("纯运行时间 t2 (h)", value="", placeholder="0", key=f"t2_train_{uid}", autocomplete="off") or 0)

            # -------- 便捷性 --------
            st.markdown("**🚶 便捷性 (站外综合时间)**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t1_train = float(st.text_input("进站等候 t1 (h)", value="", placeholder="0", key=f"t1_train_{uid}", autocomplete="off") or 0)
                a1_train = float(st.text_input("出发接驳 a1 (h)", value="", placeholder="0", key=f"acc1_train_{uid}", autocomplete="off") or 0)
            with col_t2:
                t3_train = float(st.text_input("离开车站 t3 (h)", value="", placeholder="0", key=f"t3_train_{uid}", autocomplete="off") or 0)
                a2_train = float(st.text_input("到达接驳 a2 (h)", value="", placeholder="0", key=f"acc2_train_{uid}", autocomplete="off") or 0)

            access_train_total = t1_train + t3_train + a1_train + a2_train
            st.caption(f"↳ 站外综合耗时：{access_train_total:.2f} h")

            # -------- 舒适性 --------
            st.markdown("**💺 舒适性 (疲劳度)**")
            col_f4, col_f5, col_f6 = st.columns(3)
            with col_f4:
                L_train = float(st.text_input("极限 L", "15", key=f"L_train_{uid}", autocomplete="off"))
            with col_f5:
                alpha_train = float(st.text_input("参数 α", "69", key=f"alpha_train_{uid}", autocomplete="off"))
            with col_f6:
                beta_train = float(st.text_input("参数 β", "0.22", key=f"beta_train_{uid}", autocomplete="off"))

            f_raw_train = fatigue_raw(t2_train, alpha_train, beta_train, L_train)
            comfort_train_mapped = map_to_survey_scale(f_raw_train)
            st.caption(f"↳ 原始得分: {f_raw_train:.3f} ➔ **映射等级: {comfort_train_mapped:.2f} 级**")

    st.divider()

    # 3️⃣ 效用函数构建
    st.header("3️⃣ 模型效用计算 (SPSS 系数)")

    st.markdown("### 效用函数形式：")
    st.latex(r"""
    U_i = \beta_{price} \cdot P + \beta_{time} \cdot t_2 + \beta_{access} \cdot A_{out} + \beta_{comfort} \cdot F_{mapped}
    """)

    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    with col_w1:
        w_price = float(st.text_input("经济性系数 (b_price)", value="", placeholder="0", key=f"w1_{uid}", autocomplete="off") or 0)
    with col_w2:
        w_time = float(st.text_input("快速性系数 (b_time)", value="", placeholder="0", key=f"w2_{uid}", autocomplete="off") or 0)
    with col_w3:
        w_access = float(st.text_input("便捷性系数 (b_access)", value="", placeholder="0", key=f"w3_{uid}", autocomplete="off") or 0)
    with col_w4:
        w_comfort = float(st.text_input("舒适性系数 (b_comfort)", value="", placeholder="0", key=f"w4_{uid}", autocomplete="off") or 0)

    # 注意：直接采用加法，系数应输入 SPSS 回归出的负值
    U_air = (w_price * price_air) + (w_time * t2_air) + (w_access * access_air_total) + (w_comfort * comfort_air_mapped)
    U_train = (w_price * price_train) + (w_time * t2_train) + (w_access * access_train_total) + (
                w_comfort * comfort_train_mapped)

    col_u1, col_u2 = st.columns(2)
    col_u1.info(f"✈️ 民航最终效用 U = **{U_air:.4f}**")
    col_u2.info(f"🚄 高铁最终效用 U = **{U_train:.4f}**")

    # 4️⃣ 分担率计算
    st.header("4️⃣ 市场分担率计算 (Logit)")

    # --- 新增：结果前的公式展示 ---
    st.markdown("### 分担率计算公式：")
    col_formula1, col_formula2 = st.columns(2)
    with col_formula1:
        st.latex(r"P_{air} = \frac{e^{U_{air}}}{e^{U_{air}} + e^{U_{train}}}")
    with col_formula2:
        st.latex(r"P_{train} = \frac{e^{U_{train}}}{e^{U_{air}} + e^{U_{train}}}")

    # 防止数值溢出或全0情况
    if U_air == 0 and U_train == 0:
        P_air, P_train = 0.5, 0.5
    else:
        try:
            exp_air = math.exp(U_air)
            exp_train = math.exp(U_train)
            P_air = exp_air / (exp_air + exp_train)
            P_train = exp_train / (exp_air + exp_train)
        except OverflowError:
            P_air = 1.0 if U_air > U_train else 0.0
            P_train = 1.0 - P_air

    # 显示计算结果
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.success(f"### ✈️ 民航分担率: {P_air:.2%}")
    with col_res2:
        st.success(f"### 🚄 高铁分担率: {P_train:.2%}")

# =====================================
# 主页面：设置标签页
# =====================================
tab1, tab2, tab3 = st.tabs(["🌟 长沙 - 上海", "🌟 上海 - 贵阳", "🌟 杭州 - 贵阳"])

with tab1:
    render_calculator("长沙", "上海", "cs_sh")

with tab2:
    render_calculator("上海", "贵阳", "sh_gy")

with tab3:
    render_calculator("杭州", "贵阳", "hz_gy")