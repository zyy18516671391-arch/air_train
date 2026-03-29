import streamlit as st
import math

st.set_page_config(layout="wide")
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

    # 1️⃣ 出行时间成本计算
    st.header("1️⃣ 出行时间成本计算")

    st.markdown("### 单位时间价值计算公式：")
    st.latex(r"""
    VOT = \frac{W}{H}
    """)

    st.markdown("""
    其中：
    - \(W\)：平均人均可支配收入  
    - \(H\)：年工作时间  
    """)

    col_city1, col_city2, col_work = st.columns(3)
    with col_city1:
        city1 = st.text_input("城市1名称", default_city1, key=f"city1_{uid}")
        income1 = float(st.text_input(f"{city1} 人均可支配收入", "0", key=f"inc1_{uid}"))
    with col_city2:
        city2 = st.text_input("城市2名称", default_city2, key=f"city2_{uid}")
        income2 = float(st.text_input(f"{city2} 人均可支配收入", "0", key=f"inc2_{uid}"))
    with col_work:
        work_hours = float(st.text_input("年工作小时数", "1984", key=f"work_{uid}"))

    avg_income = (income1 + income2) / 2
    # 防止除以0报错
    unit_time_cost = avg_income / work_hours if work_hours > 0 else 0

    st.success(f"平均收入 W = {avg_income:.2f}")
    st.success(f"单位时间价值 VOT = {unit_time_cost:.2f} 元/小时")

    # 2️⃣ 指标计算
    st.header("2️⃣ 指标计算（民航 vs 高铁）")

    col1, col2 = st.columns(2)

    # ================= 民航 =================
    with col1:
        st.subheader("✈️ 民航")

        # -------- 经济性 --------
        st.markdown("### 经济性")
        st.latex(r"C_{air}=P_{air}")
        price_air = float(st.text_input("票价", "0", key=f"price_air_{uid}"))
        st.info(f"经济性成本 = {price_air:.2f}")

        # -------- 快速性 --------
        st.markdown("### 快速性")
        st.latex(r"T_{air} = (t_1 + t_2 + t_3) \times VOT")

        t1_air = float(st.text_input("安检值机时间", "1", key=f"t1_air_{uid}"))
        t2_air = float(st.text_input("飞行时间", "0", key=f"t2_air_{uid}"))
        t3_air = float(st.text_input("离开机场时间", "0.5", key=f"t3_air_{uid}"))

        time_air = (t1_air + t2_air + t3_air) * unit_time_cost
        st.info(f"时间成本 = {time_air:.2f}")

        # -------- 便捷性 --------
        st.markdown("### 便捷性")
        st.latex(r"A_{air} = (a_1 + a_2) \times VOT")

        access_air_1 = float(st.text_input("前往机场时间", "0", key=f"acc1_air_{uid}"))
        access_air_2 = float(st.text_input("机场到目的地时间", "0", key=f"acc2_air_{uid}"))

        access_air = (access_air_1 + access_air_2) * unit_time_cost
        st.info(f"接驳成本 = {access_air:.2f}")

        # -------- 舒适性 --------
        st.markdown("### 舒适性")
        st.latex(r"F_{air} = \frac{L}{1 + \alpha e^{-\beta t}} \times VOT")

        L_air = float(st.text_input("极限恢复时间 L", "16", key=f"L_air_{uid}"))
        alpha_air = float(st.text_input("α", "79", key=f"alpha_air_{uid}"))
        beta_air = float(st.text_input("β", "0.25", key=f"beta_air_{uid}"))

        def fatigue(t, alpha, beta, L):
            return L / (1 + alpha * math.exp(-beta * t))

        fatigue_air_val = fatigue(t2_air, alpha_air, beta_air, L_air)
        comfort_air = fatigue_air_val * unit_time_cost
        st.info(f"疲劳成本 = {comfort_air:.2f}")

    # ================= 高铁 =================
    with col2:
        st.subheader("🚄 高铁")

        # -------- 经济性 --------
        st.markdown("### 经济性")
        st.latex(r"C_{train} = P_{train}")
        price_train = float(st.text_input("票价", "0", key=f"price_train_{uid}"))
        st.info(f"经济性成本 = {price_train:.2f}")

        # -------- 快速性 --------
        st.markdown("### 快速性")
        st.latex(r"T_{train} = (t_1 + t_2 + t_3) \times VOT")

        t1_train = float(st.text_input("进站时间", "0.5", key=f"t1_train_{uid}"))
        t2_train = float(st.text_input("运行时间", "0", key=f"t2_train_{uid}"))
        t3_train = float(st.text_input("出站时间", "0.25", key=f"t3_train_{uid}"))

        time_train = (t1_train + t2_train + t3_train) * unit_time_cost
        st.info(f"时间成本 = {time_train:.2f}")

        # -------- 便捷性 --------
        st.markdown("### 便捷性")
        st.latex(r"A_{train} = (a_1 + a_2) \times VOT")

        access_train_1 = float(st.text_input("前往车站时间", "0", key=f"acc1_train_{uid}"))
        access_train_2 = float(st.text_input("车站到目的地时间", "0", key=f"acc2_train_{uid}"))

        access_train = (access_train_1 + access_train_2) * unit_time_cost
        st.info(f"接驳成本 = {access_train:.2f}")

        # -------- 舒适性 --------
        st.markdown("### 舒适性")
        st.latex(r"F_{train} = \frac{L}{1 + \alpha e^{-\beta t}} \times VOT")

        L_train = float(st.text_input("极限恢复时间 L", "16", key=f"L_train_{uid}"))
        alpha_train = float(st.text_input("α", "59", key=f"alpha_train_{uid}"))
        beta_train = float(st.text_input("β", "0.29", key=f"beta_train_{uid}"))

        fatigue_train_val = fatigue(t2_train, alpha_train, beta_train, L_train)
        comfort_train = fatigue_train_val * unit_time_cost
        st.info(f"疲劳成本 = {comfort_train:.2f}")

    # 3️⃣ 效用函数构建
    st.header("3️⃣ 效用函数构建")

    st.markdown("### 效用函数形式：")
    st.latex(r"""
    U_i = - ( \beta_1 C_i + \beta_2 T_i + \beta_3 A_i + \beta_4 F_i )
    """)

    st.markdown("""
    其中：
    - \(C\)：经济性（票价）
    - \(T\)：快速性（时间成本）
    - \(A\)：便捷性（接驳成本）
    - \(F\)：舒适性（疲劳成本）
    """)

    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    with col_w1:
        w_price = float(st.text_input("经济性权重 β1", "0", key=f"w1_{uid}"))
    with col_w2:
        w_time = float(st.text_input("快速性权重 β2", "0", key=f"w2_{uid}"))
    with col_w3:
        w_access = float(st.text_input("便捷性权重 β3", "0", key=f"w3_{uid}"))
    with col_w4:
        w_comfort = float(st.text_input("舒适性权重 β4", "0", key=f"w4_{uid}"))

    U_air = -(w_price * price_air + w_time * time_air + w_access * access_air + w_comfort * comfort_air)
    U_train = -(w_price * price_train + w_time * time_train + w_access * access_train + w_comfort * comfort_train)

    st.success(f"✈️ 民航效用: {U_air:.2f}")
    st.success(f"🚄 高铁效用: {U_train:.2f}")

    st.divider()

    # 4️⃣ 分担率计算
    st.header("4️⃣ 分担率计算（Logit模型）")

    st.markdown("### 概率公式：")
    st.latex(r"""
    P_i = \frac{e^{U_i}}{e^{U_{air}} + e^{U_{train}}}
    """)

    # 防止数值溢出，当U都为0时，平分概率
    if U_air == 0 and U_train == 0:
        P_air = 0.5
        P_train = 0.5
    else:
        try:
            exp_air = math.exp(U_air)
            exp_train = math.exp(U_train)
            P_air = exp_air / (exp_air + exp_train)
            P_train = exp_train / (exp_air + exp_train)
        except OverflowError:
            # 极端情况处理（如果权重没调好导致数值过大）
            P_air = 1.0 if U_air > U_train else 0.0
            P_train = 1.0 - P_air

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.success(f"✈️ 民航分担率: **{P_air:.2%}**")
    with col_res2:
        st.success(f"🚄 高铁分担率: **{P_train:.2%}**")


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