import math

import streamlit as st


WORK_HOURS = 1984

OD_DATA = {
    "cs_sh": {
        "city1": "长沙",
        "city2": "上海",
        "income1": 66396,
        "income2": 91987,
        "air_price": 796.0,
        "rail_price": 527.5,
        "air_time": 5.0,
        "rail_time": 7.0,
        "real_p_air": 0.37,
        "models": {
            "总体模型（不剔除）": {
                "const": -0.395276,
                "beta_p": -0.627032,
                "beta_t": -0.511145,
                "vot": 81.518143,
            },
            "总体模型（剔除）": {
                "const": 0.224989,
                "beta_p": -1.082697,
                "beta_t": -0.839184,
                "vot": 77.508688,
            },
            "分 OD 模型（不剔除）": {
                "const": -0.960954,
                "beta_p": -0.675632,
                "beta_t": -0.759842,
                "vot": 112.463811,
            },
            "分 OD 模型（剔除）": {
                "const": -0.386790,
                "beta_p": -1.059731,
                "beta_t": -1.095673,
                "vot": 103.391569,
            },
        },
    },
    "sh_gy": {
        "city1": "上海",
        "city2": "贵阳",
        "income1": 91987,
        "income2": 47690,
        "air_price": 946.0,
        "rail_price": 803.0,
        "air_time": 6.0,
        "rail_time": 10.0,
        "real_p_air": 0.93,
        "models": {
            "总体模型（不剔除）": {
                "const": -0.395276,
                "beta_p": -0.627032,
                "beta_t": -0.511145,
                "vot": 81.518143,
            },
            "总体模型（剔除）": {
                "const": 0.224989,
                "beta_p": -1.082697,
                "beta_t": -0.839184,
                "vot": 77.508688,
            },
            "分 OD 模型（不剔除）": {
                "const": 0.750170,
                "beta_p": -0.515936,
                "beta_t": -0.221169,
                "vot": 42.867579,
            },
            "分 OD 模型（剔除）": {
                "const": 1.631045,
                "beta_p": -1.156767,
                "beta_t": -0.472329,
                "vot": 40.831793,
            },
        },
    },
}


st.set_page_config(layout="wide", page_title="空铁市场分担率计算系统")
st.title("空铁市场分担率计算系统")
st.markdown("---")


def input_with_reset(label, default_value, key, step=None, fmt=None):
    """带独立重置按钮的数字输入框"""
    c1, c2 = st.columns([10, 1])
    with c1:
        kwargs = {"key": key}
        if step is not None:
            kwargs["step"] = step
        if fmt is not None:
            kwargs["format"] = fmt
        if key not in st.session_state:
            kwargs["value"] = default_value
        value = st.number_input(label, **kwargs)
    with c2:
        st.write("")
        if st.button("↺", key=f"rst_{key}", help=f"恢复默认值: {default_value}"):
            st.session_state.pop(key, None)
            st.rerun()
    return value


def logit_share(u_air, u_train=0.0):
    if u_air == 0 and u_train == 0:
        return 0.5, 0.5

    try:
        exp_air = math.exp(u_air)
        exp_train = math.exp(u_train)
        p_air = exp_air / (exp_air + exp_train)
    except OverflowError:
        p_air = 1.0 if u_air > u_train else 0.0

    return p_air, 1.0 - p_air


def sync_model_defaults(uid, model_name, model):
    """模型切换时，把参数输入框同步到新模型默认值。"""
    active_key = f"active_model_{uid}"
    if st.session_state.get(active_key) == model_name:
        return

    for param in ("const", "beta_p", "beta_t"):
        st.session_state[f"{param}_{uid}"] = model[param]
    st.session_state[active_key] = model_name


def render_calculator(uid):
    data = OD_DATA[uid]
    city1 = data["city1"]
    city2 = data["city2"]

    st.header(f"1. 模型参数与 VOT - {city1} 到 {city2}")

    model_name = st.selectbox(
        "选择回归参数版本",
        list(data["models"].keys()),
        index=1,
        key=f"model_{uid}",
    )
    model = data["models"][model_name]
    sync_model_defaults(uid, model_name, model)

    rp_enabled = st.checkbox("RP修正", value=True, key=f"rp_{uid}",
                             help="启用后 ASC 由现实市占率校准；关闭后直接使用回归常数项")

    col_coef1, col_coef2, col_coef3, col_coef4 = st.columns(4)
    with col_coef1:
        const_input = input_with_reset("常数项 ASC", model["const"], key=f"const_{uid}", fmt="%.6f")
    with col_coef2:
        beta_p = input_with_reset("票价系数 beta_p", model["beta_p"], key=f"beta_p_{uid}", fmt="%.6f")
    with col_coef3:
        beta_t = input_with_reset("时间系数 beta_t", model["beta_t"], key=f"beta_t_{uid}", fmt="%.6f")
    col_coef4.metric("回归 VOT", f"{model['vot']:.2f} 元/小时")

    col_income1, col_income2, col_work, col_vot = st.columns(4)
    with col_income1:
        income1 = input_with_reset(f"{city1}人均可支配收入 (元/年)", data["income1"], key=f"income1_{uid}", step=100)
    with col_income2:
        income2 = input_with_reset(f"{city2}人均可支配收入 (元/年)", data["income2"], key=f"income2_{uid}", step=100)
    with col_work:
        work_hours = input_with_reset("年工作小时数", WORK_HOURS, key=f"work_{uid}", step=1)
    avg_income = (income1 + income2) / 2
    income_vot = avg_income / work_hours if work_hours > 0 else 0
    col_vot.metric("收入法 VOT", f"{income_vot:.2f} 元/小时")

    st.markdown("---")
    st.header("2. 出行属性默认值")

    col_air, col_train = st.columns(2)
    with col_air:
        st.subheader("民航 Air")
        with st.container(border=True):
            air_price = input_with_reset("全程票价 (元)", data["air_price"], key=f"air_price_{uid}", step=1.0)
            air_time = input_with_reset("门到门全程时间 (小时)", data["air_time"], key=f"air_time_{uid}", step=0.1)

    with col_train:
        st.subheader("高铁 Rail")
        with st.container(border=True):
            rail_price = input_with_reset("全程票价 (元)", data["rail_price"], key=f"rail_price_{uid}", step=1.0)
            rail_time = input_with_reset("门到门全程时间 (小时)", data["rail_time"], key=f"rail_time_{uid}", step=0.1)

    price_delta = air_price - rail_price
    time_delta = air_time - rail_time
    mean_price_delta = data["air_price"] - data["rail_price"]
    mean_time_delta = data["air_time"] - data["rail_time"]
    if rp_enabled:
        asc = math.log(data["real_p_air"] / (1 - data["real_p_air"])) - beta_p * (mean_price_delta / 100) - beta_t * mean_time_delta
    else:
        asc = const_input
    u_air = asc + beta_p * (price_delta / 100) + beta_t * time_delta
    p_air, p_train = logit_share(u_air)

    col_delta1, col_delta2 = st.columns(2)
    col_delta1.metric("票价差（民航-高铁）", f"{price_delta:.1f} 元")
    col_delta2.metric("时间差（民航-高铁）", f"{time_delta:.1f} 小时")

    st.markdown("---")
    st.header("3. 模型公式说明")
    st.latex(
        r"""
        \begin{align*}
        \Delta P &= P_{air} - P_{rail} \\
        \Delta T &= T_{air} - T_{rail} \\
        U_{air} &= ASC + \beta_p \cdot \frac{\Delta P}{100} + \beta_t \cdot \Delta T,\quad U_{rail}=0 \\
        P_{air} &= \frac{e^{U_{air}}}{e^{U_{air}} + e^{U_{rail}}},\quad P_{rail}=1-P_{air}
        \end{align*}
        """
    )

    st.markdown("---")
    st.header("4. 计算结果")

    col_u1, col_u2 = st.columns(2)
    col_u1.info(f"民航相对效用 U_air = **{u_air:.4f}**")
    col_u2.info("高铁基准效用 U_rail = **0.0000**")

    col_res1, col_res2 = st.columns(2)
    col_res1.success(f"### 民航分担率 {p_air:.2%}")
    col_res2.success(f"### 高铁分担率 {p_train:.2%}")


tab1, tab2 = st.tabs(["长沙 - 上海", "上海 - 贵阳"])

with tab1:
    render_calculator("cs_sh")

with tab2:
    render_calculator("sh_gy")
