"""Sinh cac bieu do hoat dong (TikZ) cho bao cao — Quan ly nha tro & thanh toan tien thue.
Moi bieu do: cac lan (swimlane) kem do rong, cac nut (id, kieu, lan, dx, hang, chu, rong) va cac canh.
Chay: python gen_activity.py  -> ghi cac tep hd-XX-*.tex trong thu muc nay.
Quy uoc: lan nguoi dung chi chua thao tac cua nguoi dung (nhap, chon, bam, mo trang);
moi dau ra (hien thi, thong bao, cap nhat giao dien) va nut ket thuc dat o lan He thong."""
import pathlib

HERE = pathlib.Path(__file__).parent
RS = 1.8  # khoang cach giua 2 hang (cm); chu trong o he thong dai nen gian hon mau
WF = 1.1  # he so noi rong o chu (bu cho co chu 11pt)

PREAMBLE = r"""\documentclass[11pt,border=6pt]{standalone}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shapes.geometric,calc}
\tikzset{
  act/.style={rectangle,rounded corners=6pt,draw,thick,fill=white,align=center,font=\small,minimum height=0.8cm,inner sep=3pt},
  dec/.style={diamond,aspect=2,draw,thick,fill=white,align=center,font=\footnotesize,inner sep=0.5pt},
  mrg/.style={diamond,draw,thick,fill=white,minimum size=0.6cm,inner sep=0pt},
  st/.style={circle,fill=black,minimum size=0.42cm,inner sep=0pt},
  en/.style={circle,draw,thick,minimum size=0.5cm,inner sep=0pt,path picture={\fill[black] (path picture bounding box.center) circle (0.14);}},
  arr/.style={thick,-{Stealth[length=2.4mm]}},
  lbl/.style={font=\footnotesize,inner sep=1.5pt,fill=white},
}
\begin{document}
\hyphenpenalty=10000 \exhyphenpenalty=10000
\begin{tikzpicture}
"""


def build(name, lanes, nodes, edges, rows=None):
    """lanes: [(ten, rong_cm)]
    nodes: (id, kieu, lan, dx, hang, chu, rong_chu_cm)  kieu: st/en/act/dec/mrg
    edges: (tu, den, nhan, duong); duong: "--", "-|", "|-", duong TikZ tuy y (co mui ten),
           hoac "RAW:<lenh tikz>" (ghi nguyen van)."""
    out = [PREAMBLE]
    xs, acc = [], 0.0
    for _, w in lanes:
        xs.append(acc + w / 2)
        acc += w
    total = acc
    nrows = rows if rows is not None else max(n[4] for n in nodes) + 1
    top, bottom = 0.9, -(nrows - 0.4) * RS
    out.append(rf"\draw[thick] (0,{top + 0.8}) rectangle ({total},{bottom:.2f});")
    out.append(rf"\draw[thick] (0,{top}) -- ({total},{top});")
    acc = 0.0
    for i, (lane, w) in enumerate(lanes):
        out.append(rf"\node[font=\bfseries\small,align=center] at ({acc + w / 2},{top + 0.4}) {{{lane}}};")
        if i:
            out.append(rf"\draw[thick] ({acc},{top + 0.8}) -- ({acc},{bottom:.2f});")
        acc += w
    pos, kinds = {}, {}
    for nid, kind, lane, dx, row, text, width in nodes:
        x, y = xs[lane] + dx, -row * RS
        pos[nid], kinds[nid] = (x, y), kind
        opt = kind
        if kind == "act":
            opt += f",text width={(width or 4.6) * WF:.2f}cm"
        if kind == "dec":
            opt += f",text width={(width or 1.7) * WF:.2f}cm"
        text = text.replace("%", r"\%").replace("&", r"\&")
        out.append(rf"\node[{opt}] ({nid}) at ({x:.2f},{y:.2f}) {{{text}}};")
    for e in edges:
        a, b, label, route = (list(e) + [None] * 4)[:4]
        route = route or "--"
        if route.startswith("RAW:"):
            out.append(route[4:])
            continue
        if route not in ("--", "-|", "|-"):
            out.append(rf"\draw[arr] {route};")
            continue
        (xa, ya), (xb, yb) = pos[a], pos[b]
        src = a
        if kinds[a] == "dec" and route == "-|":
            src = f"{a}.{'west' if xb < xa else 'east'}"
        lab = ""
        if label:
            if route == "-|":
                where = "pos=0,above left" if xb < xa else "pos=0,above right"
            elif route == "--" and abs(xa - xb) < 0.05:
                where = "pos=0.45,right"
            else:
                where = "pos=0.5,above"
            lab = f"node[lbl,{where}] {{[{label}]}} "
        out.append(rf"\draw[arr] ({src}) {route} {lab}({b});")
    out.append(r"\end{tikzpicture}" + "\n" + r"\end{document}" + "\n")
    (HERE / f"{name}.tex").write_text("\n".join(out), encoding="utf-8")


def bypass(a, b, label, d=1.0, side="east"):
    """Nhanh vong ngoai tu canh cua nut quyet dinh a toi canh cung phia cua nut b."""
    sgn = 1 if side == "east" else -1
    return (a, b, None, rf"({a}.{side}) -- node[lbl,pos=0,{'above right' if sgn > 0 else 'above left'}]{{[{label}]}} ++({sgn * d},0) |- ({b}.{side})")



# ---------------- Biểu đồ hoạt động: Quản lý nhà trọ & thanh toán tiền thuê ----------------
# Làn người dùng chỉ chứa thao tác của người dùng; làn Hệ thống gồm web, backend, MySQL và smart contract.
USR, SYS = ("Người dùng", 6.4), ("Hệ thống", 10.2)
LL, TT = ("Chủ nhà", 6.4), ("Người thuê", 6.4)
# Cột chính / cột phụ trong làn Hệ thống (lệch so với tâm làn). Ô chính cách mép trái làn ~0.35cm,
# hai cột cách nhau ~0.45cm, bên phải ô phụ còn ~0.6cm cho đường vòng (BY) mà không chạm viền khung.
M, R = -2.0, 2.85
WM, WR = 4.8, 2.8   # độ rộng chữ của ô ở cột chính / cột phụ
BY = 0.3            # đường vòng ra bên phải ô phụ (cm)

# 1. Đăng nhập bằng Google
build("hd-01-dang-nhap", [USR, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Bấm “Đăng nhập bằng Google”", 4.0),
    ("b1", "act", 1, M, 2, "Tạo state ngẫu nhiên,\\\\chuyển sang trang chọn tài khoản Google", WM),
    ("a2", "act", 0, 0, 3.2, "Chọn tài khoản Google,\\\\đồng ý cấp quyền", 4.0),
    ("b2", "act", 1, M, 4.4, "Nhận code và state Google gửi về", WM),
    ("d1", "dec", 1, M, 5.6, "state\\\\hợp lệ?", 1.2),
    ("b3", "act", 1, M, 7.0, "Đổi code lấy ID token, lưu tài khoản,\\\\tạo phiên đăng nhập", WM),
    ("ax", "act", 1, R, 7.0, "Hiển thị\\\\thông báo lỗi", WR),
    ("d2", "dec", 1, M, 8.4, "Đã có\\\\nickname?", 1.3),
    ("a3", "act", 0, 0, 9.7, "Nhập nickname", 4.0),
    ("b4", "act", 1, M, 10.7, "Lưu nickname, mở trang Tổng quan", WM),
    ("mf", "mrg", 1, 0, 11.8, "", None),
    ("e", "en", 1, 0, 12.7, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "a2", None, "-|"), ("a2", "b2", None, "-|"), ("b2", "d1"),
    ("d1", "b3", "Có"), ("d1", "ax", "Không", "-|"), ("b3", "d2"),
    ("d2", "a3", "Chưa", "-|"), ("d2", "b4", "Có"), ("a3", "b4", None, "|-"),
    ("b4", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])

# 2. Liên kết ví MetaMask
build("hd-02-lien-ket-vi", [USR, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Bấm “Kết nối ví”", 4.0),
    ("b1", "act", 1, M, 1, "Yêu cầu MetaMask cấp địa chỉ ví đang chọn", WM),
    ("b2", "act", 1, M, 2.2, "Tạo message liên kết gồm email, địa chỉ ví,\\\\nonce và thời gian", WM),
    ("a2", "act", 0, 0, 3.4, "Ký message trên MetaMask", 4.0),
    ("b3", "act", 1, M, 4.6, "Khôi phục địa chỉ ví từ chữ ký", WM),
    ("d1", "dec", 1, M, 6.0, "Chữ ký khớp, ví chưa\\\\thuộc tài khoản khác?", 2.1),
    ("b4", "act", 1, M, 7.5, "Lưu địa chỉ ví vào tài khoản", WM),
    ("ax", "act", 1, R, 7.5, "Hiển thị\\\\thông báo lỗi", WR),
    ("b5", "act", 1, M, 8.7, "Hiển thị ví đã liên kết; tên người dùng\\\\hiện trong hợp đồng thay cho địa chỉ ví", WM),
    ("mf", "mrg", 1, 0, 9.9, "", None),
    ("e", "en", 1, 0, 10.8, "", None),
], [
    ("s", "a1"), ("a1", "b1"), ("b1", "b2"), ("b2", "a2", None, "-|"), ("a2", "b3", None, "-|"), ("b3", "d1"),
    ("d1", "b4", "Có"), ("d1", "ax", "Không", "-|"), ("b4", "b5"),
    ("b5", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])

# 3. Khách tìm phòng & gửi yêu cầu thuê
build("hd-03-tim-phong", [TT, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Mở trang “Tìm phòng”", 4.0),
    ("b1", "act", 1, M, 2.0, "Lấy các phòng không có hợp đồng chờ ký\\\\hoặc đang thuê, kèm giá, cọc, thiết bị", WM),
    ("a2", "act", 0, 0, 3.2, "Lọc theo giá / từ khoá,\\\\chọn phòng phù hợp", 4.0),
    ("a3", "act", 0, 0, 4.4, "Nhập lời nhắn, bấm “Gửi yêu cầu thuê”", 4.4),
    ("d1", "dec", 1, M, 5.7, "Yêu cầu\\\\hợp lệ?", 1.3),
    ("b2", "act", 1, M, 7.1, "Lưu yêu cầu thuê trạng thái “Chờ chủ nhà\\\\phản hồi”, hiện ở trang Phòng của chủ nhà", WM),
    ("ax", "act", 1, R, 7.1, "Hiển thị\\\\thông báo lỗi", WR),
    ("a4", "act", 0, 0, 8.4, "Hẹn chủ nhà xem phòng\\\\và thoả thuận", 4.0),
    ("mf", "mrg", 1, 0, 9.6, "", None),
    ("e", "en", 1, 0, 10.5, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "a2", None, "-|"), ("a2", "a3"), ("a3", "d1", None, "-|"),
    ("d1", "b2", "Có"), ("d1", "ax", "Không", "-|"), ("b2", "a4", None, "-|"),
    ("a4", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])

# 4. Chủ nhà tạo hợp đồng thuê trên blockchain
build("hd-04-tao-hop-dong", [LL, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Chọn phòng trống, bấm “Hợp đồng”;\\\\chọn khách đã thoả thuận", 4.4),
    ("a2", "act", 0, 0, 2.3, "Nhập tiền phòng, tiền cọc, kỳ thanh\\\\toán, số kỳ; xác nhận trên MetaMask", 4.4),
    ("b1", "act", 1, M, 3.5, "Smart contract kiểm tra người thuê hợp lệ,\\\\tiền phòng > 0, số kỳ 1–240", WM),
    ("d1", "dec", 1, M, 4.9, "Hợp lệ?", 1.1),
    ("b2", "act", 1, M, 6.2, "Tạo hợp đồng trạng thái “Chờ ký”,\\\\phát sự kiện LeaseCreated", WM),
    ("ax", "act", 1, R, 6.2, "Hiển thị lý do\\\\bị từ chối", WR),
    ("b3", "act", 1, M, 7.5, "Backend đọc lại hợp đồng trên chain, lưu\\\\HOPDONG, gắn với phòng, tạo hồ sơ khách", WM),
    ("b4", "act", 1, M, 8.8, "Yêu cầu thuê chuyển “Đã tạo hợp đồng”,\\\\phòng chuyển “Chờ ký”", WM),
    ("mf", "mrg", 1, 0, 10.0, "", None),
    ("e", "en", 1, 0, 10.9, "", None),
], [
    ("s", "a1"), ("a1", "a2"), ("a2", "b1", None, "-|"), ("b1", "d1"),
    ("d1", "b2", "Có"), ("d1", "ax", "Không", "-|"), ("b2", "b3"), ("b3", "b4"),
    ("b4", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])

# 5. Người thuê ký hợp đồng & đặt cọc
build("hd-05-ky-hop-dong", [TT, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Mở hợp đồng “Chờ ký” trong\\\\“Phòng đang thuê”", 4.0),
    ("b1", "act", 1, M, 2.1, "Hiển thị điều khoản: tiền phòng, cọc,\\\\kỳ hạn, số tiền cần gửi khi ký", WM),
    ("d0", "dec", 0, 0, 3.4, "Đồng ý?", 1.1),
    ("a2", "act", 0, 0, 4.8, "Bấm “Ký & thanh toán”, xác nhận\\\\gửi cọc + tiền phòng kỳ đầu", 4.4),
    ("ar", "act", 1, R, 3.4, "cancelLease: huỷ\\\\hợp đồng chưa ký", WR),
    ("b2", "act", 1, M, 6.0, "Smart contract kiểm tra đúng người thuê\\\\và đúng số tiền cọc + kỳ đầu", WM),
    ("d1", "dec", 1, M, 7.3, "Hợp lệ?", 1.1),
    ("b3", "act", 1, M, 8.6, "Giữ tiền cọc, chuyển kỳ đầu cho\\\\chủ nhà, hợp đồng “Đang thuê”", WM),
    ("ax", "act", 1, R, 8.6, "Hiển thị lý do\\\\bị từ chối", WR),
    ("b4", "act", 1, M, 9.9, "Backend đồng bộ sự kiện LeaseSigned:\\\\phòng chuyển “Đã thuê”", WM),
    ("mf", "mrg", 1, 0, 11.1, "", None),
    ("e", "en", 1, 0, 12.0, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "d0", None, "-|"), ("d0", "a2", "Có"), ("d0", "ar", "Không"),
    ("a2", "b2", None, "-|"), ("b2", "d1"), ("d1", "b3", "Có"), ("d1", "ax", "Không", "-|"), ("b3", "b4"),
    ("b4", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("ar", "mf", None, "RAW:\\draw[arr] (ar.east) -- ++(" + str(BY) + ",0) |- (mf.east);"), ("mf", "e"),
])

# 6. Ghi chỉ số điện nước & tạo hoá đơn tháng
build("hd-06-chi-so-hoa-don", [LL, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Mở “Chỉ số điện nước”, chọn tháng", 4.4),
    ("b1", "act", 1, M, 2.0, "Lấy chỉ số mới tháng trước làm chỉ số cũ\\\\tháng này cho từng phòng", WM),
    ("a2", "act", 0, 0, 3.2, "Nhập chỉ số mới điện, nước", 4.4),
    ("d1", "dec", 1, M, 4.4, "Mới ≥ cũ?", 1.3),
    ("ax", "act", 1, R, 4.4, "Tô đỏ ô tiêu thụ,\\\\khoá nút Lưu", WR),
    ("b2", "act", 1, M, 5.7, "Lưu chỉ số điện nước vào SUDUNGDV", WM),
    ("a3", "act", 0, 0, 6.9, "Bấm “Tạo hoá đơn tháng”", 4.4),
    ("b3", "act", 1, M, 8.1, "Với mỗi phòng đang thuê đủ chỉ số: tính tiền\\\\điện, nước theo chỉ số × đơn giá", WM),
    ("b4", "act", 1, M, 9.4, "Cộng dịch vụ cố định\\\\và 1 kỳ tiền phòng nếu hợp đồng còn kỳ", WM),
    ("b5", "act", 1, M, 10.7, "Lưu HOADON “Chưa phát hành”, báo các\\\\phòng bị bỏ qua", WM),
    ("mf", "mrg", 1, 0, 11.9, "", None),
    ("e", "en", 1, 0, 12.8, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "a2", None, "-|"), ("a2", "d1", None, "-|"),
    ("d1", "b2", "Có"), ("d1", "ax", "Không"), ("b2", "a3", None, "-|"), ("a3", "b3", None, "-|"), ("b3", "b4"), ("b4", "b5"),
    ("b5", "mf", None, "|-"), ("ax", "mf", None, "RAW:\\draw[arr] (ax.east) -- ++(" + str(BY) + ",0) |- (mf.east);"), ("mf", "e"),
])

# 7. Xuất hoá đơn & thanh toán trên blockchain
L3 = [("Chủ nhà", 5.2), ("Người thuê", 5.2), SYS]
build("hd-07-xuat-thanh-toan-hoa-don", L3, [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Bấm “Xuất” hoá đơn,\\\\xác nhận trên MetaMask", 3.6),
    ("b1", "act", 2, M, 2.1, "Smart contract issueBill, phát BillIssued", WM),
    ("b2", "act", 2, M, 3.5, "Backend kiểm tra hoá đơn trên chain khớp\\\\số tiền, gắn mã; trạng thái “Chờ thanh toán”", WM),
    ("t1", "act", 1, 0, 5.0, "Mở “Hoá đơn của tôi”, xem\\\\chi tiết, bấm “Thanh toán”", 3.6),
    ("b3", "act", 2, M, 6.3, "Smart contract kiểm tra đúng người thuê,\\\\đúng số tiền, chưa trả, chưa huỷ", WM),
    ("d1", "dec", 2, M, 7.6, "Hợp lệ?", 1.1),
    ("b4", "act", 2, M, 8.9, "Cộng tiền vào số dư chủ nhà, cộng kỳ tiền\\\\phòng vào hợp đồng, phát BillPaid", WM),
    ("ax", "act", 2, R, 8.9, "Hiển thị lý do\\\\bị từ chối", WR),
    ("b5", "act", 2, M, 10.4, "Backend ghi PHIEUTHANHTOAN,\\\\hoá đơn “Đã thu đủ”, cập nhật doanh thu", WM),
    ("mf", "mrg", 2, 0, 11.7, "", None),
    ("e", "en", 2, 0, 12.6, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "b2"), ("b2", "t1", None, "-|"), ("t1", "b3", None, "-|"),
    ("b3", "d1"), ("d1", "b4", "Có"), ("d1", "ax", "Không", "-|"), ("b4", "b5"),
    ("b5", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])

# 8. Gia hạn hợp đồng (cần cả hai bên đồng ý)
build("hd-08-gia-han", [("Bên đề xuất", 5.2), ("Bên còn lại", 5.2), SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Nhập số kỳ gia hạn, bấm\\\\“Đề xuất gia hạn”", 3.6),
    ("b1", "act", 2, M, 2.1, "Smart contract kiểm tra hợp đồng đang thuê,\\\\chưa hết hạn, tổng số kỳ ≤ 240", WM),
    ("b2", "act", 2, M, 3.4, "Lưu đề xuất gia hạn,\\\\phát ExtensionProposed", WM),
    ("d0", "dec", 1, 0, 4.8, "Đồng ý?", 1.1),
    ("b3", "act", 2, M, 4.8, "acceptExtension: cộng số kỳ, kéo dài\\\\ngày hết hạn, phát LeaseExtended", WM),
    ("b4", "act", 2, R, 6.4, "cancelExtension:\\\\xoá đề xuất", WR),
    ("mf", "mrg", 2, 0, 7.6, "", None),
    ("e", "en", 2, 0, 8.5, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "b2"), ("b2", "d0", None, "-|"),
    ("d0", "b3", "Có"), ("d0", "b4", "Không", "|-"),
    ("b3", "mf", None, "|-"), ("b4", "mf", None, "|-"), ("mf", "e"),
])

# 9. Trả phòng: kết thúc hợp đồng & quyết toán tiền cọc
build("hd-09-tra-phong-quyet-toan-coc", [LL, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Mở hợp đồng của phòng", 4.0),
    ("d1", "dec", 1, M, 2.3, "Hết hạn hoặc\\\\khách nợ > 1 kỳ?", 1.9),
    ("ax", "act", 1, R, 3.6, "Thông báo chưa\\\\được kết thúc", WR),
    ("a2", "act", 0, 0, 3.8, "Kiểm tra THIETBI trong phòng,\\\\nhập số tiền khấu trừ và lý do", 4.4),
    ("b1", "act", 1, M, 5.0, "Smart contract kiểm tra khấu trừ ≤ tiền cọc,\\\\có lý do khi khấu trừ", WM),
    ("d2", "dec", 1, M, 6.4, "Hợp lệ?", 1.1),
    ("ay", "act", 1, R, 6.4, "Hiển thị lý do\\\\bị từ chối", WR),
    ("b2", "act", 1, M, 7.8, "Hoàn phần cọc còn lại cho người thuê,\\\\khấu trừ cho chủ nhà; hợp đồng “Đã kết thúc”", WM),
    ("b3", "act", 1, M, 9.1, "Backend đồng bộ LeaseEnded: phòng về\\\\“Trống”, ghi khoản khấu trừ vào thu chi", WM),
    ("mf", "mrg", 1, 0, 10.3, "", None),
    ("e", "en", 1, 0, 11.2, "", None),
], [
    ("s", "a1"), ("a1", "d1", None, "-|"), ("d1", "ax", "Không", "-|"), ("d1", "a2", "Có", "-|"), ("a2", "b1", None, "-|"),
    ("b1", "d2"), ("d2", "b2", "Có"), ("d2", "ay", "Không"), ("b2", "b3"),
    ("b3", "mf", None, "|-"), ("ay", "mf", None, "|-"),
    ("ax", "mf", None, "RAW:\\draw[arr] (ax.east) -- ++(" + str(BY) + ",0) |- (mf.east);"), ("mf", "e"),
])

# 10. Theo dõi tổng quan, công nợ và thu chi
build("hd-10-tong-quan-thu-chi", [LL, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Mở trang “Tổng quan”", 4.0),
    ("b1", "act", 1, M, 1, "Đếm phòng đã thuê / trống / chờ ký,\\\\tính tỷ lệ lấp đầy", WM),
    ("b2", "act", 1, M, 2.3, "Công nợ = phần còn lại của hoá đơn đã xuất\\\\+ tiền phòng quá hạn đọc từ smart contract", WM),
    ("b3", "act", 1, M, 3.6, "Doanh thu 6 tháng: tiền phòng, dịch vụ, khấu\\\\trừ cọc + phiếu thu tay − khoản chi", WM),
    ("b4", "act", 1, M, 4.9, "Hiển thị thẻ thống kê, biểu đồ cột,\\\\danh sách “Cần nhắc thu”", WM),
    ("d1", "dec", 0, 0, 6.2, "Có khoản\\\\chi mới?", 1.3),
    ("a2", "act", 0, 0, 7.6, "Vào “Thu chi”, ghi khoản chi", 4.4),
    ("b5", "act", 1, M, 8.8, "Lưu sổ thu chi, cập nhật tổng thu,\\\\tổng chi và số còn lại của tháng", WM),
    ("mf", "mrg", 1, 0, 10.0, "", None),
    ("e", "en", 1, 0, 10.9, "", None),
], [
    ("s", "a1"), ("a1", "b1"), ("b1", "b2"), ("b2", "b3"), ("b3", "b4"), ("b4", "d1", None, "-|"),
    ("d1", "a2", "Có"), ("a2", "b5", None, "-|"), ("b5", "mf", None, "|-"),
    ("d1", "mf", "Không", "RAW:\\draw[arr] (d1.west) -- node[lbl,pos=0.3,above]{[Không]} ++(-1.6,0) |- (mf.west);"), ("mf", "e"),
])

# 11. Rút tiền về MetaMask
build("hd-11-rut-tien", [USR, SYS], [
    ("s", "st", 0, 0, 0, "", None),
    ("a1", "act", 0, 0, 1, "Bấm vào số dư, nhập số ETH\\\\cần rút", 4.0),
    ("b1", "act", 1, M, 2, "Tạo giao dịch withdraw(amount),\\\\gửi tới MetaMask", WM),
    ("a2", "act", 0, 0, 3.2, "Xác nhận giao dịch\\\\trên MetaMask", 4.0),
    ("b2", "act", 1, M, 4.4, "Smart contract kiểm tra số tiền lớn hơn 0\\\\và số dư trong contract", WM),
    ("d1", "dec", 1, M, 5.7, "Số dư\\\\đủ?", 1.3),
    ("ax", "act", 1, R, 7.0, "Hiển thị lỗi\\\\“Số dư không đủ”", WR),
    ("c0", "act", 1, M, 7.0, "Trừ số dư trước,\\\\ghi lịch sử “Rút về ví”", WM),
    ("c1", "act", 1, M, 8.2, "Chuyển ETH về ví MetaMask,\\\\phát sự kiện Withdrawn", WM),
    ("c2", "act", 1, M, 9.4, "Cập nhật số dư trong contract\\\\và ví MetaMask", WM),
    ("mf", "mrg", 1, 0, 10.6, "", None),
    ("e", "en", 1, 0, 11.5, "", None),
], [
    ("s", "a1"), ("a1", "b1", None, "-|"), ("b1", "a2", None, "-|"), ("a2", "b2", None, "-|"), ("b2", "d1"),
    ("d1", "ax", "Không", "-|"), ("d1", "c0", "Có"), ("c0", "c1"), ("c1", "c2"),
    ("c2", "mf", None, "|-"), ("ax", "mf", None, "|-"), ("mf", "e"),
])
print("done")
