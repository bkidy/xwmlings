import sys
import mainui
import requests
import sqlite3
from PyQt5.QtWidgets import QApplication,QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        # self.url_role = 'https://bgateway.joyobpo.com/basic/role/multiList'
        # self.url_tree = 'https://bgateway.joyobpo.com/basic/role/getRoleMenuActionTree'

    def sql_connection(self):
        try:
            con = sqlite3.connect('tlrole.db')
            return con
        except sqlite3.Error as e:
            self.ui.textEdit.append("连接数据库错误：%s" % e)

    def queryRoleList(self):
        con = MainWindow.sql_connection(1)
        cursorObj = con.cursor()
        if self.ui.lineEdit.text() == "":
            self.ui.textEdit.append("请输入Token！")
        else:
            token = self.ui.lineEdit.text()    
        self.ui.textEdit.append("您当前输入的Token: \n %s" % token)
        role_data = {
            "pageNum": 1,
            "pageSize": 50,
            "roleLabel": "",
            "admType": 10,
            "rootOrgId": "1"
        }
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "aid": "101121",
            "content-type": "application/json;charset=UTF-8",
            "token": token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        rolelist_url = 'https://bgateway.joyobpo.com/basic/role/multiList'
        role = requests.post(rolelist_url, json=role_data, headers=headers)
        self.ui.textEdit.append("请求结果:%s /n" % role.status_code)
        rolejosn = role.json().get("data").get("pageInfo").get("list")
        # print(role_josn)
        insert_sql = 'insert into role (id,roleLabel,status,admType) VALUES (?,?,?,?)'
        for i in rolejosn:
            id = i.get("id")
            roleLabel = i.get("roleLabel")
            status = i.get("status")
            updatetime = i.get("updatetime")
            admType = 0
            try:
                cursorObj.execute(insert_sql,(id,roleLabel,status,admType))
                con.commit()
            except sqlite3.Error as e:
                self.ui.textEdit.append("插入数据错误：%s" % e)
            self.ui.textEdit.append(roleLabel)
            self.ui.comboBox.addItem(roleLabel)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

