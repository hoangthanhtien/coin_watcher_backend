from application import app
from application.database import db, redis_db
import json
import os


def write_price_data_to_file(file_name="csv_for_charts/current_prices.dat", data=None):
    if data:
        chart_header = "@ "
        prices_list = []
        for coin_id in data.keys():
            if len(list(data.keys())) <= 1:
                chart_header += f"{coin_id}"
            else:
                chart_header += f"{coin_id},"
            prices_list.append(data.get(coin_id))
        file = open(file_name, "w")
        chart_header = chart_header.rstrip(",")
        file.write(chart_header + "\n")
        for prices in zip(*prices_list):
            line_content = f"{prices[0]['datetime']}"
            for price in prices:
                line_content += f",{price['price']}"
            file.write(line_content + "\n")
        file.close()


def get_chart_colors(length=1):
    valid_colors = ["blue", "green", "magenta", "yellow", "black", "cyan"]
    result = ""
    if length > len(valid_colors):
        raise Exception("Biểu đồ hỗ trợ tối da 6 coin")
    for i in range(1, length + 1):
        result += valid_colors[i] + " "
    return result


def show_curr_price_chart(coin_ids=None):
    """Xuất file data rồi dùng file data đó để vẽ chart trên terminal
    :param str coin_ids: Chuỗi các coin_id ngăn cách nhau bởi dấu phẩy
    """
    coin_id_list = coin_ids.split(",")
    prices_info = {}
    valid_coin_id_num = 0
    for coin_id in coin_id_list:
        coin_price_info = redis_db.get(coin_id)
        if not coin_price_info:
            print(f"Giá của coin có id {coin_id} hiện đang không được theo dõi")
        else:
            valid_coin_id_num += 1
            prices_info[coin_id] = json.loads(coin_price_info)
    write_price_data_to_file(data=prices_info)
    chart_colors = get_chart_colors(length=valid_coin_id_num)
    os.system(
        f'termgraph ~/sourceCode/python/coin_watcher/repo/csv_for_charts/current_prices.dat --color {chart_colors} --title "Biểu đồ giá crypto hiện tại"'
    )
