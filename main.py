import json
import xlwings as xw
from get_role import ROLE

#读取权限Json
# def openjson(filepath):
#     with open(filepath, encoding='utf-8') as f:
#         data = json.load(f)
#         tuling_json = data.get("data").get("menuTreeByTuring")
#         return tuling_json
role_josn = ROLE().get_tree()


#插入一级菜单
def insertmenu(json):
    app = xw.App(visible=True,add_book=False)
    tl = app.books.open("tl.xlsx")
    sht = tl.sheets("sheet1")
#获取一级菜单数据
    rngA = 3
    for top_menu in json:
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
                    sht.range('D%d' % rngD).options(transpose=True).value = ["本人","部门","全部"]
                    sht.range('C%d:C%d' % (rngD,(rngD+2))).api.merge
                    rngD = rngD + 2
                sht.range('B%d:B%d' % (rngB,rngD)).api.merge
                rngC = rngD +1
            sht.range('A%d:A%d' % (rngA,rngD)).api.merge
            rngB = rngD +1
        rngA = rngD +1
    return rngD

def insert_role_data(role_name,role_json):
    app = xw.App(visible=True,add_book=False)
    tl = app.books.open("tl.xlsx")
    sht = tl.sheets("sheet1")



