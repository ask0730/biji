# 1.数据抓取抓取到的是窗口名称（如：新闻公告 -上海图书馆-Microsoft Edge），不是自己选取到的元素

## 原因分析：
目标中缺失了{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}
也就是内容窗口，猜测是没聚焦到内容窗口，具体是操作哪里有误，目前还没有分析出来

## 解决方法：
### 以下是成功和失败案例：
成功获取链接
{"wnd":[{"cls":"Chrome_WidgetWin_1","title":"*","app":"msedge"},{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}],"html":[{"tag":"DIV","parentid":"news","css-selector":"body>div>div>div>div>main>div>div>div>div>div>div>div>div>div>div>div"}]}
{"ExtractTable":0,"Columns":[{"selecors":{"path":[{"tag":"span"},{"tag":"a","idx":0}],"exact":true,"vprops":["text","url"]},"props":["url"]}]}

获取链接失败
{"wnd":[{"cls":"Chrome_WidgetWin_1","title":"*","app":"msedge"}],"html":[{"tag":"DIV","parentid":"news","css-selector":"body>div>div>div>div>main>div>div>div>div>div>div>div>div>div>div>div"}]}
{"ExtractTable":0,"Columns":[{"selecors":{"path":[{"tag":"span"},{"tag":"a","idx":0}],"exact":true,"vprops":["text","url"]},"props":["url"]}]}

内层窗口缺失贴到目标里：
`{"cls":"Chrome_RenderWidgetHostHWND","title":"Chrome Legacy Window"}`

开发语言
BotScript（简称UB语言）