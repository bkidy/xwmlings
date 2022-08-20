import logging
import sqlite3
import sys, re
from sqlite3 import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# 构建邮件头
from email.header import Header

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator, QMessageBox, QDialog

import mainui, form


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.children()
        self.__connect()
        self.__create_table()
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

    def __connect(self):
        try:
            self.con = sqlite3.connect("tl_data.db")  # 建立数据库连接
        except Error:
            logging.log(2, "数据库无法连接")
        else:
            self.cur = self.con.cursor()

    def __close(self):
        self.cur.close()
        self.con.close()

    def __del__(self):
        self.__close()

    def __create_table(self):
        try:
            action = '''
                    CREATE TABLE "action" (
                    "id" INTEGER NOT NULL,
                    "actionId" INTEGER,
                    "menuPId" INTEGER,
                    "actionCode" TEXT,
                    "actionLabel" TEXT,
                    PRIMARY KEY ("id")
                    );'''
            menu = '''
                    CREATE TABLE "menu" (
                    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "menuId" INTEGER,
                    "menuPId" INTEGER,
                    "menuLabel" TEXT
                    );'''
            role = '''
                    CREATE TABLE role ( id integer PRIMARY KEY, roleLabel char, status int, admType integer, updateTime time );
                    '''
            role_menu_action = '''
                    CREATE TABLE "role_menu_action" (
                    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "role_id" INTEGER,
                    "role_label" TEXT,
                    "menu_top_id" INTEGER,
                    "menu_top_label" TEXT,
                    "menu_second_id" INTEGER,
                    "menu_second_label" TEXT,
                    "action_id" INTEGER,
                    "action_label" TEXT,
                    "range_code" integer,
                    "range_str" TEXT,
                    "is_right_before" integer,
                    "is_right_after" integer,
                    "is_changed" integer
                    );'''
            self.cur.execute(action)
            self.cur.execute(menu)
            self.cur.execute(role)
            self.cur.execute(role_menu_action)
            self.con.commit()
            self.ui.textBrowser.append("初始化成功！")
        except Error as e:
            logging.log(2, e)

    # # 连接数据库
    # def sql_connection(self):
    #     try:
    #         con = sqlite3.connect('tl_data.db')
    #         return con
    #     except Error as e:
    #         self.ui.textBrowser.append(str(e))

    # 清空指定表
    def sql_delete_table(self, name):
        try:
            self.cur.execute("DELETE FROM {}".format(name))
            self.cur.execute("UPDATE sqlite_sequence SET seq=0 WHERE NAME ='%s'" % name)
            self.con.commit()
        except Error as e:
            self.ui.textBrowser.append(str(e))

    # 查询数据库角色数据并返给Combox赋值
    def role_init(self):
        query_role_sql = "select id,roleLabel FROM role"
        role_data = self.cur.execute(query_role_sql)
        cb_data = []
        for row in role_data:
            cb_data.append({"label": row[1], "id": row[0]})
        for item in cb_data:
            self.ui.comboBox.addItem(item['label'], userData=str(item['id']))
        current_role = self.ui.comboBox.currentData()
        MainWindow.show_role_right(self, current_role)

    def show_role_right(self, current_role):
        self.ui.treeWidget.clear()
        query_role_right_sql = "select * from role_menu_action where role_id = ? "
        top_menu_id = 0
        second_menu_id = 0
        query_role_right = self.cur.execute(query_role_right_sql, (current_role,))
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
        self.ui.treeWidget.expandAll()
        self.label_change()

    def label_change(self):
        current_role = self.ui.comboBox.currentData()
        query_is_changed_sql = "SELECT SUM(is_changed) FROM role_menu_action WHERE role_id = ?"
        query_changed_count = self.cur.execute(query_is_changed_sql, (current_role,))
        for item in query_changed_count:
            if item[0]:
                self.ui.label_2.setText("已调整权限：%d 项" % item[0])
            else:
                self.ui.label_2.setText("    当前用户无权限调整")

    def save_right_after(self):
        update_sql = "UPDATE role_menu_action SET is_right_after = ?, is_changed = 1 WHERE id = ? ".format()
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        role_label = self.ui.comboBox.currentText()
        self.ui.textBrowser.append("\n【%s】权限调整如下：" % role_label)
        while iterator.value():
            item = iterator.value()
            old_action = item.data(1, 1)
            action_ck = item.checkState(1)
            if action_ck == 2:
                action_ck = 1
            if old_action:
                if old_action[6] != action_ck:
                    if action_ck == 1:
                        self.ui.textBrowser.append("新增： %s-%s:%s " % (old_action[2], old_action[3], old_action[4]))
                    else:
                        self.ui.textBrowser.append("移除： %s-%s:%s " % (old_action[2], old_action[3], old_action[4]))
                    try:
                        self.cur.execute(update_sql, (action_ck, old_action[0]))
                        self.con.commit()
                    except Error as e:
                        self.ui.textBrowser.append(str(e))
            iterator += 1
        self.label_change()

    def discard_changed(self):
        update_sql = "UPDATE role_menu_action SET is_right_after = ?, is_changed = 0 WHERE id = ? ".format()
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        while iterator.value():
            item = iterator.value()
            old_action = item.data(1, 1)
            if old_action:
                action_ck = old_action[6]
                try:
                    self.cur.execute(update_sql, (action_ck, old_action[0]))
                    self.con.commit()
                except Error as e:
                    self.ui.textBrowser.append(str(e))
            iterator += 1
        MainWindow.show_role_right(self, self.ui.comboBox.currentData())
        self.ui.textBrowser.append("\n【%s】权限已重置成线上数据" % self.ui.comboBox.currentText())
        self.label_change()

    # 获取角色列表
    def get_role_list(self, token):
        url_role = 'https://bgateway.joyobpo.com/basic/role/multiList'
        self.headers["token"] = token
        json_data = {
            "pageNum": 1,
            "pageSize": 50,
            "roleLabel": "",
            "admType": 10,
            "rootOrgId": "1"
        }
        j_role_list = requests.post(url_role, json=json_data, headers=self.headers)
        role_list = j_role_list.json().get("data").get("pageInfo").get("list")
        return role_list

    # 获取角色权限包
    def get_role_tree(self, post_data):
        url_tree = 'https://bgateway.joyobpo.com/basic/role/getRoleMenuActionTree'
        self.headers["token"] = self.ui.lineEdit.text()
        tree = requests.post(url_tree, json=post_data, headers=self.headers)
        return tree.json()

    # 获取线上最新数据并更新数据库各表
    def update_role_data(self):
        token = self.ui.lineEdit.text()
        if len(token) < 50:
            QMessageBox.warning(self, "Warnning!", "Token 错误，请重新填写！", QMessageBox.Cancel)
            return
        menu_sql = 'insert into menu (menuId,menuPid,menuLabel) VALUES (?,?,?)'
        action_sql = 'insert into action (actionId,actionCode,actionLabel,menuPId) VALUES (?,?,?,?)'
        user_sql = 'insert into role_menu_action (role_id,role_label,menu_top_id,menu_top_label,menu_second_id,menu_second_label,action_id,action_label,range_code,is_right_before,is_right_after) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
        role_sql = 'insert into role (id,roleLabel) VALUES (?,?)'

        #  清空menu表及action表
        MainWindow.sql_delete_table(self, name="menu")
        MainWindow.sql_delete_table(self, name="action")
        MainWindow.sql_delete_table(self, name="role_menu_action")
        MainWindow.sql_delete_table(self, name="role")

        # 获取线上角色列表
        role_list = MainWindow.get_role_list(self, token)
        for role in role_list:
            role_id = role["id"]
            role_label = role["roleLabel"]
            self.ui.comboBox.addItem(role_label, userData=role_id)
            try:
                self.cur.execute(role_sql, (role_id, role_label))
                self.con.commit()
            except Error as e:
                self.ui.textBrowser.append(str(e))
            role_id_adm_type_dto_list = role.get("roleIdAdmTypeDtoList")
            QApplication.processEvents()
            self.ui.textBrowser.append("\n获取到角色：【%s】\n开始更新角色权限..." % role_label)
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
                        self.cur.execute(menu_sql, (menu_top_id, menu_pid, menu_top_label))
                        self.con.commit()
                        QApplication.processEvents()
                        self.ui.textBrowser.append("\n更新一级菜单：【%s】..." % menu_top_label)
                    except Error as e:
                        self.ui.textBrowser.append(str(e))
                for childMenu in topMenu.get("children"):
                    # 获取二级菜单数据
                    menu_second_id = childMenu.get("menuId")
                    menu_pid = childMenu.get("menuPId")
                    menu_second_label = childMenu.get("menuLabel")
                    if role_id == "1":
                        try:
                            self.cur.execute(menu_sql, (menu_second_id, menu_pid, menu_second_label))
                            self.con.commit()
                            QApplication.processEvents()
                            self.ui.textBrowser.append("+ 更新二级菜单：【%s】..." % menu_second_label)
                        except Error as e:
                            self.ui.textBrowser.append(str(e))
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
                                self.cur.execute(action_sql, (action_id, action_code, action_label, menu_second_id))
                                self.con.commit()
                                self.ui.textBrowser.append("+++ 更新操作菜单：【%s】" % action_label)
                            except Error as e:
                                self.ui.textBrowser.append(str(e))
                        # 写入用户权限包
                        try:
                            self.cur.execute(user_sql, (
                                role_id, role_label, menu_top_id, menu_top_label, menu_second_id, menu_second_label,
                                action_id, action_label, range_code, action_ck, action_ck))
                            self.con.commit()
                        except Error as e:
                            self.ui.textBrowser.append(str(e))
            self.ui.textBrowser.append("\n【%s】 权限更新完成" % role_label)
        self.show_role_right(self.ui.comboBox.currentData())

    def pre_changed(self):
        action_cgd_sql = "SELECT role_label,menu_top_label,menu_second_label,action_label,action_id FROM role_menu_action WHERE is_changed =1 AND is_right_after = ? ORDER BY action_id".format()
        action_add_cgd = self.cur.execute(action_cgd_sql, (1,))
        action_add = []
        role_add = []
        for item in action_add_cgd:
            if item[4] not in action_add:
                if role_add:
                    self.ui.textBrowser.append("角色： %s" % role_add)
                    role_add = []
                action_label = item[1] + "-" + item[2] + "::" + item[3]
                self.ui.textBrowser.append("\n本次新增权限：%s" % action_label)
                role_add.append("【%s】" % item[0])
                action_add.append(item[4])
            elif item[4] in action_add:
                role_add.append("【%s】" % item[0])
        if role_add:
            self.ui.textBrowser.append("角色： %s" % role_add)

        action_move_cgd = self.cur.execute(action_cgd_sql, (0,))
        action_move = []
        role_move = []
        for item in action_move_cgd:
            if item[4] not in action_move:
                if role_move:
                    self.ui.textBrowser.append("角色： %s" % role_move)
                    role_move = []
                action_label = item[1] + "-" + item[2] + "::" + item[3]
                self.ui.textBrowser.append("\n本次移除权限：%s" % action_label)
                role_move.append("【%s】" % item[0])
                action_move.append(item[4])
            elif item[4] in action_move:
                role_move.append("【%s】" % item[0])
        if role_move:
            self.ui.textBrowser.append("角色： %s" % role_move)
        if not action_add and not action_move:
            self.ui.textBrowser.append("\n暂无调整!")

    def select_role(self):
        current_role = self.ui.comboBox.currentData()
        MainWindow.show_role_right(self, current_role)

    def btn_send_email(self):
        self.ui.textBrowser.clear()
        self.pre_changed()
        mailForm = EmailForm(self)
        mailForm.show()


class EmailForm(QDialog):
    def __init__(self, parent=None):
        super(EmailForm, self).__init__(parent)
        self.ui = form.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModal)

    def get_input(self):
        version = self.ui.lineEdit.text()
        to_addr = self.ui.lineEdit_2.text()
        to_name = self.ui.lineEdit_3.text()
        send_addr = self.ui.lineEdit_4.text()
        pass_wd = self.ui.lineEdit_5.text()
        if not version:
            QMessageBox.warning(self, "输入错误", "版本号未填写", QMessageBox.Yes)
        elif not re.match("^\w{1,20}@joyowo.com", to_addr):
            QMessageBox.warning(self, "输入错误", "仅支持joyowo.com企业邮箱", QMessageBox.Yes)
        elif not re.match("^\w{1,20}@joyowo.com", send_addr):
            QMessageBox.warning(self, "输入错误", "仅支持joyowo.com企业邮箱", QMessageBox.Yes)
        elif not pass_wd:
            QMessageBox.warning(self, "输入错误", "邮箱密码未填写", QMessageBox.Yes)
        else:
            self.send_mail(version, to_addr, to_name, send_addr, pass_wd)

    def send_mail(self, v, to_addr, to_name, send_addr, pass_wd):
        smtp_server = 'smtphz.qiye.163.com'
        change_msg = mainWindow.ui.textBrowser.toPlainText()
        msg_body = '''
        Dear %s:\n
        %s 已经成功上线，为确保用户正常使用，需申请图灵正式环境角色权限调整。本次角色权限调整内容如下，请审批：
        %s
        ''' % (to_name, v, change_msg)
        msg = MIMEText(msg_body, 'plain', 'utf-8')
        msg['From'] = Header(send_addr)
        msg['To'] = Header(to_name)
        subject = '【权限申请】%s上线权限初始化申请' % v
        msg['Subject'] = Header(subject, 'utf-8')
        try:
            smtpobj = smtplib.SMTP_SSL(smtp_server)
            smtpobj.connect(smtp_server, 465)
            smtpobj.login(send_addr, pass_wd)
            smtpobj.sendmail(send_addr, to_addr, msg.as_string())
            QMessageBox.information(self, "Well Done！", "邮件发送成功！", QMessageBox.Yes)
            self.close()
        except smtplib.SMTPException as e:
            QMessageBox.critical(self, "Error", str(e), QMessageBox.Yes)

    def close(self) -> bool:
        self.setParent(None)
        self.deleteLater()
        return super(EmailForm,self).close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mail_form = EmailForm()
    mainWindow.show()
    sys.exit(app.exec_())
