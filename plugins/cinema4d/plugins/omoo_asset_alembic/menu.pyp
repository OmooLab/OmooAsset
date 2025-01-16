import c4d
import typing

# 定义菜单数据类型
MenuData: typing.Type = dict[str, typing.Union[int, 'MenuData']]

# 定义要插入的菜单数据
MENU_DATA: MenuData = {
    "Import .abc (OmooAsset)": 1064257  # 插件命令 ID，示例 ID，请替换为实际命令 ID
    # "start": {
    #     "button": 1064257  # 插件命令 ID，示例 ID，请替换为实际命令 ID
    # }
}

def UpdateMenu(root: c4d.BaseContainer, title: str, data: MenuData, forceUpdate: bool = False) -> bool:
    """添加数据到指定根菜单下，根菜单中如果不存在该标题，则创建。
    
    当 forceUpdate 为 True 时，强制更新 Cinema 4D 菜单。
    """
    def doesContain(root: c4d.BaseContainer, title: str) -> bool:
        """测试根菜单中是否包含指定标题的子菜单。"""
        for _, value in root:
            if not isinstance(value, c4d.BaseContainer):
                continue
            elif value.GetString(c4d.MENURESOURCE_SUBTITLE) == title:
                return True
        return False
    
    def insert(root: c4d.BaseContainer, title: str, data: MenuData) -> c4d.BaseContainer:
        """递归地将数据插入到根菜单的指定标题下。"""
        # 创建一个新的容器并设置其标题
        subMenu: c4d.BaseContainer = c4d.BaseContainer()
        subMenu.InsData(c4d.MENURESOURCE_SUBTITLE, title)

        # 遍历数据中的值，插入命令，并对字典进行递归处理
        for key, value in data.items():
            if isinstance(value, dict):
                subMenu = insert(subMenu, key, value)
            elif isinstance(value, int):
                subMenu.InsData(c4d.MENURESOURCE_COMMAND, f"PLUGIN_CMD_{value}")
        
        root.InsData(c4d.MENURESOURCE_SUBMENU, subMenu)
        return root

    # 如果标题已存在，返回 False
    if doesContain(root, title):
        return False

    # 更新根菜单并根据需要强制更新菜单
    insert(root, title, data)
    if forceUpdate and c4d.threading.GeIsMainThreadAndNoDrawThread():
        c4d.gui.UpdateMenus()

    return True

def PluginMessage(mid: int, data: typing.Any) -> bool:
    """在 C4DPL_BUILDMENU 消息时更新菜单。"""
    if mid == c4d.C4DPL_BUILDMENU:
        # 获取 Cinema 4D 的主菜单并插入 MENU_DATA
        menu: c4d.BaseContainer = c4d.gui.GetMenuResource("M_EDITOR")
        UpdateMenu(root=menu, title="OmooAsset", data=MENU_DATA)

def SomeFunction():
    """在任何时候调用以更新菜单，只要调用来自主线程。"""
    # 获取 Cinema 4D 的主菜单并插入 MENU_DATA
    menu: c4d.BaseContainer = c4d.gui.GetMenuResource("M_EDITOR")
    UpdateMenu(root=menu, title="OmooAsset", data=MENU_DATA, forceUpdate=True)

if __name__ == "__main__":
    pass
