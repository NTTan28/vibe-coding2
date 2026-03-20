from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "123"

def get_db():
    return sqlite3.connect("library.db")

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        acc = conn.execute(
            "SELECT * FROM nhan_vien WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        ).fetchone()
        conn.close()

        if acc:
            session["user"] = acc[1]
            return redirect("/")
        else:
            return "Sai tài khoản"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")



# ================= USERS =================
@app.route("/users")
def users():
    conn = get_db()
    data = conn.execute("SELECT * FROM doc_gia").fetchall()
    conn.close()
    return render_template("users.html", users=data)

@app.route("/add_user", methods=["POST"])
def add_user():
    conn = get_db()
    conn.execute("""
    INSERT INTO doc_gia (ho_ten,lop,ngay_sinh,gioi_tinh)
    VALUES (?,?,?,?)
    """,(request.form["ten"],request.form["lop"],
         request.form["ngaysinh"],request.form["gioitinh"]))
    conn.commit()
    conn.close()
    return redirect("/users")

@app.route("/edit_user/<int:id>", methods=["GET","POST"])
def edit_user(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        UPDATE doc_gia
        SET ho_ten=?, lop=?, ngay_sinh=?, gioi_tinh=?
        WHERE ma_doc_gia=?
        """, (
            request.form["ten"],
            request.form["lop"],
            request.form["ngaysinh"],
            request.form["gioitinh"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/users")

    user = conn.execute("SELECT * FROM doc_gia WHERE ma_doc_gia=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_user.html", u=user)

@app.route("/delete_user/<int:id>")
def delete_user(id):
    conn = get_db()
    conn.execute("DELETE FROM phieu_muon WHERE ma_doc_gia=?", (id,))
    conn.execute("DELETE FROM doc_gia WHERE ma_doc_gia=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/users")

# ================= CHUYÊN NGÀNH =================
@app.route("/chuyen_nganh")
def chuyen_nganh():
    conn = get_db()
    data = conn.execute("SELECT * FROM chuyen_nganh").fetchall()
    conn.close()
    return render_template("chuyen_nganh.html", data=data)

@app.route("/add_chuyen_nganh", methods=["POST"])
def add_chuyen_nganh():
    ten = request.form["ten"]
    mota = request.form["mota"]
    conn = get_db()
    conn.execute("INSERT INTO chuyen_nganh VALUES (NULL, ?, ?)", (ten, mota))
    conn.commit()
    conn.close()
    return redirect("/chuyen_nganh")

@app.route("/edit_chuyen_nganh/<int:id>", methods=["GET", "POST"])
def edit_chuyen_nganh(id):
    conn = get_db()
    if request.method == "POST":
        ten = request.form["ten"]
        mota = request.form["mota"]
        conn.execute("""
            UPDATE chuyen_nganh
            SET ten_chuyen_nganh=?, mo_ta=?
            WHERE ma_chuyen_nganh=?
        """, (ten, mota, id))
        conn.commit()
        conn.close()
        return redirect("/chuyen_nganh")
    
    # GET: Hiển thị form sửa
    chuyen_nganh = conn.execute("SELECT * FROM chuyen_nganh WHERE ma_chuyen_nganh=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_chuyen_nganh.html", c=chuyen_nganh)

@app.route("/delete_chuyen_nganh/<int:id>")
def delete_chuyen_nganh(id):
    conn = get_db()
    # Xóa tất cả đầu sách thuộc chuyên ngành này trước (nếu muốn tránh lỗi FK)
    conn.execute("DELETE FROM dau_sach WHERE ma_chuyen_nganh=?", (id,))
    conn.execute("DELETE FROM chuyen_nganh WHERE ma_chuyen_nganh=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/chuyen_nganh")
# ================= ĐẦU SÁCH =================
@app.route("/dau_sach")
def dau_sach():
    conn = get_db()

    data = conn.execute("""
    SELECT dau_sach.*, chuyen_nganh.ten_chuyen_nganh
    FROM dau_sach
    LEFT JOIN chuyen_nganh
    ON dau_sach.ma_chuyen_nganh = chuyen_nganh.ma_chuyen_nganh
    """).fetchall()

    cn = conn.execute("SELECT * FROM chuyen_nganh").fetchall()

    conn.close()
    return render_template("dau_sach.html", data=data, chuyen_nganh=cn)

@app.route("/add_dau_sach", methods=["POST"])
def add_dau_sach():
    conn = get_db()
    conn.execute("""
    INSERT INTO dau_sach 
    (ten_sach, nha_xuat_ban, so_trang, kich_thuoc, tac_gia, so_luong, ma_chuyen_nganh)
    VALUES (?,?,?,?,?,?,?)
    """, (
        request.form["ten"],
        request.form["nxb"],
        request.form["trang"],
        request.form["size"],
        request.form["tacgia"],
        request.form["soluong"],
        request.form["ma_chuyen_nganh"]
    ))
    conn.commit()
    conn.close()
    return redirect("/dau_sach")

@app.route("/edit_dau_sach/<int:id>", methods=["GET","POST"])
def edit_dau_sach(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        UPDATE dau_sach
        SET ten_sach=?, nha_xuat_ban=?, so_trang=?, kich_thuoc=?, tac_gia=?, so_luong=?, ma_chuyen_nganh=?
        WHERE ma_dau_sach=?
        """, (
            request.form["ten"],
            request.form["nxb"],
            request.form["trang"],
            request.form["size"],
            request.form["tacgia"],
            request.form["soluong"],
            request.form["ma_chuyen_nganh"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/dau_sach")

    data = conn.execute("SELECT * FROM dau_sach WHERE ma_dau_sach=?", (id,)).fetchone()
    cn = conn.execute("SELECT * FROM chuyen_nganh").fetchall()
    conn.close()
    return render_template("edit_dau_sach.html", d=data, chuyen_nganh=cn)

@app.route("/delete_dau_sach/<int:id>")
def delete_dau_sach(id):
    conn = get_db()
    conn.execute("DELETE FROM sach WHERE ma_dau_sach=?", (id,))
    conn.execute("DELETE FROM dau_sach WHERE ma_dau_sach=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dau_sach")

# ================= SÁCH =================
@app.route("/books")
def books():
    conn = get_db()

    data = conn.execute("""
    SELECT sach.ma_sach, sach.ma_dau_sach, dau_sach.ten_sach, sach.tinh_trang, sach.ngay_nhap
    FROM sach
    JOIN dau_sach ON sach.ma_dau_sach = dau_sach.ma_dau_sach
    """).fetchall()

    dau_sach = conn.execute("SELECT * FROM dau_sach").fetchall()

    conn.close()
    return render_template("books.html", books=data, dau_sach=dau_sach, now=date.today().isoformat())

@app.route("/add_book", methods=["POST"])
def add_book():
    conn = get_db()
    conn.execute("INSERT INTO sach VALUES(NULL,?,?,?)",
                 (request.form["ma_dau_sach"],
                  request.form["tinh_trang"],
                  request.form["ngay_nhap"]))
    conn.commit()
    conn.close()
    return redirect("/books")

@app.route("/edit_book/<int:id>", methods=["GET","POST"])
def edit_book(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        UPDATE sach
        SET ma_dau_sach=?, tinh_trang=?, ngay_nhap=?
        WHERE ma_sach=?
        """, (
            request.form["ma_dau_sach"],
            request.form["tinh_trang"],
            request.form["ngay_nhap"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/books")

    book = conn.execute("SELECT * FROM sach WHERE ma_sach=?", (id,)).fetchone()
    dau_sach = conn.execute("SELECT * FROM dau_sach").fetchall()
    conn.close()
    return render_template("edit_book.html", b=book, dau_sach=dau_sach)

@app.route("/delete_book/<int:id>")
def delete_book(id):
    conn = get_db()
    conn.execute("DELETE FROM phieu_muon WHERE ma_sach=?", (id,))
    conn.execute("DELETE FROM sach WHERE ma_sach=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/books")

# ================= BORROW =================
@app.route("/borrow")
def borrow():
    conn = get_db()

    books = conn.execute("""
    SELECT sach.ma_sach, sach.ma_dau_sach, dau_sach.ten_sach, sach.tinh_trang
    FROM sach
    JOIN dau_sach ON sach.ma_dau_sach = dau_sach.ma_dau_sach
    WHERE sach.tinh_trang LIKE 'Còn%'
    """).fetchall()

    users = conn.execute("SELECT * FROM doc_gia").fetchall()

    conn.close()
    return render_template("borrow.html", books=books, users=users)

@app.route("/borrow_book", methods=["POST"])
def borrow_book():
    conn = get_db()

    user_id = request.form.get("user_id")
    sach_id = request.form.get("sach_id")

    if not user_id or not sach_id:
        return "❌ Thiếu dữ liệu!"

    check_user = conn.execute("""
    SELECT * FROM phieu_muon
    WHERE ma_doc_gia=? AND tinh_trang='Đang mượn'
    """, (user_id,)).fetchone()

    if check_user:
        conn.close()
        return "❌ Sinh viên đã mượn 1 cuốn!"

    check_book = conn.execute("""
    SELECT * FROM sach
    WHERE ma_sach=? AND tinh_trang LIKE 'Còn%'
    """, (sach_id,)).fetchone()

    if not check_book:
        conn.close()
        return "❌ Sách không còn!"

    conn.execute("""
    INSERT INTO phieu_muon (ma_sach, ma_doc_gia, ngay_muon, ngay_tra, tinh_trang)
    VALUES (?, ?, date('now'), NULL, 'Đang mượn')
    """, (sach_id, user_id))

    conn.execute("UPDATE sach SET tinh_trang='Đang mượn' WHERE ma_sach=?", (sach_id,))

    conn.commit()
    conn.close()

    return redirect("/borrow")

# ================= RETURN =================
@app.route("/return")
def return_page():
    conn = get_db()
    # Lấy tất cả phiếu mượn đang mượn
    data = conn.execute("""
        SELECT phieu_muon.ma_phieu,
               dau_sach.ten_sach,
               doc_gia.ho_ten,
               phieu_muon.ngay_muon,
               phieu_muon.tinh_trang,
               phieu_muon.ma_sach
        FROM phieu_muon
        JOIN sach ON phieu_muon.ma_sach = sach.ma_sach
        JOIN dau_sach ON sach.ma_dau_sach = dau_sach.ma_dau_sach
        JOIN doc_gia ON phieu_muon.ma_doc_gia = doc_gia.ma_doc_gia
        WHERE phieu_muon.tinh_trang='Đang mượn'
    """).fetchall()
    conn.close()
    return render_template("return.html", data=data)


@app.route("/return_book", methods=["POST"])
def return_book():
    ma_phieu = request.form["ma_phieu"]
    ma_sach = request.form["ma_sach"]

    conn = get_db()
    # Cập nhật phiếu mượn
    conn.execute("""
        UPDATE phieu_muon
        SET tinh_trang='Đã trả', ngay_tra=date('now')
        WHERE ma_phieu=?
    """, (ma_phieu,))

    # Cập nhật trạng thái sách
    conn.execute("""
        UPDATE sach
        SET tinh_trang='Còn'
        WHERE ma_sach=?
    """, (ma_sach,))

    conn.commit()
    conn.close()

    return redirect("/return")
# ================= REPORT =================
@app.route("/report")
def report():
    conn = get_db()

    # Top sách được mượn nhiều nhất
    top = conn.execute("""
        SELECT dau_sach.ten_sach, COUNT(*) as so_lan_muon
        FROM phieu_muon
        JOIN sach ON phieu_muon.ma_sach = sach.ma_sach
        JOIN dau_sach ON sach.ma_dau_sach = dau_sach.ma_dau_sach
        GROUP BY dau_sach.ten_sach
        ORDER BY so_lan_muon DESC
        LIMIT 10
    """).fetchall()

    # Các phiếu mượn chưa trả
    late = conn.execute("""
        SELECT phieu_muon.ma_phieu,
               dau_sach.ten_sach,
               doc_gia.ho_ten,
               phieu_muon.ngay_muon,
               phieu_muon.tinh_trang
        FROM phieu_muon
        JOIN sach ON phieu_muon.ma_sach = sach.ma_sach
        JOIN dau_sach ON sach.ma_dau_sach = dau_sach.ma_dau_sach
        JOIN doc_gia ON phieu_muon.ma_doc_gia = doc_gia.ma_doc_gia
        WHERE phieu_muon.tinh_trang='Đang mượn'
    """).fetchall()

    conn.close()
    return render_template("report.html", top=top, late=late)
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)