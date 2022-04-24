import efinance as ef

aa=ef.stock.getter.get_latest_holder_number()
ttt=aa[aa['股东户数统计截止日']=='2022-03-31 00:00:00']
print(ttt)