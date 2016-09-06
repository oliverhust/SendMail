''''''''''''''''''''''''''''''''''''''''''读取界面'''''''''''''''''''''''''''''''''''''''''''''''
set ie=wscript.createobject("internetexplorer.application","event_") '创建ie对象'
Set objShell = WScript.CreateObject("WScript.Shell")

ie.menubar=0 '取消菜单栏'
ie.addressbar=0 '取消地址栏'
ie.toolbar=0 '取消工具栏'
ie.statusbar=0 '取消状态栏'
ie.width=500 '宽400'
ie.height=600 '高400'
ie.resizable=0 '不允许用户改变窗口大小'
ie.navigate "about:blank" '打开空白页面'
ie.left=fix((ie.document.parentwindow.screen.availwidth-ie.width)/2) '水平居中'
ie.top=fix((ie.document.parentwindow.screen.availheight-ie.height)/2) '垂直居中'
ie.visible=1 '窗口可见'
attachfile = ""

with ie.document 
.write "<html><body bgcolor=#dddddd scroll=no>" 
.write "<h2 align=center>群发邮件</h2><br>"
.write "<p>*主题  ：<input id=theme type=text size=30 >" 
.write "<p>*正文  ：<input type=file name=fileField class=file id=text accept='.txt' >" 
.write "<p>附件1 ：<input type=file name=fileField class=file id=attach1 >" 
.write "<p>附件2 ：<input type=file name=fileField class=file id=attach2 >" 
.write "<p>附件3 ：<input type=file name=fileField class=file id=attach3 >" 
.write "<p>*邮箱列表 ：<input type=file name=fileField class=file id=email_list >" 
.write "<p>*从第<input type=text id=from value=1 >到第<input type=text id=to value=9 >张表"
.write "<p>*账号  ：<input id=user type=text size=15 value=U201313778 >@hust.edu.cn" 
.write "<p>发件人：<input id=username type=text size=12 value=王佳静 >" 
.write "<p>*密码  ：<input id=password type=password size=30 value=dian201313778 >"
.write "<br><br>" 
.write "<input id=confirm type=button value=确定 >"
.write "<input id=cancel type=button value=取消 >"
.write "</body></html>"
end with

dim wmi '显式定义一个全局变量'
set wnd=ie.document.parentwindow '设置wnd为窗口对象'
set id=ie.document.all '设置id为document中全部对象的集合'
id.confirm.onclick=getref("confirm") '设置点击"确定"按钮时的处理函数'
id.cancel.onclick=getref("cancel") '设置点击"取消"按钮时的处理函数'

do while true '由于ie对象支持事件，所以相应的，'
wscript.sleep 200 '脚本以无限循环来等待各种事件。'
loop

sub event_onquit 'ie退出事件处理过程'
wscript.quit '当ie退出时，脚本也退出'
end sub

sub cancel '"取消"事件处理过程'
ie.quit '调用ie的quit方法，关闭IE窗口'
end sub '随后会触发event_onquit，于是脚本也退出了'

sub confirm '"确定"事件处理过程，这是关键'
dim theme
theme = ie.document.getElementById("theme").value
if theme = "" then
	MsgBox ("请输入主题！")
else
	WSH.Echo theme
end if

dim textname
textfile = ie.document.getElementById("text").value
if textfile = "" then 
	MsgBox ("请选择正文！")
else
	fakepath = left(textfile,12)
	textname = replace(textfile,fakepath,"")
	WSH.Echo textname
end if 

dim filename
for i = 1 to 3
	attachfile = ie.document.getElementById("attach"&i).value
	if attachfile = "" then 
	else
		filename_tmp = replace(attachfile,fakepath,"")
		WSH.Echo filename_tmp
		filename = filename &"|"&"C:\"&filename_tmp
	end if	
next
strlen = Len(filename)
filename = mid(filename,2,strlen) 
WSH.Echo filename

dim emailname
emailfile = ie.document.getElementById("email_list").value
if emailfile = "" then 
	MsgBox ("请选择要发送的邮箱！")
else
	emailname = replace(emailfile,fakepath,"")
	WSH.Echo emailname
end if 

''''''''''''''''''''''''''''''''''''''''''''' 
WSH.Echo "发送部分"
if textfile = "" Or theme = "" then 
else
	Set oExcel=CreateObject("excel.application")
	Set oWorkBook=oExcel.Workbooks.Open( "C:\"&emailname )
	SendEmailALL oWorkBook, textname,filename
	oExcel.Quit
end if

''''''''''''''''''''''''''''''''
end sub

sub clearlog(name)
wql="select * from Win32_NTEventLogFile where logfilename='"&name&"'"
set logs=wmi.execquery(wql) '注意，logs的成员不是每条日志，'
for each l in logs '而是指定日志的文件对象。'
if l.cleareventlog() then
wnd.alert("清除日志"&name&"时出错！")
ie.quit
wscript.quit
end if
next
end sub



Class CdoMail
  ' 定义公共变量，类初始化
      Public fso, wso, objMsg
    Private Sub Class_Initialize()
        Set fso = CreateObject("Scripting.FileSystemObject")
        Set wso = CreateObject("wscript.Shell")
        Set objMsg = CreateObject("CDO.Message")
    End Sub


' 设置服务器属性，4参数依次为：STMP邮件服务器地址，STMP邮件服务器端口，STMP邮件服务器STMP用户名，STMP邮件服务器用户密码
    ' 例子：Set MyMail = New CdoMail : MyMail.MailServerSet "smtp.qq.com", 443, "yu2n", "P@sSW0rd"
    Public Sub MailServerSet( strServerName, strServerPort, strServerUsername, strServerPassword )
        NameSpace = "http://schemas.microsoft.com/cdo/configuration/"
        With objMsg.Configuration.Fields
            .Item(NameSpace & "sendusing") = 2                      'Pickup = 1(Send message using the local SMTP service pickup directory.), Port = 2(Send the message using the network (SMTP over the network). )
            .Item(NameSpace & "smtpserver") = strServerName         'SMTP Server host name / ip address
            .Item(NameSpace & "smtpserverport") = strServerPort     'SMTP Server port
            .Item(NameSpace & "smtpauthenticate") = 1               'Anonymous = 0, basic (clear-text) authentication = 1, NTLM = 2
            .Item(NameSpace & "smtpusessl") = True          
            .Item(NameSpace & "sendusername") = strServerUsername   '<发送者邮件地址>
            .Item(NameSpace & "sendpassword") = strServerPassword   '<发送者邮件密码>
            .Update
        End With
    End Sub
  ' 设置邮件寄送者与接受者地址，4参数依次为：寄件者(不能空)、收件者(不能空)、副本抄送、密件抄送
    Public Sub  MailFromTo( strMailFrom, strMailTo, strMailCc, strMailBCc)
        objMsg.From = strMailFrom   '<发送者邮件地址,与上面设置相同>
        objMsg.To = strMailTo       '<接收者邮件地址>
        objMsg.Cc = strMailCc       '[副本抄送]           
        objMsg.Bcc = strMailBcc     '[密件抄送]
    End Sub
' 邮件内容设置，3参数依次是：邮件类型(text/html/url)、主旨标题、主体内容(text文本格式/html网页格式/url一个现存的网页文件地址)
     Public Function MailBody( strType, strMailSubjectStr, strMessage )
        objMsg.Subject = strMailSubjectStr          '<邮件主旨标题>
        Select Case LCase( strType )
            Case "text"
                objMsg.TextBody = strMessage        '<文本格式内容>       
            Case "html"
                objMsg.HTMLBody = strMessage        '<html网页格式内容>
            Case "url"
                objMsg.CreateMHTMLBody strMessage   '<网页文件地址>
            Case Else
                objMsg.BodyPart.Charset = "gb2312"   '<邮件内容编码，默认gb2312>   
                objMsg.TextBody = strMessage        '<邮件内容，默认为文本格式内容>
        End Select
    End Function
  ' 添加所有附件，参数为附件列表数组，单个文件可使用 arrPath = Split( strPath & "|", "|")传入路径。
    Public Function MailAttachment( arrAttachment )
        If Not IsArray( arrAttachment ) Then arrAttachment = Split( arrAttachment & "|", "|")
        For i = 0 To UBound( arrAttachment )
            If fso.FileExists( arrAttachment(i) ) = True Then
                objMsg.Addattachment arrAttachment(i)
            End If
        Next
    End Function  
    ' 发送邮件
    Public Sub Send()
        'Delivery Status Notifications: Default = 0, Never = 1, Failure = 2, Success 4, Delay = 8, SuccessFailOrDelay = 14
        objMsg.DSNOptions = 0
        objMsg.Fields.update
        objMsg.Send
    End Sub

End Class

Function SendOneEmail(strSendAddr, strAcount, strAccountName, strPasswd,textname,filename)
    Set MyMail = New CdoMail
    '邮件正文内容文件读取
    TextBodyFileDir = "C:\"&textname
    Set fso=CreateObject("Scripting.FileSystemObject")
    Set TextBodyFile=fso.OpenTextFile(TextBodyFileDir, 1, False, 0)
    TextBodyInfo = TextBodyFile.readall
    TextBodyFile.Close
    '设置服务器(*)：服务器地址、服务器端口、邮箱用户名、邮箱密码
    MyMail.MailServerSet    "mail.hust.edu.cn", 25, strAccountName, strPasswd
    '设置寄件者与收件者地址(*)：寄件者、收件者、抄送副本(非必填)、密送副本(非必填)
    MyMail.MailFromTo       strAcount, "", "", strSendAddr
    '设置邮件内容(*)：内容类型(text/html/url)、邮件主旨标题、邮件正文文本
    MyMail.MailBody         "text", ie.document.getElementById("theme").value, TextBodyInfo
    '添加附件(非必填)：参数可以是一个文件路径，或者是一个包含多个文件路径的数组
    'MyMail.MailAttachment   Split("e:\2016全国批判性思维教师培训通知.doc|e:\2016全国批判性思维会议通知.doc|e:\2016年第一届全国基础教育批判性思维教师培训班（20160227）.docx|e:\2016年第一届全国基础教育批判性思维年会通知（20160227).docx", "|")
    MyMail.MailAttachment   Split(filename, "|")	
	WSH.Echo filename
	' 发送邮件(*)
    MyMail.Send
End Function
Function SendEmailToOneSheetAddr(Sheet, uiSheetCnt,textname,filename)
    arrAccountName = array("dian",ie.document.getElementById("user").value)'这里三行可以设置多个账号、密码
    arrAccount = array("dian@hust.edu.cn(Dian Group)",ie.document.getElementById("user").value&"@hust.edu.cn("&ie.document.getElementById("username").value&")")
    arrPasswd = array("diangroup1",ie.document.getElementById("password").value)
    uiCntAddrMax = 40 '这里设置每封邮件发送密送人数的上限
    uiCntAddr = 0
    strSendAddr = ""
    uiRowMax = Sheet.UsedRange.Rows.Count
    WSH.Echo "sheet " & uiSheetCnt & "总行数：" & uiRowMax
    'wscript.sleep 1*60*1000  '单位ms 1分钟  
    uiMyEmailCnt = 0
	'正则匹配邮箱
	Dim re
	Set re = New RegExp
	re.Pattern = "^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$"
	re.Global = True
	re.IgnoreCase = True
    For uiCntRow = 2 To uiRowMax '遍历每一行
        strCurAddr = Sheet.cells(uiCntRow,3).value 'Email信息在第3列
		If not re.Test(strCurAddr) Then
		Else
            strSendAddr = strSendAddr & strCurAddr & ","
            uiCntAddr = uiCntAddr + 1
        End If        
        If uiCntAddr = uiCntAddrMax Then
            '发送邮件
            SendOneEmail   strSendAddr, arrAccount(1), arrAccountName(1), arrPasswd(1),textname,filename'这里可更换账号发送,uiMyEmailCnt
            WSH.Echo "当前账户 :" & arrAccount(1)
            WSH.Echo "已发送至 :" & strSendAddr
            wscript.sleep 0.5*60*1000  '单位ms 0.5分钟  
            uiMyEmailCnt = uiMyEmailCnt + 1
            If uiMyEmailCnt = 2 Then '这个uiMyEmailCnt用来记录账号个数，也就是数组中元素个数
                uiMyEmailCnt = 0
            End If
            strSendAddr = ""
            uiCntAddr = 0
        End If
    Next
    
    If uiCntAddr > 0 Then
        '发送邮件
        SendOneEmail   strSendAddr, arrAccount(1), arrAccountName(1), arrPasswd(1),textname,filename'这里可更换账号发送,uiMyEmailCnt
        WSH.Echo "当前账户 :" & arrAccount(1)
        WSH.Echo "已发送至 :" & strSendAddr
        wscript.sleep 0.5*60*1000  '单位ms 0.5分钟  
        uiMyEmailCnt = uiMyEmailCnt + 1
        If uiMyEmailCnt = 2 Then '这个uiMyEmailCnt用来记录账号个数，也就是数组中元素个数
            uiMyEmailCnt = 0
        End If
        strSendAddr = ""
        uiCntAddr = 0 
    End If
End Function

Function SendEmailALL(Book,textname,filename)
    For uiSheetCnt = ie.document.getElementById("from").value To ie.document.getElementById("to").value '注意修改这里的值，从第1张表到第22张表
        Set Sheet = Book.Sheets(uiSheetCnt)     
        SendEmailToOneSheetAddr Sheet,uiSheetCnt,textname,filename
    Next
End Function

''''''''''''''''''''''''''''''''''''''''''发送邮件'''''''''''''''''''''''''''''''''''''''''''''''
