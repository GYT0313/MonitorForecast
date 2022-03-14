// //中国疫情数据
// var china = function () {
//     $.ajax({
//         url: 'http://127.0.0.1:5000/china/map',
//         type: 'get',
//         // data: {},
//         dataType: 'jsonp',
//         success: function (data) {
//             console.log(data.confirm)
//             return data.confirm
//         }
//     })
// };
//
//
// // 1、各大洲累计确诊分布(不包含国内)
// (function () {
//     //初识化ECharts
//     var myChart = echarts.init(document.querySelector(".china .bar .chart"));
//     //指定配置项和数据
//     var option = {
//         title: {
//             show: false,
//             text: '饼图',
//             x: 'center'
//         },
//         color: ['#37a2da', '#9fe6b8', '#ffdb5c', '#ff9f7f', '#fb7293', '#8378ea', '#00d887'],
//         tooltip: {
//             trigger: 'item',
//             formatter: "{a} <br/>{b} : {c} ({d}%)"
//         },
//         calculable: true,
//         series: [{
//             name: '各州累计确诊',
//             type: 'pie',
//             radius: [20, 70],
//             center: ['50%', '50%'],
//             roseType: 'radius',
//             // data:
//         }]
//     };
//     //配置项设置给ECarts实例对象
//     myChart.setOption(option);
//     var count = [];
//     $.ajax({
//         url: 'http://127.0.0.1:5000/global/continent',
//         type: 'get',
//         // data: {},
//         dataType: 'json',
//         success: function (data) {
//             data.forEach(x => count.push({
//                 name: x['continent'],
//                 value: x['confirm']
//             }))
//
//             //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
//             myChart.setOption({ //加载数据图表
//                 series: [{
//                     data: count
//                 }]
//             })
//         }
//     })
//
//     //图表跟随屏幕自适应
//     window.addEventListener('resize', function () {
//         myChart.resize();
//     })
// })();
//

// 2、各省疫情确诊情况前十五
(function () {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.querySelector(".chinaBar1 .chart"));
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
                return params.data[0] + "</br>" +
                    "累计确诊: " + params.data[1] + "</br>" +
                    "累计治愈: " + params.data[2] + "</br>" +
                    "累计死亡: " + params.data[3] + "</br>" +
                    "现有确诊: " + params.data[4] + "</br>" +
                    "较昨日确诊: " + (params.data[5] > 0 ? '+' + params.data[5] : params.data[5]) + "</br>";
            }
        },
        series: [{
            name: '累计确诊',
            type: 'pie',
            clockWise: false,
            radius: [30, 460],
            center: ['73%', '80%'],
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
                            return params.data[0]
                        },

                    },
                },
            },

        },
            {
                name: '透明圆圈',
                type: 'pie',
                radius: [8, 20],
                center: ['73%', '80%'],
                itemStyle: {
                    color: 'rgba(250, 250, 250, 0.3)',
                },
                data: [
                    {value: 5, name: ''}
                ]
            },
            {
                name: '透明圆圈',
                type: 'pie',
                radius: [8, 28],
                center: ['73%', '80%'],
                itemStyle: {
                    color: 'rgba(250, 250, 250, 0.3)',
                },
                data: [
                    {value: 5, name: ''}
                ]
            }
        ]

    };

    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
    var virus = []
    $.ajax({
        // 丁格尔玫瑰图
        url: 'http://127.0.0.1:5000/china/province/head',
        type: 'get',
        // data: {},
        dataType: 'json',
        success: function (data) {
            data.forEach(item => {
                virus.push([item.name, item.confirm, item.heal, item.dead, item.now_confirm, item.confirm_compare])
            })
            //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
            myChart.setOption({ //加载数据图表
                dataset: {
                    source: virus
                }
            })
        }
    })

    window.addEventListener("resize", function () {
        myChart.resize();
    });
})();


// // 3、全球疫情数据趋势(不包含国内)
// (function () {
//     var myChart = echarts.init(document.querySelector('.chinaLine .chart'))
//     var option = {
//         tooltip: {
//             trigger: 'axis',
//             axisPointer: {
//                 type: 'cross',
//                 label: {
//                     backgroundColor: '#6a7985'
//                 }
//             }
//         },
//         //图例
//         legend: {
//             top: "0%",
//             //图例字体样式
//             textStyle: {
//                 color: "rgba(255,255,255,.5)",
//                 fontSize: "12"
//             }
//         },
//         // 坐标系
//         grid: {
//             left: "10",
//             top: "30",
//             right: "10",
//             bottom: "10",
//             //文字标注算入
//             containLabel: true
//         },
//         xAxis: [{
//             type: 'category',
//             boundaryGap: false,
//             // data: ['二月', '三月', '四月', '五月', '六月'],
//             // 文本颜色为rgba(255,255,255,.6)  文字大小为 12
//             axisLabel: {
//                 textStyle: {
//                     color: "rgba(255,255,255,.6)",
//                     fontSize: 12
//                 }
//             },
//             // x轴线的颜色为   rgba(255,255,255,.2)
//             axisLine: {
//                 lineStyle: {
//                     color: "rgba(255,255,255,.2)"
//                 }
//             },
//         }],
//         yAxis: [{
//             type: 'value',
//             //隐藏坐标轴刻度
//             axisTick: {show: false},
//             //标注y轴线样式
//             axisLine: {
//                 lineStyle: {
//                     color: "rgba(255,255,255,.1)"
//                 }
//             },
//             //标注文本
//             axisLabel: {
//                 textStyle: {
//                     color: "rgba(255,255,255,.6)",
//                     fontSize: 8
//                 }
//             },
//             // 修改分割线的颜色
//             splitLine: {
//                 lineStyle: {
//                     color: "rgba(255,255,255,.1)"
//                 }
//             }
//         }],
//         //主题样式设计
//         series: [{
//             name: '累计确诊',
//             type: 'line',
//             // stack: '总量', //数据堆叠
//             // data: [220, 182, 191, 234, 290, 330, 310],
//             //线圆滑
//             smooth: true,
//             // 单独修改线的样式
//             lineStyle: {
//                 color: "#0184d5",
//                 width: 2
//             },
//             // 填充区域
//             areaStyle: {
//                 // 渐变色
//                 color: new echarts.graphic.LinearGradient(
//                     0,
//                     0,
//                     0,
//                     1,
//                     [{
//                         offset: 0,
//                         color: "rgba(1, 132, 213, 0.4)" // 渐变色的起始颜色
//                     },
//                         {
//                             offset: 0.8,
//                             color: "rgba(1, 132, 213, 0.1)" // 渐变线的结束颜色
//                         }
//                     ],
//                     false
//                 ),
//                 shadowColor: "rgba(0, 0, 0, 0.1)" //阴影颜色
//             },
//             // 设置拐点 小圆点
//             symbol: "circle",
//             // 拐点大小
//             symbolSize: 8,
//             // 设置拐点颜色以及边框
//             itemStyle: {
//                 color: "#0184d5",
//                 borderColor: "rgba(221, 220, 107, .1)",
//                 borderWidth: 12
//             },
//             //开始不显示坐标圆点
//             showSymbol: false,
//         },
//             {
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 name: "累计死亡",
//                 type: "line",
//                 smooth: true,
//                 lineStyle: {
//                     normal: {
//                         color: "#37a2da",
//                         width: 2
//                     }
//                 },
//                 areaStyle: {
//                     normal: {
//                         color: new echarts.graphic.LinearGradient(
//                             0,
//                             0,
//                             0,
//                             1,
//                             [{
//                                 offset: 0,
//                                 color: "rgba(0, 216, 135, 0.4)"
//                             },
//                                 {
//                                     offset: 0.8,
//                                     color: "rgba(0, 216, 135, 0.1)"
//                                 }
//                             ],
//                             false
//                         ),
//                         shadowColor: "rgba(0, 0, 0, 0.1)"
//                     }
//                 },
//                 // 设置拐点 小圆点
//                 symbol: "circle",
//                 // 拐点大小
//                 symbolSize: 5,
//                 // 设置拐点颜色以及边框
//                 itemStyle: {
//                     color: "#37a2da",
//                     borderColor: "rgba(221, 220, 107, .1)",
//                     borderWidth: 12
//                 },
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 // data: [120, 132, 101, 134, 90, 230, 210]
//                 // stack: '总量',
//             },
//             {
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 name: "累计治愈",
//                 type: "line",
//                 smooth: true,
//                 lineStyle: {
//                     normal: {
//                         color: "#ffdb5c",
//                         width: 2
//                     }
//                 },
//                 areaStyle: {
//                     normal: {
//                         color: new echarts.graphic.LinearGradient(
//                             0,
//                             0,
//                             0,
//                             1,
//                             [{
//                                 offset: 0,
//                                 color: "rgba(0, 216, 135, 0.4)"
//                             },
//                                 {
//                                     offset: 0.8,
//                                     color: "rgba(0, 216, 135, 0.1)"
//                                 }
//                             ],
//                             false
//                         ),
//                         shadowColor: "rgba(0, 0, 0, 0.1)"
//                     }
//                 },
//                 // 设置拐点 小圆点
//                 symbol: "circle",
//                 // 拐点大小
//                 symbolSize: 5,
//                 // 设置拐点颜色以及边框
//                 itemStyle: {
//                     color: "#ffdb5c",
//                     borderColor: "rgba(221, 220, 107, .1)",
//                     borderWidth: 12
//                 },
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 // data: [120, 132, 101, 134, 90, 230, 210]
//                 // stack: '总量',
//             },
//             {
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 name: "较昨日新增",
//                 type: "line",
//                 smooth: true,
//                 lineStyle: {
//                     normal: {
//                         color: "#ff9f7f",
//                         width: 2
//                     }
//                 },
//                 areaStyle: {
//                     normal: {
//                         color: new echarts.graphic.LinearGradient(
//                             0,
//                             0,
//                             0,
//                             1,
//                             [{
//                                 offset: 0,
//                                 color: "rgba(0, 216, 135, 0.4)"
//                             },
//                                 {
//                                     offset: 0.8,
//                                     color: "rgba(0, 216, 135, 0.1)"
//                                 }
//                             ],
//                             false
//                         ),
//                         shadowColor: "rgba(0, 0, 0, 0.1)"
//                     }
//                 },
//                 // 设置拐点 小圆点
//                 symbol: "circle",
//                 // 拐点大小
//                 symbolSize: 5,
//                 // 设置拐点颜色以及边框
//                 itemStyle: {
//                     color: "#ff9f7f",
//                     borderColor: "rgba(221, 220, 107, .1)",
//                     borderWidth: 12
//                 },
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 // data: [120, 132, 101, 134, 90, 230, 210]
//                 // stack: '总量',
//             },
//             {
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 name: "死亡率%",
//                 type: "line",
//                 smooth: true,
//                 lineStyle: {
//                     normal: {
//                         color: "#fb7293",
//                         width: 2
//                     }
//                 },
//                 areaStyle: {
//                     normal: {
//                         color: new echarts.graphic.LinearGradient(
//                             0,
//                             0,
//                             0,
//                             1,
//                             [{
//                                 offset: 0,
//                                 color: "rgba(0, 216, 135, 0.4)"
//                             },
//                                 {
//                                     offset: 0.8,
//                                     color: "rgba(0, 216, 135, 0.1)"
//                                 }
//                             ],
//                             false
//                         ),
//                         shadowColor: "rgba(0, 0, 0, 0.1)"
//                     }
//                 },
//                 // 设置拐点 小圆点
//                 symbol: "circle",
//                 // 拐点大小
//                 symbolSize: 5,
//                 // 设置拐点颜色以及边框
//                 itemStyle: {
//                     color: "#fb7293",
//                     borderColor: "rgba(221, 220, 107, .1)",
//                     borderWidth: 12
//                 },
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 // data: [120, 132, 101, 134, 90, 230, 210]
//                 // stack: '总量',
//             },
//             {
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 name: "治愈率%",
//                 type: "line",
//                 smooth: true,
//                 lineStyle: {
//                     normal: {
//                         color: "#8378ea",
//                         width: 2
//                     }
//                 },
//                 areaStyle: {
//                     normal: {
//                         color: new echarts.graphic.LinearGradient(
//                             0,
//                             0,
//                             0,
//                             1,
//                             [{
//                                 offset: 0,
//                                 color: "rgba(0, 216, 135, 0.4)"
//                             },
//                                 {
//                                     offset: 0.8,
//                                     color: "rgba(0, 216, 135, 0.1)"
//                                 }
//                             ],
//                             false
//                         ),
//                         shadowColor: "rgba(0, 0, 0, 0.1)"
//                     }
//                 },
//                 // 设置拐点 小圆点
//                 symbol: "circle",
//                 // 拐点大小
//                 symbolSize: 5,
//                 // 设置拐点颜色以及边框
//                 itemStyle: {
//                     color: "#8378ea",
//                     borderColor: "rgba(221, 220, 107, .1)",
//                     borderWidth: 12
//                 },
//                 // 开始不显示拐点， 鼠标经过显示
//                 showSymbol: false,
//                 // data: [120, 132, 101, 134, 90, 230, 210]
//                 // stack: '总量',
//             }
//         ]
//     };
//     // 把配置和数据给实例对象
//     myChart.setOption(option);
//
//     var confirmCount = []
//     var deadCount = []
//     var healCount = []
//     var newAddConfirmCount = []
//     var deadRateCount = []
//     var healRateCount = []
//     var date = []
//     //  全球疫情趋势
//     $.ajax({
//         url: 'http://127.0.0.1:5000/global/daily',
//         type: 'get',
//         // data: {},
//         dataType: 'json',
//         success: function (data) {
//             data.forEach(item => {
//                 confirmCount.push(item.confirm)
//                 deadCount.push(item.dead)
//                 healCount.push(item.heal)
//                 newAddConfirmCount.push(item.new_add_confirm)
//                 deadRateCount.push(item.dead_rate)
//                 healRateCount.push(item.heal_rate)
//                 date.push(item.date_time)
//             })
//
//             //必须在这里在设置一遍，这里涉及到的问题不太懂，只知道如不再设置，而在ajax外赋值是没有作用的
//             myChart.setOption({ //加载数据图表
//                 series: [{
//                     data: confirmCount
//                 }, {
//                     data: deadCount
//                 }, {
//                     data: healCount
//                 }, {
//                     data: newAddConfirmCount
//                 }, {
//                     data: deadRateCount
//                 }, {
//                     data: healRateCount
//                 }],
//                 xAxis: [{
//                     data: date
//                 }]
//             })
//         }
//     })
//
//     window.addEventListener('resize', function () {
//         myChart.resize()
//     })
// })();


// 4、国内各省疫情地图
(function () {
    var myChart = echarts.init(document.querySelector('.chinaMap .chart'))
    var option = {
        title: {
            text: '全球各国确诊情况',
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
                // var value = params.value + '';
                // return params.seriesName + '<br/>' + params.name + ' : ' + params.data[2] + '人';
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
            max: 300000,
            text: ['High', 'Low'],
            realtime: false,
            calculable: false,
            textStyle: {
                color: 'white'
            },
            color: ['#481380', '#7f78d2', '#efb1ff', '#ffe2ff']
        },
        // geo: {
        //     // 这个是重点配置区
        //     map: "china", // 表示中国地图
        //     roam: true,
        //     label: {
        //         normal: {
        //             show: true, // 是否显示对应地名
        //             textStyle: {
        //                 color: "#fff",
        //             },
        //         },
        //     }
        // },
        series: [
            {
                name: '累计确诊人数',
                type: 'map',
                mapType: 'china',
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
        url: 'http://127.0.0.1:5000/china/province',
        type: 'get',
        // data: {},
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
})();