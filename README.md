# mail_auth
批量验证邮箱密码，支持gmail,163,126,yahoo,sina,outlook,hotmail,live等

usage

This is an Emails batch auth login program!
useage:
  mailAuth.py <email_list_file> <threads> [start_line_number]


Notice:Your email list must includes complete address which
also include a character '@' and the password you want to
test,and they must be separated with character ','!

Example:
    xxxx@gmail.com,password

After it completed,it will create 2 file in current path
which name is 'successMail.txt' and 'failedMail.txt'.
