import sys
from tkinter import SEL
import mainui
import requests
import sqlite3
from enum import Enum
from sqlite3 import Error
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class Range(Enum):
    全部数据 = 1
    本人 = 0
    本部门或以下 = 4


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
        MainWindow.show_role_right(self, current_role)

    def show_role_right(self, current_role):
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
                self.ui.treeWidget.topLevelItem(self.ui.treeWidget.topLevelItemCount() - 1).setText(0, item[4])
                top_menu_id = item[3]
            if item[5] != second_menu_id:
                second_menu = QTreeWidgetItem(top_menu)
                second_menu.setText(0, item[6])
                second_menu_id = item[5]
            action = QTreeWidgetItem(second_menu)
            # checked = ("添加 %s-%s：%s" % (item[4],item[6],item[8]))
            action.setData(1, 1, [item[0], item[2], item[4], item[6], item[8], item[9], item[11]])
            action.setText(0, item[8])
            if item[11] == 1:
                action.setIcon(0, QIcon('./icon/checked.png'))
            else:
                action.setIcon(0, QIcon('./icon/unchecked.png'))
            if item[12] == 1:
                action.setCheckState(1, Qt.Checked)
            else:
                action.setCheckState(1, Qt.Unchecked)
            # self.ui.textEdit.append(str(action.data(0,1)))
        self.ui.treeWidget.expandAll()

    def save_right_after(self):
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        update_sql = "UPDATE role_menu_action SET is_right_after = ?, is_changed = 1 WHERE id = ? ".format()
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        role_label = self.ui.comboBox.currentText()
        self.ui.textEdit.append("\n【%s】权限调整如下：" % role_label)
        while iterator.value():
            item = iterator.value()
            # self.ui.textEdit.append(str(item.data(1,1)))
            old_action = item.data(1, 1)
            action_ck = item.checkState(1)
            if action_ck == 2:
                action_ck = 1
            if old_action:
                if old_action[6] != action_ck:
                    if action_ck == 1:
                        self.ui.textEdit.append("新增： %s-%s:%s " % (old_action[2], old_action[3], old_action[4]))
                    else:
                        self.ui.textEdit.append("移除： %s-%s:%s " % (old_action[2], old_action[3], old_action[4]))
                    try:
                        cursor_obj.execute(update_sql, (action_ck, old_action[0]))
                        con.commit()
                    except Error as e:
                        self.ui.textEdit.append(str(e))
            iterator += 1
        con.close()

    def discard_changed(self):
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        update_sql = "UPDATE role_menu_action SET is_right_after = ?, is_changed = 0 WHERE id = ? ".format()
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        while iterator.value():
            item = iterator.value()
            old_action = item.data(1, 1)
            if old_action:
                action_ck = old_action[6]
                try:
                    cursor_obj.execute(update_sql, (action_ck, old_action[0]))
                    con.commit()
                except Error as e:
                    self.ui.textEdit.append(str(e))
            iterator += 1
        con.close()
        MainWindow.show_role_right(self,self.ui.comboBox.currentData())
        self.ui.textEdit.append("\n【%s】权限已重置成线上数据" % self.ui.comboBox.currentText())

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

    def pre_changed(self):
        con = MainWindow.sql_connection(1)
        cursor_obj = con.cursor()
        action_cgd_sql = "SELECT role_label,menu_top_label,menu_second_label,action_label,action_id FROM role_menu_action WHERE is_changed =1 AND is_right_after = ? GROUP BY role_id ORDER BY action_id".format()
        action_add_cgd = cursor_obj.execute(action_cgd_sql,(1,))
        action_add = []
        role_add = []
        for item in action_add_cgd:
            if item[4] not in action_add:
                if role_add:
                    self.ui.textEdit.append("角色： %s\n" % role_add)
                    role_add = []
                action_label = item[1] +"-" + item[2]+ "::" + item[3]
                self.ui.textEdit.append("本次新增权限：%s\n" % action_label)
                role_add.append("【%s】" % item[0])
                action_add.append(item[4])
            elif item[4] in action_add:
                role_add.append("【%s】" % item[0])
        self.ui.textEdit.append("角色： %s\n" % role_add)

        action_move_cgd = cursor_obj.execute(action_cgd_sql,(0,))
        action_move = []
        role_move = []
        for item in action_move_cgd:
            if item[4] not in action_move:
                if role_move:
                    self.ui.textEdit.append("角色： %s\n" % role_move)
                    role_move = []
                action_label = item[1] +"-" + item[2]+ "::" + item[3]
                self.ui.textEdit.append("本次移除权限：%s\n" % action_label)
                role_move.append("【%s】" % item[0])
                action_move.append(item[4])
            elif item[4] in action_move:
                role_move.append("【%s】" % item[0])
        self.ui.textEdit.append("角色： %s\n" % role_move)


    def select_role(self):
        self.ui.label_2.setText(self.ui.comboBox.currentData())
        current_role = self.ui.comboBox.currentData()
        MainWindow.show_role_right(self, current_role)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
