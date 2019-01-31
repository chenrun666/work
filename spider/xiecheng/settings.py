# 出发地
STARTLOCAL = "太原"
# 目的地
ENDLOCAL = "昆明"

# 地方名对应的代号
# CODE = {"深圳": ["SZX", 2], "昆明": ["KMG", 34]}
# 加载城市名字和代码
import xlrd

CITYCODE = {}
workbook = xlrd.open_workbook(r"./cityname.xls")
sheet_name = workbook.sheet_by_name("Sheet2")
# 获取行数和列数
rows = sheet_name.nrows
cols = sheet_name.ncols
for r in range(4, rows):
    r_content = sheet_name.row_values(r)
    for item in range(0, cols, 2):
        CITYCODE[r_content[item]] = r_content[item + 1]

# 出发日期
STARTDATE = "2019-02-20"
# 返回日期
ENDDATE = ""

# 是否有婴儿
HASBABY = False
# 是否有孩子
HASCHILD = False

#
FLIGHTWAY = "Oneway"

if __name__ == '__main__':
    import xlrd

    city_code_dic = {}
    workbook = xlrd.open_workbook(r"./cityname.xls")
    sheet_name = workbook.sheet_by_name("Sheet2")
    # 获取行数和列数
    rows = sheet_name.nrows
    cols = sheet_name.ncols
    for r in range(4, rows):
        r_content = sheet_name.row_values(r)
        for item in range(0, cols, 2):
            city_code_dic[r_content[item]] = r_content[item + 1]
