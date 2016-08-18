#-*- encoding: utf-8 -*-
 #author : rayment
 #CreateDate : 2013-01-24

 import imaplib
 import email
 #设置命令窗口输出使用中文编码
 import sys
 reload(sys)
 sys.setdefaultencoding('gbk')

 #保存文件方法（都是保存在指定的根目录下）
 def savefile(filename, data, path):
     try:
         filepath = path + filename
         print 'Saved as ' + filepath
         f = open(filepath, 'wb')
     except:
         print('filename error')
         f.close()
     f.write(data)
     f.close()
    
 #字符编码转换方法
 def my_unicode(s, encoding):
     if encoding:
         return unicode(s, encoding)
     else:
         return unicode(s)

 #获得字符编码方法
 def get_charset(message, default="ascii"):
     #Get the message charset
     return message.get_charset()
     return default

#解析邮件方法（区分出正文与附件）
def parseEmail(msg, mypath):
    mailContent = None
    contenttype = None
    suffix = None
    for part in msg.walk():
        if not part.is_multipart():
            contenttype = part.get_content_type()   
            filename = part.get_filename()
            charset = get_charset(part)
            #是否有附件
            if filename:
                h = email.Header.Header(filename)
                dh = email.Header.decode_header(h)
                fname = dh[0][0]
                encodeStr = dh[0][1]
                if encodeStr != None:
                    if charset == None:
                        fname = fname.decode(encodeStr, 'gbk')
                    else:
                        fname = fname.decode(encodeStr, charset)
                data = part.get_payload(decode=True)
                print('Attachment : ' + fname)
                #保存附件
                if fname != None or fname != '':
                    savefile(fname, data, mypath)            
            else:
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                if contenttype in ['text/html']:
                    suffix = '.htm'
               if charset == None:
                    mailContent = part.get_payload(decode=True)
                else:
                    mailContent = part.get_payload(decode=True).decode(charset)         
    return  (mailContent, suffix)

 #获取邮件方法
 def getMail(mailhost, account, password, diskroot, port = 993, ssl = 1):
     mypath = diskroot + ':\\'
     #是否采用ssl
     if ssl == 1:
         imapServer = imaplib.IMAP4_SSL(mailhost, port)
     else:
         imapServer = imaplib.IMAP4(mailhost, port)
     imapServer.login(account, password)
     imapServer.select()
     #邮件状态设置，新邮件为Unseen
     #Message statues = 'All,Unseen,Seen,Recent,Answered, Flagged'
     resp, items = imapServer.search(None, "Unseen")
     number = 1
     for i in items[0].split():
        #get information of email
        resp, mailData = imapServer.fetch(i, "(RFC822)")   
        mailText = mailData[0][1]
        msg = email.message_from_string(mailText)
        ls = msg["From"].split(' ')
        strfrom = ''
        if(len(ls) == 2):
            fromname = email.Header.decode_header((ls[0]).strip('\"'))
            strfrom = 'From : ' + my_unicode(fromname[0][0], fromname[0][1]) + ls[1]
        else:
            strfrom = 'From : ' + msg["From"]
        strdate = 'Date : ' + msg["Date"]
        subject = email.Header.decode_header(msg["Subject"])
        sub = my_unicode(subject[0][0], subject[0][1])
        strsub = 'Subject : ' + sub
              
        mailContent, suffix = parseEmail(msg, mypath)
        #命令窗体输出邮件基本信息
        print '\n'
        print 'No : ' + str(number)
        print strfrom
        print strdate
        print strsub
        '''
        print 'Content:'
        print mailContent
        '''
        #保存邮件正文
        if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
            savefile(str(number) + suffix, mailContent, mypath)
            number = number + 1
            
     imapServer.close()
     imapServer.logout()


 if __name__ =="__main__":
     #邮件保存在e盘
     mypath ='e'
     print 'begin to get email...'
     getMail('pop.gmail.com', 'xxxxxxxx@gmail.com', 'xxxxxxxx', mypath, 993, 1)
     #126邮箱登陆没用ssl
     #getMail('imap.126.com', 'xxxxxxxxx@126.com', 'xxxxxxxxxx', mypath, 143, 0)
     print 'the end of get email.'