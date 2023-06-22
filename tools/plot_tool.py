import uuid
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_chart(data: Any, title: str, chart_type: str, plot_image: bool = True) -> str:
    unique_filename = "images/" + str(uuid.uuid4())[:8] + '.png'
    if not plot_image: return unique_filename
    # 创建新的图表
    fig, ax = plt.subplots()

    x_data = pd.to_datetime(data['日期']).dt.strftime("%Y-%m-%d")
    y_data = data.drop('日期', axis=1)
    bar_width = 0.8 / len(y_data.keys())
    x_offsets = np.arange(len(x_data)) - (0.8 / 2) + bar_width / 2

    if chart_type == 'line':
        # 绘制折线图
        for i, (k, v) in enumerate(y_data.items()):
            ax.plot(x_data, v.values, 'o-', label=k)
        ax.set_xticks(np.arange(len(x_data)), data['日期'].values)
        ax.set_xticklabels(x_data, rotation=45)
    elif chart_type == 'bar':
        # 绘制柱状图
        for i, (k, v) in enumerate(y_data.items()):
            rects = ax.bar(x_offsets + i * bar_width, v.values, bar_width, label=k)
            ax.bar_label(rects, padding=3)
        ax.set_xticks(np.arange(len(x_data)), data['日期'].values, rotation=45, fontsize=8)
        ax.set_xticklabels(x_data, rotation=45)
    elif chart_type == 'scatter':
        # 绘制散点图
        for i, (k, v) in enumerate(y_data.items()):
            ax.scatter(v.values, label=k)
    elif chart_type == 'pie':
        # 绘制饼图
        ax.pie(y_data.sum().values, labels=y_data.keys(), autopct='%1.1f%%')
    else:
        # 未知图表类型
        plt.close(fig)
        return "sorry, can only plot this pie, line, bar, scatter chart."

    if chart_type != "pie":
        ax.legend(loc="best")
    ax.set_title(title)
    ax.tick_params(axis='x', labelsize=8)
    plt.savefig(unique_filename)
    plt.close(fig)

    return unique_filename
