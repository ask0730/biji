# 1.数据抓取抓取到的是窗口名称（如：新闻公告 -上海图书馆-Microsoft Edge），不是自己选取到的元素

## 原因分析：
目标中缺失了{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}
也就是内容窗口，猜测是没聚焦到内容窗口，具体是操作哪里有误，目前还没有分析出来

## 解决方法：
### 以下是成功和失败案例：
- 成功获取链接
{"wnd":[{"cls":"Chrome_WidgetWin_1","title":"*","app":"msedge"},{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}],"html":[{"tag":"DIV","parentid":"news","css-selector":"body>div>div>div>div>main>div>div>div>div>div>div>div>div>div>div>div"}]}
{"ExtractTable":0,"Columns":[{"selecors":{"path":[{"tag":"span"},{"tag":"a","idx":0}],"exact":true,"vprops":["text","url"]},"props":["url"]}]}

- 获取链接失败
{"wnd":[{"cls":"Chrome_WidgetWin_1","title":"*","app":"msedge"}],"html":[{"tag":"DIV","parentid":"news","css-selector":"body>div>div>div>div>main>div>div>div>div>div>div>div>div>div>div>div"}]}
{"ExtractTable":0,"Columns":[{"selecors":{"path":[{"tag":"span"},{"tag":"a","idx":0}],"exact":true,"vprops":["text","url"]},"props":["url"]}]}

内层窗口缺失贴到目标里：
```
{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}
```


# 2.开发语言
BotScript（简称UB语言）




# 3.在机器人指挥官部署流程
- 1、新建流程
- 2、在creator发布流程
- 3、新建触发器




# 4.合并二维数组
```vbscript
resultArray = []
For i = 0 To UBound(arrayTitle) - 1
    newItem = [
        arrayTitle[i][0],  
        arrayHref[i][0],   
        arrayDate[i][0]   
    ]
    push(resultArray, newItem)
Next
TracePrint(resultArray)
```

# 5.拆分二维数组
```vb
Rem 获取标题和日期
// arrayData = [
//     [
//         "置顶\n上海图书馆（上海科学技术情报研究所）2025年国庆节、中秋节期间开放公告\n2025-09-22"
//     ],
//     [
//         "置顶\n邀请读者为上海图书馆\"十五五\"发展规划建言献策\n2025-08-05"
//     ],
//     [
//         "上海图书馆电话总机临时关闭公告\n2025-09-17"
//     ]
// ]

arrayTitle = []
arrayDate = []

For i = 0 To UBound(arrayData) - 1
    strOriginal = arrayData[i][0]
    arrParts = Split(strOriginal, "\n")
    
    If UBound(arrParts) >= 2 And arrParts[0] = "置顶" Then
        strTitle = arrParts[1]
        strDate = arrParts[2]
    ElseIf UBound(arrParts) >= 1 Then
        strTitle = arrParts[0]
        strDate = arrParts[1]
    Else
        strTitle = strOriginal
        strDate = ""
    End If
    
    Push(arrayTitle, [strTitle])
    Push(arrayDate, [strDate])
Next
```