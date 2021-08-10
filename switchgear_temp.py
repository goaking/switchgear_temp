# coding=utf-8
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse',False)

# 温升曲线函数
def func(x, τw, T):
    τ = τw * (1-np.exp(-x/T))
    return τ

# App 标题及说明
st.title('开关柜温升预警App')
st.write('此App用于判断开关柜在运行电流下的温升是否异常，及测温点接触电阻的变化情况')

# 选择开关柜额定电流
I_list = [1250]
Ie = st.sidebar.selectbox(
    "开关柜的额定电流是多少A？",
    I_list)

# 输入运行电流
current = st.sidebar.slider(label = '运行电流(A)', min_value = np.int(0.2 * Ie),
                          max_value = np.int(1.2 * Ie),
                          value = np.int(0.4 * Ie),
                          step = 1)

# 温度测量点选择
temp_measurement_list = ['断路器室上触头','母线室', '电缆室']
temp_measurement = st.sidebar.selectbox(
    "温度测量点位置？",
    temp_measurement_list)

# 输入测量点温升值
temp = st.sidebar.slider(label = '测量点温升K', min_value = 0.0,
                          max_value = 100.0,
                          value = 10.0,
                          step = 0.1)

# 输入信息列表展示
features = {'额定电流A': Ie,
            '运行电流A': current,
            '温度测量点': temp_measurement,
            '测量点温升K': '%.1f'%temp
            }
features_df = pd.DataFrame([features])
st.table(features_df)

# 标准状态下的参数计算
xx = np.linspace(0, 800, 801)
τw = 0.0
T = 0.0
if temp_measurement =='母线室':
    τw = 39.3 * np.power(current/1000.0, 1.7)
    T = 36.39 * np.power(current/1000.0, 2) - 92.14 * current/1000.0 + 129.7
elif temp_measurement =='断路器室上触头':
    τw = 43.0 * np.power(current/1000.0, 1.6)
    T = 136.4 * np.power(current/1000.0, 2) - 310.8 * current/1000.0 + 269.5
else:
    τw = 26.1 * np.power(current/1000.0, 1.9)
    T = 14.67 * np.power(current/1000.0, 2) - 45.38 * current/1000.0 + 114.2

# 电阻增加1.2倍后参数计算
τw_R = 1.16 * τw
T_R = 0.96 * T

# 输出
if st.button('开始'):
    # 绘图和点
    fig = plt.figure(figsize=(10, 5))
    plt.plot(xx, func(xx, τw, T), 'g-', label='1.0R:Standard temp curve')
    plt.plot(xx, func(xx, τw_R, T_R), 'm-', label='1.2R:Warning temp curve')
    plt.plot(xx, 0*xx+65, 'r-', label='65K:temp limit line')
    plt.scatter(700, temp, marker='*', color='r', label='Current position', linewidth=1)
    plt.xlabel('min')
    plt.ylabel('K')
    plt.legend(loc=2)
    st.pyplot()

    # 数值计算
    temp_delta = np.round(temp - τw,1)
    R_rate = np.round(np.power(temp/τw, 1.25),1)*100
    st.write(' 监测点温升相对于标准温升的增加值：' + str(temp_delta) + 'K')
    st.write(' 监测点电阻相对于标准电阻的变化率：' + str(R_rate) + '%')
