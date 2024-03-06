import pandas as pd


# this function reads the data vertically. this function will only work if your data looks like this:
# !-1-- --2--- ---3---- --4-- ---5--- --6--- --7-- --8--- ---9---- 10 -11- ---12--- - ---14-- - --16- 17 --18- 19 --20-- 21
# !Samp Pressu Temperat Trans Fluores Oxygen Oxyge  PAR   Salinity Bo Numb Salinity F Oxygen: F Nitra Fl Silic Fl Phosph Fl
# !le_  re     ure:     missi cence:  :      n:           :T0:C0   tt er_o :Bottle  l Dissolv l te_   ag ate   ag ate    ag
# !Numb        Primary  vity  URU:    Dissol Disso                 ~u ~bin          ~ ed      ~ plus_ ~t       ~i        ~p
# !er                         Seapoin ved:   lved:                 mb _rec          l         e Nitri ri       ca        ha
# !                           t       SBE    SBE                   er ords          e         d te    te       te        te
# !---- ------ -------- ----- ------- ------ ----- ------ -------- -- ---- -------- - ------- - ----- -- ----- -- ------ --
# *END OF HEADER
#     6    2.6   5.4073  48.8   0.664   7.68 336.0    9.8  25.3794 12   41  25.4529 0   7.667 0   0.0 0    2.6 0    0.55 0
#     5   24.9   0.9359  50.4   1.598   8.11 354.5 9999.0  27.5703 11   41  27.5531 0   8.067 0   0.7 0    5.8 0    0.86 0
#     4   50.4  -0.3014  49.3   1.566   7.22 315.1 9999.0  27.9789 10   41  28.0918 0   7.233 0   4.2 0   14.1 0    1.19 0
#     3  100.1  -0.4492  53.2   0.311   6.12 267.0    0.1  28.5079  7   14  28.5155 0   6.776 0   8.0 0   27.3 0    1.45 0
#     2  149.2  -0.3500  53.4   0.249   5.80 253.1    0.1  28.6228  4   13  28.6298 0   5.834 0   8.9 0   31.6 0    1.51 0
#     1  170.3  -0.3256  52.3   0.256   5.71 249.1 4655.3  28.6395  1   21  28.6606 0   5.732 0   9.1 0   33.0 0    1.58 0
def read_table_vertically(cnv_file, fid, m):
    # get the header
    with open(cnv_file, 'r', errors="ignore") as file:
        content = file.readlines()
    header_data_line = ''
    i = m - 1
    while not all(char in content[i] for char in "!1-"):
        i -= 1
        header_data_line = content[i]
        header_data_line = header_data_line.lstrip("!")
    file = fid.readlines()
    split_items = []
    line = header_data_line
    for item in header_data_line.split():
        index = line.index(item)
        to_be_replaced = line[:line.index(item) + len(item)]
        line = line.replace(to_be_replaced, " " * len(to_be_replaced), 1)
        split_items.append(index)

    data = []
    for i in range(len(split_items)):
        tmp = []
        for li in file:
            if i + 1 < len(split_items):
                tmp.append(li[split_items[i]:split_items[i + 1]])
            else:
                tmp.append(li[split_items[i]:])
        data.append(tmp)

    # print(data)
    data = pd.DataFrame.transpose(pd.DataFrame(data))
    return data
