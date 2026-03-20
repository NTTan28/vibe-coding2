import sqlite3
import pandas as pd

conn = sqlite3.connect("library.db")

# ===== TABLE =====
conn.execute("""CREATE TABLE IF NOT EXISTS doc_gia(
ma_doc_gia INTEGER PRIMARY KEY AUTOINCREMENT,
ho_ten TEXT,lop TEXT,ngay_sinh TEXT,gioi_tinh TEXT)""")

conn.execute("""CREATE TABLE IF NOT EXISTS nhan_vien(
ma_nv INTEGER PRIMARY KEY AUTOINCREMENT,
ten_nv TEXT,username TEXT,password TEXT,role TEXT)""")

conn.execute("""CREATE TABLE IF NOT EXISTS chuyen_nganh(
ma_chuyen_nganh INTEGER PRIMARY KEY AUTOINCREMENT,
ten_chuyen_nganh TEXT,mo_ta TEXT)""")

conn.execute("""CREATE TABLE IF NOT EXISTS dau_sach(
ma_dau_sach INTEGER PRIMARY KEY AUTOINCREMENT,
ten_sach TEXT,nha_xuat_ban TEXT,so_trang INTEGER,
kich_thuoc TEXT,tac_gia TEXT,so_luong INTEGER,
ma_chuyen_nganh INTEGER)""")

conn.execute("""CREATE TABLE IF NOT EXISTS sach(
ma_sach INTEGER PRIMARY KEY AUTOINCREMENT,
ma_dau_sach INTEGER,tinh_trang TEXT,ngay_nhap TEXT)""")

conn.execute("""CREATE TABLE IF NOT EXISTS phieu_muon(
ma_phieu INTEGER PRIMARY KEY AUTOINCREMENT,
ma_sach INTEGER,ma_doc_gia INTEGER,
ngay_muon TEXT,ngay_tra TEXT,tinh_trang TEXT)""")

# ===== LOAD CSV =====
pd.read_csv("data/doc_gia.csv").to_sql("doc_gia", conn, if_exists="append", index=False)
pd.read_csv("data/chuyen_nganh.csv").to_sql("chuyen_nganh", conn, if_exists="append", index=False)
pd.read_csv("data/dau_sach.csv").to_sql("dau_sach", conn, if_exists="append", index=False)
pd.read_csv("data/sach.csv").to_sql("sach", conn, if_exists="append", index=False)
pd.read_csv("data/phieu_muon.csv").to_sql("phieu_muon", conn, if_exists="append", index=False)

# USER
conn.execute("INSERT INTO nhan_vien VALUES (NULL,'Admin','admin','123','admin')")
conn.execute("INSERT INTO nhan_vien VALUES (NULL,'Staff','staff','123','staff')")

conn.commit()
conn.close()

print("DONE")