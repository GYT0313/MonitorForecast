// 中国城市页面js
// 刷新
function provinceClick() {
    buttonClick()
}

// 省-城市二级联动
(function () {
    $.ajax({
        url: "http://127.0.0.1:5000/china/province/city/json",
        type: "get",
        dataType: "json",
        success: function (retJson) {
            renderList(retJson)
        }
    })

    function renderList(jsonObj) {
        var allProvinces = jsonObj.provinces
        // 得到所有省份的数据

        $("#province").empty()

        // 这里利用forEach循环添加省份的数据
        allProvinces.forEach(function (element) {
            var option = $(`<option value="${element.name}">${element.name}</option>`)
            // option.appendTo("#province")
            $("#province").append(option)
        });

        // 给省份的选择框添加change事件
        $("#province").change(function () {
            var curProvince = $("#province>option:selected").val();
            // 得到当前选中的省份的val值

            var selectedProvince = allProvinces.find(function (curElement, index) {
                // find() 方法获得当前元素集合中每个元素的后代，通过选择器、jQuery 对象或元素来筛选。

                return curElement.name == curProvince;
                // 将当前选中省份的名字返回给 selectedProvince
            })

            var allCities = selectedProvince.cities;
            // allCities指当前被选中省份下的所有城市

            $("#city").empty()
            // select之前选中显示的文本还残留在select框里，为了去掉残留的文本，需要清空城市选择框的内容

            // 这里利用forEach循环添加城市的数据
            allCities.forEach(function (element) {
                var option = $(`<option value="${element.name}">${element.name}</option>`)
                option.appendTo("#city");
            });
        })

        $("#province").triggerHandler("change");
        // 这个方法将会触发指定的事件类型上所有绑定的处理函数。但不会执行浏览器默认动作，也不会产生事件冒泡。
    }
})();

// 点击确认按钮后查询该省各城市数据（地图）、该省每日数据趋势（折线图）、该省累计确诊前五的数据（丁格尔玫瑰图）
function buttonClick() {
    var province = document.getElementById("province")
    var city = document.getElementById("city")
    var provinceName = province.options[province.selectedIndex].text
    var cityName = city.options[city.selectedIndex].text

    var params = {
        "province": provinceName,
        "city": cityName
    }
    // 地图json与名称需要匹配
    var specialMap = {
        "内蒙古": "自治区",
        "西藏": "自治区",
        "宁夏": "回族自治区",
        "广西": "壮族自治区",
        "新疆": "维吾尔自治区",
        "香港": "特别行政区",
        "澳门": "特别行政区",
        "上海": "市",
        "北京": "市",
        "天津": "市",
        "重庆": "市",
    }
    // 拼接
    provinceName = specialMap[provinceName] != null ? provinceName + specialMap[provinceName] : provinceName + "省";


    // 中间累计数据
    $.ajax({
        url: 'http://127.0.0.1:5000/china/province/new',
        type: 'get',
        data: params,
        dataType: 'json',
        success: function (data) {
            $(".no-hd-province li:first").text(data.confirm)
            $(".no-hd-province li:nth-child(2)").text(data.heal)
            $(".no-hd-province li:nth-child(3)").text(data.now_confirm)
            $(".no-hd-province li:nth-child(4)").text(data.dead)
        }
    })


    // 该省各城市数据（地图）
    $.get('../static/js/map/province/' + provinceName + '.json', function (mapJson) {
        echarts.registerMap(provinceName, mapJson)
        var myChart = echarts.init(document.querySelector('.provinceMap .chart'))
        var option = {
            title: {
                text: provinceName + '各城市确诊情况',
                // subtext: '累计确诊人数',
                left: 'center',
                textStyle: {
                    color: 'white'
                },
                top: 'top'
            },
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    return params.data.name + "</br>" +
                        "累计确诊: " + params.data.confirm + "</br>" +
                        "累计治愈: " + params.data.heal + "</br>" +
                        "累计死亡: " + params.data.dead + "</br>" +
                        "现有确诊: " + params.data.now_confirm + "</br>" +
                        "较昨日确诊: " + (params.data.confirm_compare > 0 ? '+' + params.data.confirm_compare : params.data.confirm_compare);
                }
            },
            visualMap: {
                show: true,
                min: 0,
                max: 150,
                text: ['High', 'Low'],
                realtime: false,
                calculable: false,
                textStyle: {
                    color: 'white'
                },
                color: ['#481380', '#7f78d2', '#efb1ff', '#ffe2ff']
            },
            series: [
                {
                    name: '累计确诊人数',
                    type: 'map',
                    mapType: provinceName,
                    roam: true,
                    itemStyle: {
                        normal: {
                            areaColor: '#fce8d5',
                            borderColor: 'rgb(0,108,255)',
                        },
                        emphasis: {
                            label: {
                                show: true,
                                color: 'black'
                            },
                            areaColor: '#fce8d5'
                        }
                    }

                    // nameMap: nameMap,
                    // data:
                }]
        };
        // 把配置和数据给实例对象
        myChart.setOption(option);
        var virus = []
        $.ajax({
            url: 'http://127.0.0.1:5000/china/province/city',
            type: 'get',
            data: params,
            dataType: 'json',
            success: function (data) {
                data.forEach(item => {
                    virus.push({
                        // 用于visualMap与地图区域对应
                        'name': item.name,
                        'confirm': item.confirm,
                        'heal': item.heal,
                        'dead': item.dead,
                        'now_confirm': item.now_confirm,
                        'confirm_compare': item.confirm_compare,
                        // 用于visualMap筛选, 颜色显示
                        'value': item.confirm
                    })
                })
                myChart.setOption({ //加载数据图表
                    series: [{
                        // 根据名字对应到相应的系列
                        data: virus
                    }]
                })
            }
        });
        window.addEventListener('resize', function () {
            myChart.resize()
        })
    })


    //  省每日疫情趋势
    $.ajax({
        url: 'http://127.0.0.1:5000/china/province/daily',
        type: 'get',
        data: params,
        dataType: 'json',
        success: function (data) {
            var myChart = echarts.init(document.querySelector('.provinceLine .chart'))
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
                series: [{
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
                        name: "累计治愈",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#37a2da",
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
                            color: "#37a2da",
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
                        name: "现有确诊",
                        type: "line",
                        smooth: true,
                        lineStyle: {
                            normal: {
                                color: "#ff9f7f",
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
                            color: "#ff9f7f",
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
                                color: "#fb7293",
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
                            color: "#fb7293",
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


            var confirmCompareCount = []
            var healCompareCount = []
            var deadCompareCount = []
            var nowConfirmCompareCount = []
            var confirm_compareCount = []
            var date = []

            data.forEach(item => {
                confirmCompareCount.push(item.confirm)
                healCompareCount.push(item.heal)
                deadCompareCount.push(item.dead)
                nowConfirmCompareCount.push(item.now_confirm)
                confirm_compareCount.push(item.confirm_compare > 0 ? '+' + item.confirm_compare : item.confirm_compare)
                date.push(item.date_time)
            })


            //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
            myChart.setOption({ //加载数据图表
                series: [{
                    data: confirmCompareCount
                }, {
                    data: healCompareCount
                }, {
                    data: deadCompareCount
                }, {
                    data: nowConfirmCompareCount
                }, {
                    data: confirm_compareCount
                }],
                xAxis: [{
                    data: date
                }]
            })

            window.addEventListener('resize', function () {
                myChart.resize()
            })
        }
    })


    // 该省累计确诊前15的数据（丁格尔玫瑰图）
    $.ajax({
        // 丁格尔玫瑰图
        url: 'http://127.0.0.1:5000/china/province/city/head',
        type: 'get',
        data: params,
        dataType: 'json',
        success: function (data) {
            // 基于准备好的dom，初始化echarts实例
            var myChart = echarts.init(document.querySelector(".provinceBar1 .chart"));
            option = {
                dataset: {
                    source: [
                        ['name', 'confirm', 'heal', 'dead', 'now_confirm', 'confirm_compare']
                    ]
                },
                calculable: true,
                tooltip: {
                    trigger: 'item',
                    // formatter: '{a} <br/>{c} ({d}%)'
                    formatter: function (params) {
                        return params.data.name + "</br>" +
                            "累计确诊: " + params.data.confirm + "</br>" +
                            "累计治愈: " + params.data.heal + "</br>" +
                            "累计死亡: " + params.data.dead + "</br>" +
                            "现有确诊: " + params.data.now_confirm + "</br>" +
                            "较昨日确诊: " + (params.data.confirm_compare > 0 ? '+' + params.data.confirm_compare : params.data.confirm_compare) + "</br>";
                    }
                },
                series: [{
                    name: '累计确诊',
                    type: 'pie',
                    clockWise: false,
                    radius: [70, 450],
                    center: ['70%', '70%'],
                    roseType: 'area',
                    // encode: {
                    //     itemName: 'name',
                    //     value: 'confirm'
                    // },
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                var colorList = [
                                    "#a71a4f", "#c71b1b", "#d93824", "#e7741b", "#dc9e31", "#d2b130", "#8cc13f", "#53b440", "#48af54", "#479c7f", "#48a698", "#57868c"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {
                                position: 'inside',
                                textStyle: {
                                    fontWeight: 'bold',
                                    fontFamily: 'Microsoft YaHei',
                                    color: '#FAFAFA',
                                    fontSize: 10
                                },
                                //注意这里大小写敏感
                                formatter: function (params) {
                                    return params.data.name
                                },

                            },
                        },
                    },
                },
                    {
                        name: '透明圆圈',
                        type: 'pie',
                        radius: [0, 70],
                        center: ['70%', '70%'],
                        itemStyle: {
                            color: 'rgba(250, 250, 250, 0.3)',
                        },
                        data: [
                            {value: 8, name: ''}
                        ]
                    }
                ]

            };

            // 使用刚指定的配置项和数据显示图表。
            myChart.setOption(option);
            var virus = []

            data.forEach(item => {
                virus.push({
                    "name": item.name,
                    "confirm": item.confirm,
                    "heal": item.heal,
                    "dead": item.dead,
                    "now_confirm": item.now_confirm,
                    "confirm_compare": item.confirm_compare
                })
            })
            //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
            myChart.setOption({ //加载数据图表
                dataset: {
                    source: virus
                }
            })

            window.addEventListener("resize", function () {
                myChart.resize();
            });
        }
    })
}
