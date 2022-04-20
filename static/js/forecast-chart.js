// 预测页面js

// 刷新
function forecastClick() {
    forecastButtonClick()
}

// 省-城市二级联动
(function () {
    $.ajax({
        url: "http://127.0.0.1:5000/china/province/cities/json",
        type: "get",
        dataType: "json",
        success: function (retJson) {
            renderList(retJson)
        }
    })

    function renderList(jsonObj) {
        var allProvinces = jsonObj.provinces
        // 得到所有省份的数据

        $("#forecastProvince").empty()

        // 这里利用forEach循环添加省份的数据
        allProvinces.forEach(function (element) {
            var option = $(`<option value="${element.name}">${element.name}</option>`)
            // option.appendTo("#province")
            $("#forecastProvince").append(option)
        });

        // 给省份的选择框添加change事件
        $("#forecastProvince").change(function () {
            var curProvince = $("#forecastProvince>option:selected").val();
            // 得到当前选中的省份的val值

            var selectedProvince = allProvinces.find(function (curElement, index) {
                // find() 方法获得当前元素集合中每个元素的后代，通过选择器、jQuery 对象或元素来筛选。

                return curElement.name == curProvince;
                // 将当前选中省份的名字返回给 selectedProvince
            })

            var allCities = selectedProvince.cities;
            // allCities指当前被选中省份下的所有城市

            $("#forecastCity").empty()
            // select之前选中显示的文本还残留在select框里，为了去掉残留的文本，需要清空城市选择框的内容

            // 这里利用forEach循环添加城市的数据
            allCities.forEach(function (element) {
                var option = $(`<option value="${element.name}">${element.name}</option>`)
                option.appendTo("#forecastCity");
            });
        })

        $("#forecastProvince").triggerHandler("change");
        // 这个方法将会触发指定的事件类型上所有绑定的处理函数。但不会执行浏览器默认动作，也不会产生事件冒泡。
    }
})();


// 下拉框选择预测天数
(function () {
    $("#forecastNums").empty()

    for (var i = 1; i <= 7; i++) {
        var option = $(`<option value="${i}">${i}</option>`)
        $("#forecastNums").append(option)
    }
})();

// 时间标签的支持的时间段设置
(function () {
    $.ajax({
        url: 'http://127.0.0.1:5000/forecast/china/time',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            startTime = data.start_time
            endTime = data.end_time
            var tagStartTime = document.getElementById("startTime")
            var tagEndTime = document.getElementById("endTime")
            // 设置时间标签的初始值、可选择范围
            tagStartTime.value = startTime
            tagStartTime.min = startTime
            tagStartTime.max = endTime
            tagEndTime.value = endTime
            tagEndTime.min = startTime
            tagEndTime.max = endTime
        }
    })
})();

var src_png_list;

// 点击确认按钮后查询该省各城市数据（地图）、该省每日数据趋势（折线图）、该省累计确诊前五的数据（丁格尔玫瑰图）
function forecastButtonClick() {
    // 获取省份
    var province = document.getElementById("forecastProvince")
    // 获取城市（目前没有使用）
    var city = document.getElementById("forecastCity")
    var provinceName = province.options[province.selectedIndex].text

    // 选择的时间返回获取
    var tagStartTime = document.getElementById("startTime")
    var tagEndTime = document.getElementById("endTime")
    var startTime = tagStartTime.value
    var endTime = tagEndTime.value

    // 预测多少天
    var forecastNums = document.getElementById("forecastNums").value
    console.log(forecastNums)

    var params = {
        "province": provinceName,
        "startTime": startTime,
        "endTime": endTime,
        "forecastNums": forecastNums
    }

    // 预测省份数据
    $.ajax({
        url: 'http://127.0.0.1:5000/forecast/china/province',
        type: 'get',
        data: params,
        dataType: 'json',
        success: function (data) {
            var myChart = echarts.init(document.querySelector('.forecastLine .chart'))
            var option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: {
                            backgroundColor: '#6a7985'
                        }
                    }
                },
                //图例
                legend: {
                    top: "0%",
                    //图例字体样式
                    textStyle: {
                        color: "rgba(255,255,255,.5)",
                        fontSize: "12"
                    }
                },
                // 坐标系
                grid: {
                    left: "10",
                    top: "30",
                    right: "10",
                    bottom: "10",
                    //文字标注算入
                    containLabel: true
                },
                xAxis: [{
                    type: 'category',
                    boundaryGap: false,
                    // data: ['二月', '三月', '四月', '五月', '六月'],
                    // 文本颜色为rgba(255,255,255,.6)  文字大小为 12
                    axisLabel: {
                        textStyle: {
                            color: "rgba(255,255,255,.6)",
                            fontSize: 12
                        }
                    },
                    // x轴线的颜色为   rgba(255,255,255,.2)
                    axisLine: {
                        lineStyle: {
                            color: "rgba(255,255,255,.2)"
                        }
                    },
                }],
                yAxis: [{
                    type: 'value',
                    //隐藏坐标轴刻度
                    axisTick: {show: false},
                    //标注y轴线样式
                    axisLine: {
                        lineStyle: {
                            color: "rgba(255,255,255,.1)"
                        }
                    },
                    //标注文本
                    axisLabel: {
                        textStyle: {
                            color: "rgba(255,255,255,.6)",
                            fontSize: 8
                        }
                    },
                    // 修改分割线的颜色
                    splitLine: {
                        lineStyle: {
                            color: "rgba(255,255,255,.1)"
                        }
                    }
                }],
                //主题样式设计
                series: [
                    {
                        name: '累计确诊',
                        type: 'line',
                        // stack: '总量', //数据堆叠
                        // data: [220, 182, 191, 234, 290, 330, 310],
                        //线圆滑
                        smooth: true,
                        // 单独修改线的样式
                        lineStyle: {
                            color: "#0184d5",
                            width: 2
                        },
                        // 填充区域
                        areaStyle: {
                            // 渐变色
                            color: new echarts.graphic.LinearGradient(
                                0,
                                0,
                                0,
                                1,
                                [{
                                    offset: 0,
                                    color: "rgba(1, 132, 213, 0.4)" // 渐变色的起始颜色
                                },
                                    {
                                        offset: 0.8,
                                        color: "rgba(1, 132, 213, 0.1)" // 渐变线的结束颜色
                                    }
                                ],
                                false
                            ),
                            shadowColor: "rgba(0, 0, 0, 0.1)" //阴影颜色
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 8,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#0184d5",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        //开始不显示坐标圆点
                        showSymbol: false,
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "预测累计确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#ffdb5c",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#ffdb5c",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "累计治愈",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#00FF7F",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#00FF7F",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "预测累计治愈",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#800080",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#800080",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "累计死亡",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#c71b1b",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#c71b1b",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "预测累计死亡",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#FF69B4",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#FF69B4",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "现有确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#FF00FF",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#FF00FF",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "预测现有确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#DDA0DD",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#DDA0DD",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "较昨日确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#FF69B4",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#FF69B4",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    },
                    {
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        name: "预测较昨日确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#7B68EE",
                                width: 2
                            }
                        },
                        areaStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    [{
                                        offset: 0,
                                        color: "rgba(0, 216, 135, 0.4)"
                                    },
                                        {
                                            offset: 0.8,
                                            color: "rgba(0, 216, 135, 0.1)"
                                        }
                                    ],
                                    false
                                ),
                                shadowColor: "rgba(0, 0, 0, 0.1)"
                            }
                        },
                        // 设置拐点 小圆点
                        symbol: "circle",
                        // 拐点大小
                        symbolSize: 5,
                        // 设置拐点颜色以及边框
                        itemStyle: {
                            color: "#7B68EE",
                            borderColor: "rgba(221, 220, 107, .1)",
                            borderWidth: 12
                        },
                        // 开始不显示拐点， 鼠标经过显示
                        showSymbol: false,
                        // data: [120, 132, 101, 134, 90, 230, 210]
                        // stack: '总量',
                    }
                ]
            };
            // 把配置和数据给实例对象
            myChart.setOption(option);

            var confirmHistory = []
            var confirmForecast = []
            var healHistory = []
            var healForecast = []
            var deadHistory = []
            var deadForecast = []
            var nowConfirmHistory = []
            var nowConfirmForecast = []
            var confirmCompareHistory = []
            var confirmCompareForecast = []
            var date = []

            data.data.forEach(item => {
                confirmHistory.push(item.confirm)
                confirmForecast.push(item.confirm_forecast)
                healHistory.push(item.heal)
                healForecast.push(item.heal_forecast)
                deadHistory.push(item.dead)
                deadForecast.push(item.dead_forecast)
                nowConfirmHistory.push(item.now_confirm)
                nowConfirmForecast.push(item.now_confirm_forecast)
                confirmCompareHistory.push(item.confirm_compare > 0 ? "+" + item.confirm_compare : item.confirm_compare)
                confirmCompareForecast.push(item.confirm_compare_forecast > 0 ? "+" + item.confirm_compare_forecast : item.confirm_compare_forecast)
                date.push(item.date_time)
            })


            //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
            myChart.setOption({ //加载数据图表
                series: [{
                    data: confirmHistory
                }, {
                    data: confirmForecast
                }, {
                    data: healHistory
                }, {
                    data: healForecast
                }, {
                    data: deadHistory
                }, {
                    data: deadForecast
                }, {
                    data: nowConfirmHistory
                }, {
                    data: nowConfirmForecast
                }, {
                    data: confirmCompareHistory
                }, {
                    data: confirmCompareForecast
                }],
                xAxis: [{
                    data: date
                }]
            })

            window.addEventListener('resize', function () {
                myChart.resize()
            })


            // 左下table常数、系数显示
            var item = data.data[0]
            var linearRegressions = [
                {
                    "name": "预测累计确诊",
                    "a": item.confirm_forecast_a,
                    "b": item.confirm_forecast_b
                },
                {
                    "name": "预测累计治愈",
                    "a": item.heal_forecast_a,
                    "b": item.heal_forecast_b
                },
                {
                    "name": "预测累计死亡",
                    "a": item.dead_forecast_a,
                    "b": item.dead_forecast_b
                },
                {
                    "name": "预测现有确诊",
                    "a": item.now_confirm_forecast_a,
                    "b": item.now_confirm_forecast_b
                },
                {
                    "name": "预测较昨日确诊",
                    "a": item.confirm_compare_forecast_a,
                    "b": item.confirm_compare_forecast_b
                },
            ]

            // 左下回归方程系数
            $('#forecastLinearRegression').html("")
            tableHead = "<tr><th id='tableHeadLine' style='background-color: rgba(255, 145, 0, 0.7);'><span style=\"float:left;\">类型</span><span style=\"float:right;\">名称</span></th><th>常数a</th><th>系数b</th></tr>"
            $('#forecastLinearRegression').append(tableHead);
            linearRegressions.forEach(lr => {
                item = "<tr><td><h4>" + lr.name + "</h4></td><td>" + lr.a + "</td><td>" + lr.b + "</td></tr>";
                $('#forecastLinearRegression').append(item);
            })

            // 下拉框选择图片
            src_png_list = data.src_png
            $("#forecastPng").empty()
            data.src_png.forEach(src_dict => {
                var option = $(`<option value="${src_dict.src_name}">${src_dict.src_name}</option>`)
                $("#forecastPng").append(option)
            })

            // 图片
            $('#forecastBar1').html("")
            $('#forecastBar1').append("<img src=\"" + data.src_png[0].src + "\"/>")
        }
    })

}


// 选择图片下拉框
function forecastPngButtonClick() {
    // 获取下拉框
    var forecastPng = document.getElementById("forecastPng")
    var name_png = forecastPng.options[forecastPng.selectedIndex].text
    src_png_list.forEach(src_dict => {
        if (src_dict.src_name === name_png) {
            $('#forecastBar1').html("")
            $('#forecastBar1').append("<img src=\"" + src_dict.src + "\"/>")
        }
    })
}
