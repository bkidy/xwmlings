import sys
from tkinter import SEL
import mainui
import requests
import sqlite3
from sqlite3 import Error
from PyQt5.QtWidgets import QApplication, QMainWindow,QTreeWidgetItem
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.textEdit.append("欢迎使用权限配置助手，请点击下方【更新角色】开始操作\n")
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
        self.role_init()

    # 连接数据库
    def sql_connection(self):
        try:
            con = sqlite3.connect('tlrole.db')
            return con
        except Error as e:
            self.ui.textEdit.append(str(e))

    # 清空指定表
    def sql_delete_table(self, name, con):
        cursor_obj = con.cursor()
        try:
            cursor_obj.execute("DELETE FROM %s" % name)
            cursor_obj.execute("UPDATE sqlite_sequence SET seq=0 WHERE NAME ='%s'" % name)
            con.commit()
        except Error as e:
            self.ui.textEdit.append(str(e))

    # 查询数据库角色数据并返给Combox赋值
    def role_init(self):
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        query_role_sql = "select id,roleLabel FROM role"
        query_role_right_sql = "select * from role_menu_action where role_id = ? "
        role_data = cursor_obj.execute(query_role_sql)
        for row in role_data:
            self.ui.comboBox.addItem(row[1], userData=str(row[0]))
        current_role = self.ui.comboBox.currentData()
        MainWindow.show_role_right(self,current_role)

    def show_role_right(self,current_role):
        self.ui.treeWidget.clear()
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        query_role_right_sql = "select * from role_menu_action where role_id = ? "
        top_menu_id = 0
        second_menu_id = 0
        query_role_right = cursor_obj.execute(query_role_right_sql, (current_role,))
        for item in query_role_right:
            if item[3] != top_menu_id:
                top_menu = QTreeWidgetItem(self.ui.treeWidget)
                self.ui.treeWidget.topLevelItem(self.ui.treeWidget.topLevelItemCount()-1).setText(0,item[4])
                top_menu_id = item[3]
            if item[5] != second_menu_id:
                second_menu = QTreeWidgetItem(top_menu)
                second_menu.setText(0,item[6])
                second_menu_id = item[5]
            action = QTreeWidgetItem(second_menu)
            action.setData(0,1,item[7])
            action.setText(0,item[8])
            
            if item[11] == 1:
                # is_right = "True"
                action.setCheckState(0,Qt.Checked)
            else:
                # is_right = "False"
                action.setCheckState(0,Qt.Unchecked)
            if item[12] == 1:
                action.setCheckState(1,Qt.Checked)
            else:
                action.setCheckState(1,Qt.Unchecked)
            # self.ui.textEdit.append(str(action.data(0,1)))
        self.ui.treeWidget.expandAll()
        
    # def save_right_after(self):
        # con = MainWindow.sql_connection(1)
        # cursor_obj = con.cursor()
        # action_id = str(self.ui.treeWidget.findItems(0).data(0,1))
        # self.ui.textEdit.append(action_id)



    # 获取角色列表
    def get_role_list(self, token):
        self.headers["token"] = token
        json_data = {
            "pageNum": 1,
            "pageSize": 50,
            "roleLabel": "",
            "admType": 10,
            "rootOrgId": "1"
        }
        j_role_list = requests.post(self.url_role, json=json_data, headers=self.headers)
        role_list = j_role_list.json().get("data").get("pageInfo").get("list")
        return role_list

    # 获取角色权限包
    def get_role_tree(self, post_data):
        self.headers["token"] = self.ui.lineEdit.text()
        tree = requests.post(self.url_tree, json=post_data, headers=self.headers)
        return tree.json()

    # 获取线上最新数据并更新数据库各表
    def update_role_data(self):
        token = self.ui.lineEdit.text()
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        menu_sql = 'insert into menu (menuId,menuPid,menuLabel) VALUES (?,?,?)'
        action_sql = 'insert into action (actionId,actionCode,actionLabel,menuPId) VALUES (?,?,?,?)'
        user_sql = 'insert into role_menu_action (role_id,role_label,menu_top_id,menu_top_label,menu_second_id,menu_second_label,action_id,action_label,range_code,is_right_before,is_right_after) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
        role_sql = 'insert into role (id,roleLabel) VALUES (?,?)'

        #  清空menu表及action表
        MainWindow.sql_delete_table(self, name="menu", con=con)
        MainWindow.sql_delete_table(self, name="action", con=con)
        MainWindow.sql_delete_table(self, name="role_menu_action", con=con)
        MainWindow.sql_delete_table(self, name="role", con=con)

        # 获取线上角色列表
        role_list = MainWindow.get_role_list(self, token)
        for role in role_list:
            role_id = role["id"]
            role_label = role["roleLabel"]
            self.ui.comboBox.addItem(role_label)
            try:
                cursor_obj.execute(role_sql, (role_id, role_label))
                con.commit()
            except Error as e:
                self.ui.textEdit.append(str(str(Error)))
            role_id_adm_type_dto_list = role.get("roleIdAdmTypeDtoList")
            QApplication.processEvents()
            self.ui.textEdit.append("\n获取到角色：%s\n开始更新角色权限..." % role_label)
            j_user_role = MainWindow.get_role_tree(self, role_id_adm_type_dto_list)
            user_role = j_user_role.get("data").get("menuTreeByTuring")
            for topMenu in user_role:
                # 获取一级菜单数据
                menu_top_id = topMenu.get("menuId")
                menu_pid = topMenu.get("menuPId")
                menu_top_label = topMenu.get("menuLabel")
                # 向数据库写入一级菜单数据
                if role_id == "1":
                    try:
                        cursor_obj.execute(menu_sql, (menu_top_id, menu_pid, menu_top_label))
                        con.commit()
                        QApplication.processEvents()
                        self.ui.textEdit.append("更新一级菜单：%s...\n" % menu_top_label)
                    except Error as e:
                        self.ui.textEdit.append(str(e))
                for childMenu in topMenu.get("children"):
                    # 获取二级菜单数据
                    menu_second_id = childMenu.get("menuId")
                    menu_pid = childMenu.get("menuPId")
                    menu_second_label = childMenu.get("menuLabel")
                    if role_id == "1":
                        try:
                            cursor_obj.execute(menu_sql, (menu_second_id, menu_pid, menu_second_label))
                            con.commit()
                            QApplication.processEvents()
                            self.ui.textEdit.append("++ 更新二级菜单：%s...\n" % menu_second_label)
                        except Error as e:
                            self.ui.textEdit.append(str(e))
                    for action in childMenu.get("actions"):
                        # 获取动作数据
                        action_code = action.get("actionCode")
                        action_id = action.get("actionId")
                        action_label = action.get("actionLabel")
                        action_ck = action.get("checked")
                        if action_ck:
                            action_ck = 1
                        else:
                            action_ck = 0
                        range_code = action.get("range")
                        # 写入动作数据
                        if role_id == "1":
                            try:
                                cursor_obj.execute(action_sql, (action_id, action_code, action_label, menu_second_id))
                                con.commit()
                                self.ui.textEdit.append("+++ 更新操作菜单：%s" % action_label)
                            except Error as e:
                                self.ui.textEdit.append(str(e))
                        # 写入用户权限包
                        try:
                            cursor_obj.execute(user_sql, (
                                role_id, role_label, menu_top_id, menu_top_label, menu_second_id, menu_second_label,
                                action_id, action_label, range_code, action_ck, action_ck))
                            con.commit()
                        except Error as e:
                            self.ui.textEdit.append(str(e))
            self.ui.textEdit.append("%s 权限更新完成" % role_label)

    def select_role(self):
        self.ui.label_2.setText(self.ui.comboBox.currentData())
        current_role = self.ui.comboBox.currentData()
        MainWindow.show_role_right(self,current_role)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
