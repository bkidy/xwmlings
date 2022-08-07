import requests,json
import xlwings as xw

class ROLE():

    def __init__(self):
        self.tree_url = ''
        self.rolelist_url = ''
        # self.token = input("请输入最新的Token：")
        self.token = ''
        self.headers = {
            "accept":"application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "aid": "0",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://test3crm.joyobpo.net",
            "referer": "https://test3crm.joyobpo.net/",
            "token": self.token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            }
        return

    def get_role(self):
        role_data = {
            "pageNum": 1,
            "pageSize": 50,
            "roleLabel": "",
            "admType": 10,
            "rootOrgId": "1"
        }
        role = requests.post(self.rolelist_url,json=role_data,headers=self.headers)
        role_josn = role.json().get("data").get("pageInfo").get("list")
        return role_josn



    def insert_role_data(self):
        x = 2
        y = 5
        app = xw.App(visible=True, add_book=False)
        for role in ROLE().get_role():
            tl = app.books.open("tl.xlsx")
            sht = tl.sheets("sheet1")
            info = sht.used_range
            ncols = info.last_cell.column
            role_label = role.get("roleLabel")
            roleIdAdmTypeDtoList = role.get("roleIdAdmTypeDtoList")
            tree = requests.post(self.tree_url,json=roleIdAdmTypeDtoList,headers=self.headers)
            menuTreeByTuring = tree.json().get("data").get("menuTreeByTuring")
            if role_label == "直辖区-分总":
                ROLE().inert_menu(sht,menuTreeByTuring)
                print("菜单更新成功！")
            sht.range(x, y).value = role_label
            print("成功写入（%s,%s）:%s" % (x, y, role_label))
            for top_menu in menuTreeByTuring:
                topmenu_name = top_menu.get("menuLabel")
                topmenu_ck = top_menu.get("checked")
                second_menus = top_menu.get("children")
                for second_menu in second_menus:
                    secondmenu_name = second_menu.get("menuLabel")
                    secondmenu_ck = second_menu.get("checked")
                    actions = second_menu.get("actions")
                    for action in actions:
                        action_label = action.get("actionLabel")
                        action_ck = action.get("checked")
                        action_rng = action.get("range")
                        if action_label == "列表":
                            if action_ck == True:
                                if action_rng == 1:
                                    x = x + 1
                                    sht.range(x, y).value = "√"
                                    print("成功写入1（%s,%s）:本人" % (x, y))
                                    x = x + 2
                                elif action_rng == 4:
                                    x = x + 2
                                    sht.range(x, y).value = "√"
                                    print("成功写入2（%s,%s）:部门" % (x, y))
                                    x = x + 1
                                #列表数据中存在勾选但无range的情况，所以当做全部数据权限处理，否则影响后续数据
                                else:
                                    x = x + 3
                                    sht.range(x, y).value = "√"
                                    print("成功写入3（%s,%s）:全部" % (x, y))
                            else:
                                x = x + 3
                                print("列表-（%s,%s）无权限" % (x, y))
                        elif action_label != "列表":
                            if action_ck == True:
                                x = x + 1
                                sht.range(x,y).value = "√"
                                print("成功写入4（%s,%s）:%s" % (x, y, action_label))
                            else:
                                x = x + 1
                                print("无权限（%s,%s）:%s" % (x, y, action_label))
            y = y + 1
            x = 2
            tl.save()
            tl.close()


    def insert_role_label(self):
        role_label_list = []
        for role in ROLE().get_role():
            role_label = role.get("roleLabel")
            role_label_list.append(role_label)
        app = xw.App(visible=True, add_book=False)
        tl = app.books.open("tl.xlsx")
        sht = tl.sheets("sheet1")
        sht.range('E2').value = role_label_list
        tl.save()
        tl.close()

    def inert_menu(self,sht,menuTreeByTuring):
        # app = xw.App(visible=True, add_book=False)
        # tl = app.books.open("tl.xlsx")
        # sht = tl.sheets("sheet1")
        rngA = 3
        for top_menu in menuTreeByTuring:
            topmenu_name = top_menu.get("menuLabel")
            sht.range('A%d' % rngA).value = topmenu_name
            second_menus = top_menu.get("children")
            rngB = rngA
            for second_menu in second_menus:
                secondmenu_name = second_menu.get("menuLabel")
                sht.range('B%d' % rngB).value = secondmenu_name
                actions = second_menu.get("actions")
                rngC = rngB
                for action in actions:
                    action_name = action.get("actionLabel")
                    sht.range('C%d' % rngC).value = action_name
                    rngD = rngC
                    if action_name == "列表":
                        sht.range('D%d' % rngD).options(transpose=True).value = ["本人", "部门", "全部"]
                        sht.range('C%d:C%d' % (rngD, (rngD + 2))).api.merge
                        rngD = rngD + 2
                    sht.range('B%d:B%d' % (rngB, rngD)).api.merge
                    rngC = rngD + 1
                sht.range('A%d:A%d' % (rngA, rngD)).api.merge
                rngB = rngD + 1
            rngA = rngD + 1
        # tl.save()
        # tl.close()

    def indert_role_data(self):
        app = xw.App(visible=True, add_book=False)
        tl = app.books.open("tl.xlsx")
        sht = tl.sheets("sheet1")



ROLE().insert_role_data()