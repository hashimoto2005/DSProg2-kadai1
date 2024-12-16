import flet as ft
from pathlib import Path
import json
import requests
from datetime import datetime

# カードの横ならび数
CARD_COUNT = 4
DAYS = 7


def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 10

    # ========== json 読み込み ================
    parent = Path(__file__).resolve().parent
    
    areas = requests.get("http://www.jma.go.jp/bosai/common/const/area.json").json()

    # コンソールから Forecast.Const.TELOPS と入力して取得したjson
    telops = json.load(open(parent.joinpath("telops.json")))
    # ========================================

    # ========== ヘッダー ===================== 
    header = ft.Container(
        content= ft.Row(controls=[
                ft.Icon(ft.Icons.WB_SUNNY, size=30, color="white"),
                ft.Text("天気予報", size=30, weight="bold", color="white"),
            ]),
        bgcolor="#4A148C",
        padding=10,
        alignment=ft.alignment.center_left
    )
    # ========================================

    # ============ body =====================
    def get_weather_data(code):
        URL = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
        res = requests.get(URL)
        try :
            data_json = res.json()
        except:
            raise Exception("天気予報の取得に失敗しました")
        
        for data in data_json:
            if len(data["timeSeries"][0]["timeDefines"]) == DAYS:
                return data
    
    def body(code):
        data = get_weather_data(code)
        area_num = len(data["timeSeries"][0]["areas"])
        def make_card(i, day):
            date = datetime.fromisoformat(data["timeSeries"][0]["timeDefines"][day]).date().isoformat()
            weather_code = data["timeSeries"][0]["areas"][i]["weatherCodes"][day]
            min_tmp = data["timeSeries"][1]["areas"][i]["tempsMin"][day]
            max_tmp = data["timeSeries"][1]["areas"][i]["tempsMax"][day]
            return ft.Card(
                content=ft.Column(
                    controls=[
                        ft.Row(controls = [ft.Text(date, size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER,),
                        ft.Row(controls = [ft.Image(src=f"https://www.jma.go.jp/bosai/forecast/img/{telops[weather_code][0]}")],
                                alignment=ft.MainAxisAlignment.CENTER,),
                        ft.Row(controls = [ft.Text(telops[weather_code][3]),], alignment=ft.MainAxisAlignment.CENTER,),
                        ft.Row(
                                controls=[
                                    ft.Text(f"{min_tmp} °C", color=ft.Colors.BLUE),
                                    ft.Text(" / "),
                                    ft.Text(f"{max_tmp} °C", color=ft.Colors.RED),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=200,
                height=200,
            )
        cols = []
        for i in range(area_num):
            area1 = data["timeSeries"][0]["areas"][i]["area"]["name"]
            area2 = data["timeSeries"][1]["areas"][i]["area"]["name"]
            cols += [   
                        ft.ListTile(
                            title=ft.Text(area1, size=20, weight="bold"),
                            subtitle=ft.Text(f"最低/最高気温は{area2}参照"),
                        ),
                        ft.Row(
                            controls=[
                                make_card(i, day)
                                for day in range(CARD_COUNT)
                            ]
                        ),
                        ft.Row(
                            controls=[
                                make_card(i, day)
                                for day in range(CARD_COUNT, DAYS)
                            ]
                        ),
                    ]
        return ft.ListView(expand=True, spacing=10, controls=cols)
    
    cards = body("130000") # 東京都 初期値

    # =======================================


    # ========== サイドバー ====================
    def select_area(e):
        area_code = e.control.subtitle.value
        cards = body(area_code)
        page.controls[1].controls.pop()
        page.controls[1].controls.append(cards)
        page.update()
            
    lv = ft.ListView(expand=True, spacing=10)
    lv.controls.append(
        ft.ExpansionTile(
            title=ft.Text("地域を選択"),
            controls=[
                ft.ExpansionTile(
                    title=ft.Text(value["name"]),
                    subtitle=ft.Text(key),
                    controls=[
                        ft.ListTile(
                            title=ft.Text(areas["offices"][code]["name"]),
                            subtitle=ft.Text(code),
                            on_click=select_area,
                        )
                        for code in value["children"]
                    ],
                ) for key, value in areas["centers"].items()
            ],
        )
    )
    nav_rail=ft.Container(
        width=300,
        content=lv,
        padding=ft.padding.symmetric(vertical=10),
    )

    def toggle_nav_rail(e):
        nav_rail.visible = not nav_rail.visible
        toggle_nav_rail_button.selected = not toggle_nav_rail_button.selected
        toggle_nav_rail_button.tooltip = "Open Side Bar" if toggle_nav_rail_button.selected else "Collapse Side Bar"
        page.update()

    toggle_nav_rail_button = ft.IconButton(
        icon=ft.Icons.ARROW_CIRCLE_LEFT,
        icon_color=ft.Colors.BLUE_GREY_400,
        selected=False,
        selected_icon=ft.Icons.ARROW_CIRCLE_RIGHT,
        on_click=toggle_nav_rail,
        tooltip="Collapse Nav Bar",   
    )

    # =======================================

    page.add(header,
             ft.Row(
                controls=[
                    nav_rail, # サイドバー本体
                    toggle_nav_rail_button, # サイドバーの開閉ボタン
                    cards, # カード
                ],
                expand=True, # 画面の空白部分を補うかどうか
                vertical_alignment="start", # 画面上部より表示
            )
        )
    # page.scroll="HIDDEN"
    page.update()


ft.app(target=main)
