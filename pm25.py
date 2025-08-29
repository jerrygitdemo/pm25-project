import pymysql
import requests, os

table_str = """
create table if not exists pm25(
id int auto_increment primary key,
site varchar(25),
county varchar(50),
pm25 int,
datacreationdate datetime,
itemunit varchar(20),
unique key site_time (site,datacreationdate)
)
"""

sqlstr = "insert ignore into pm25(site,county,pm25,datacreationdate,itemunit)\
      values(%s,%s,%s,%s,%s)"

url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=JSON"

conn, cursor = None, None


from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 讀取環境變數
host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
port = int(os.getenv("MYSQL_PORT"))
database = os.getenv("MYSQL_DB")


def open_db():
    global conn, cursor
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database,
        )

        # print(conn)
        cursor = conn.cursor()
        cursor.execute(table_str)
        conn.commit()
        print("資料庫開啟成功!")
    except Exception as e:
        print(e)


def close_db():
    if conn is not None:
        conn.close()
        print("資料庫關閉成功!")


def get_open_data():
    resp = requests.get(url, verify=False)
    datas = resp.json()["records"]
    values = [list(data.values()) for data in datas if list(data.values())[2] != ""]
    return values


def write_data_to_mysql():
    try:
        open_db()
        size = write_to_sql()
        return {"result": "success", "size": size}
    except Exception as e:
        print(e)
    finally:
        close_db()
    return {"result": "failure", "size": size}


def write_to_sql():
    try:
        values = get_open_data()
        if len(values) == 0:
            print("目前無資料")
            return

        size = cursor.executemany(sqlstr, values)
        conn.commit()
        print(f"寫入{size}筆資料成功!")
        return size
    except Exception as e:
        print(e)
    return 0


def get_county_avg_pm25():
    try:
        open_db()
        sqlstr = """
        SELECT county,round(AVG(pm25),2) as avg_pm25 FROM pm25 group by county;
        """
        cursor.execute(sqlstr)
        result = [(data[0], float(data[1])) for data in cursor.fetchall()]

        return result
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


def get_data_from_mysql():
    try:
        open_db()
        sqlstr = (
            "select site,county,pm25,datacreationdate,itemunit "
            "from pm25 "
            "where datacreationdate=(select max(datacreationdate) from pm25);"
        )
        cursor.execute(sqlstr)
        datas = cursor.fetchall()

        return datas
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


if __name__ == "__main__":
    print(get_county_avg_pm25())
# print(get_data_from_mysql())

# open_db()
# write_to_sql()
# close_db()
