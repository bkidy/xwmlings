import sys, json
import mainui
import requests
import sqlite3
from sqlite3 import Error
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.url_role = 'https://bgateway.joyobpo.com/basic/role/multiList'
        self.url_tree = 'https://bgateway.joyobpo.com/basic/role/getRoleMenuActionTree'
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "aid": "101121",
            "content-type": "application/json;charset=UTF-8",
            "token": "",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        self.ui.textEdit.append("欢迎使用权限配置助手，请点击下方【更新角色】开始操作\n")

    def sql_connection(self):
        try:
            con = sqlite3.connect('tlrole.db')
            return con
        except Error:
            self.ui.textEdit.append(Error)

    def sqlDeleteTable(self, name, con):
        cursorObj = con.cursor()
        try:
            cursorObj.execute("DELETE FROM %s" % name)
            cursorObj.execute("UPDATE sqlite_sequence SET seq=0 WHERE NAME ='%s'" % name)
            con.commit()
        except Error:
            self.ui.textEdit.append(Error)

    def getRoleList(self,token):
        self.headers["token"] = token
        json_data = {
            "pageNum": 1,
            "pageSize": 50,
            "roleLabel": "",
            "admType": 10,
            "rootOrgId": "1"
        }
        j_roleList = requests.post(self.url_role, json=json_data, headers=self.headers)
        roleList = j_roleList.json().get("data").get("pageInfo").get("list")
        return roleList

    def getRoleJosn(self, json):
        self.headers["token"] = self.ui.lineEdit.text()
        tree = requests.post(self.url_tree, json=json, headers=self.headers)
        return tree.json()

    def queryRoleData(self):
        token = self.ui.lineEdit.text()
        con = MainWindow.sql_connection(1)
        cursorObj = con.cursor()
        menuSql = 'insert into menu (menuId,menuPid,menuLabel) VALUES (?,?,?)'
        actionSql = 'insert into action (actionId,actionCode,actionLabel,menuPId) VALUES (?,?,?,?)'
        userSql = 'insert into role_menu_action (role_id,menu_id,action_id,range_code) VALUES (?,?,?,?)'
        roleSql = 'insert into role (id,roleLabel) VALUES (?,?)'

        # # 清空menu表及action表
        MainWindow.sqlDeleteTable(self, name="menu", con=con)
        MainWindow.sqlDeleteTable(self, name="action", con=con)
        MainWindow.sqlDeleteTable(self, name="role_menu_action", con=con)
        MainWindow.sqlDeleteTable(self, name="role", con=con)
        
        #获取线上角色列表
        roleList = MainWindow.getRoleList(self,token)
        for role in roleList:
            roleId = role["id"]
            roleLabel = role["roleLabel"]
            try:
                cursorObj.execute(roleSql, (roleId, roleLabel))
                con.commit()
            except Error:
                self.ui.textEdit.append(Error)
            roleIdAdmTypeDtoList = role.get("roleIdAdmTypeDtoList")
            QApplication.processEvents()
            self.ui.textEdit.append("\n获取到角色：%s\n开始获取角色权限..." % roleLabel)
            j_userRole = MainWindow.getRoleJosn(self,roleIdAdmTypeDtoList)
            userRole = j_userRole.get("data").get("menuTreeByTuring")
            for topMenu in userRole:
                #获取一级菜单数据
                menuId = topMenu.get("menuId")
                menuPId = topMenu.get("menuPId")
                menuLabel = topMenu.get("menuLabel")
                #向数据库写入一级菜单数据
                if roleId == "1":
                    try:
                        cursorObj.execute(menuSql, (menuId, menuPId, menuLabel))
                        con.commit()
                        QApplication.processEvents()
                        self.ui.textEdit.append("更新一级菜单：%s...\n" % menuLabel)
                    except Error:
                        self.ui.textEdit.append(Error)
                for childMenu in topMenu.get("children"):
                    #获取二级菜单数据
                    menuId = childMenu.get("menuId")
                    menuPId = childMenu.get("menuPId")
                    menuLabel = childMenu.get("menuLabel")
                    if roleId == "1":
                        try:
                            cursorObj.execute(menuSql, (menuId, menuPId, menuLabel))
                            con.commit()
                            QApplication.processEvents()
                            self.ui.textEdit.append("++ 更新二级菜单：%s...\n" % menuLabel)
                        except Error:
                            self.ui.textEdit.append(Error)
                    for action in childMenu.get("actions"):
                        #获取动作数据
                        actionCode = action.get("actionCode")
                        actionId = action.get("actionId")
                        actionLabel = action.get("actionLabel")
                        actionCk = action.get("checked")
                        range = action.get("range")
                        #写入动作数据
                        if roleId == "1":
                            try:
                                cursorObj.execute(actionSql, (actionId, actionCode, actionLabel, menuId))
                                con.commit()
                                self.ui.textEdit.append("+++ 更新操作菜单：%s" % actionLabel)
                            except Error:
                                self.ui.textEdit.append(Error)
                        #写入用户权限包
                        if actionCk == True:
                            try:
                                cursorObj.execute(userSql,(roleId,menuId,actionId,range))
                                con.commit()
                                QApplication.processEvents()
                                self.ui.textEdit.append("更新角色权限：%s 菜单：%s 操作：%s" % (roleLabel,menuLabel,actionLabel))
                            except Error:
                                self.ui.textEdit.append(Error)
                

    def selectRole(self):
        # con = MainWindow.sql_connection(1)
        # cursorObj = con.cursor()
        # cursorObj.execute("SELECT menu_id,action_id FROM role_menu_action WHERE role_id = 7")
        self.ui.label_2.setText(self.ui.comboBox.currentText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
