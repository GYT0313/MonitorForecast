# -*- coding: UTF-8 -*-
import base64
import copy
from io import BytesIO

import matplotlib.pyplot as plt
from sklearn import linear_model


# from sklearn.model_selection import train_test_split


def forecast(df, feature_nums, forecast_name):
    """
    sklearn 一元线性回归模型
    :param df: 训练数据
    :param feature_nums 预测未来几天的
    :param forecast_name  预测的数据名称
    :return: # 分别是常熟a、系数b、横坐标x列表、预测值y列表
    """
    """
    sklearn 一元线性回归模型
    :param df: 训练数据
    :return: 预测结果
    """
    model = linear_model.LinearRegression()

    # 示例: x = [[1], [2], [3]]
    x = list(df['x'].apply(lambda v: [v]))
    y = list(df['y'].apply(lambda v: [v]))

    # 使用一元线性模型
    model.fit(x, y)

    # 截距 常数a
    print(model.intercept_[0])
    # 线性模型的系数 系数b
    print(model.coef_[0][0])

    # 预测, x为最后的值+1, 即时间返回end_time的第二天、三天...
    x_pred = []
    for i in range(1, feature_nums + 1):
        x_pred.append(x[-1][0] + i)

    # 使用预测模型预测历史数据和将来数据x_test_list] 为将来的自变量x(意义上的未来某一天)
    x_test_list = copy.deepcopy(x)
    for v in x_pred:
        x_test_list.append([v])
    y_pred_list = model.predict(x_test_list)

    # 使用历史数据、预测数据绘制图形
    src = graphic_drawing(x, y, x_test_list, y_pred_list, feature_nums, forecast_name)

    # 分别是常熟a（保留两位小数）、系数b（保留两位小数）、横坐标x列表、预测值y列表（向下取整）
    return round(model.intercept_[0], 2), \
           round(model.coef_[0][0], 2), \
           list(map(lambda v: v[0], x_test_list)), \
           list(map(lambda v: int(v[0]), y_pred_list)), \
           {
               "src_name": forecast_name,
               "src": src
           }


def get_plt(size=None):
    """
    图形
    :param size:
    :return:
    """
    plt.figure(figsize=size)
    plt.title('cod-v19 forecast')
    plt.xlabel('x')
    plt.ylabel('y')
    # plt.axis([0, 25, 0, 25])
    plt.grid(True)
    return plt


def graphic_drawing(x_original, y_original, x_test_list, y_pred_list, feature_nums, forecast_name):
    """
    根据历史数据和预测数据绘图
    :param x_original:
    :param y_original:
    :param x_test_list:
    :param y_pred_list:
    :param feature_nums
    :param forecast_name
    :return:
    """
    plt = get_plt()
    # 大小、中文设置
    plt.figure(figsize=(7, 4), dpi=70)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

    # 历史数据散点
    plt.plot(x_original, y_original, 'k.')

    # 预测数据散点
    plt.scatter(x_test_list[-1 * feature_nums:], y_pred_list[-1 * feature_nums:], color='blue')

    plt.title(forecast_name)
    plt.xlabel("时间")
    plt.ylabel("数量/人")
    plt.grid()

    # 通过回归方程的值绘线
    plt.plot(x_test_list, y_pred_list, 'r')
    # plt.show()
    sio = BytesIO()
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    sio.seek(0)  # rewind to beginning of file
    data = base64.b64encode(sio.getvalue())
    img_str = str(data, "utf-8")
    # # 记得关闭，不然画出来的图是重复的
    plt.close()
    return "data:image/JPEG;base64,{}".format(img_str)
