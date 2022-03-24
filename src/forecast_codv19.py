# -*- coding: UTF-8 -*-

import copy

import matplotlib.pyplot as plt
from sklearn import linear_model


# from sklearn.model_selection import train_test_split


def forecast(df, feature_nums):
    """
    sklearn 一元线性回归模型
    :param df: 训练数据
    :param feature_nums 预测未来几天的
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
    graphic_drawing(x, y, x_test_list, y_pred_list, feature_nums)

    # 分别是常熟a（保留两位小数）、系数b（保留两位小数）、横坐标x列表、预测值y列表（向下取整）
    return round(model.intercept_[0], 2), \
           round(model.coef_[0][0], 2), \
           list(map(lambda v: v[0], x_test_list)), \
           list(map(lambda v: int(v[0]), y_pred_list))


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


def graphic_drawing(x_original, y_original, x_test_list, y_pred_list, feature_nums):
    """
    根据历史数据和预测数据绘图
    :param x_original:
    :param y_original:
    :param x_test_list:
    :param y_pred_list:
    :param feature_nums
    :return:
    """
    plt = get_plt()

    # 历史数据散点
    plt.plot(x_original, y_original, 'k.')

    # 预测数据散点
    plt.scatter(x_test_list[-1 * feature_nums:], y_pred_list[-1 * feature_nums:], color='blue')

    # 通过回归方程的值绘线
    plt.plot(x_test_list, y_pred_list, 'r')
    plt.show()

#
# def forecast(df):
#     """
#     sklearn 一元线性回归模型
#     :param df: 训练数据
#     :return: 预测结果
#     """
#     # 第一列的所有行
#     x = df.iloc[:, : 1].values
#     # 第二列的所有行
#     y = df.iloc[:, 1].values
#
#     # 1、拆分训练集和测试集, 拆分训练:测试量数据 比值为3:1
#     x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=1 / 4, random_state=0)
#
#     # 2、用简单线性回归模型拟合训练集
#     regression = linear_model.LinearRegression()
#     regression = regression.fit(x_train, y_train)
#
#     # 3、预测结果
#     y_pred = regression.predict(x_test)
#
#     # 可视化训练集预测结果
#     # 散点图
#     plt.scatter(x_train, y_train, color='red')
#     plt.plot(x_train, regression.predict(x_train), color='blue')
#
#     # 可视化测试集预测结果
#     plt.scatter(x_test, y_test, color='yellow')
#     plt.plot(x_test, y_pred, color='black')
#     plt.show()
#
#     return y_pred
