"""Sinh biểu đồ use case tổng quát (TikZ) theo kiểu báo cáo mẫu: 2 tác nhân hai bên,
các use case xếp giữa, mũi tên từ tác nhân tới use case, không vẽ khung hệ thống.
Quyền của từng tác nhân lấy theo require(msg.sender ...) của RentalManager.sol và API backend.
Chạy: python gen_usecase.py -> bieu-do-use-case-tong-quat.tex, rồi biên dịch bằng ../build.sh"""
import pathlib

HERE = pathlib.Path(__file__).parent

# (nhãn, ai dùng: L = chủ nhà, T = người thuê)
UC = [
    ("Quản lý phòng,\\\\thiết bị và khách thuê", "L"),
    ("Duyệt yêu cầu thuê,\\\\tạo hợp đồng thuê", "L"),
    ("Ghi chỉ số điện nước,\\\\xuất hoá đơn tháng", "L"),
    ("Kết thúc hợp đồng,\\\\quyết toán tiền cọc", "L"),
    ("Theo dõi tổng quan,\\\\công nợ, thu chi", "L"),
    ("Đăng nhập Google,\\\\liên kết ví MetaMask", "LT"),
    ("Gia hạn hợp đồng", "LT"),
    ("Rút tiền về MetaMask,\\\\xem lịch sử giao dịch", "LT"),
    ("Tìm phòng,\\\\gửi yêu cầu thuê", "T"),
    ("Ký hợp đồng\\\\và đặt cọc", "T"),
    ("Trả tiền phòng,\\\\thanh toán hoá đơn", "T"),
    ("Chấm dứt sớm,\\\\nhận lại tiền cọc", "T"),
]

DY = 1.5      # khoảng cách dọc giữa các use case (cm)
XA = 6.2      # khoảng cách từ trục giữa tới mỗi tác nhân

PRE = r"""\documentclass[11pt,border=8pt]{standalone}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shapes.geometric}
\tikzset{
  uc/.style={ellipse,draw,thick,fill=white,align=center,font=\small,minimum width=4.6cm,minimum height=1.2cm,inner sep=1pt},
  arr/.style={thick,-{Stealth[length=2.6mm]}},
  actor/.pic={   % gốc ở bàn chân; tay ở độ cao 1.0
    \draw[thick,fill=white] (0,1.45) circle (0.25);
    \draw[thick] (0,1.2) -- (0,0.55) (-0.42,1.0) -- (0.42,1.0) (0,0.55) -- (-0.32,0) (0,0.55) -- (0.32,0);
  },
}
\begin{document}
\begin{tikzpicture}
"""

BS = "\\"


def main():
    out = [PRE]
    for i, (label, _) in enumerate(UC):
        out.append(f"{BS}node[uc] (u{i}) at (0,{-i * DY}) {{{label}}};\n")

    y_mid = -(len(UC) - 1) * DY / 2          # độ cao tay của tác nhân
    for x, name in ((-XA, "Chủ nhà"), (XA, "Người thuê")):
        out.append(f"{BS}pic at ({x},{y_mid - 1.0}) {{actor}};\n")
        out.append(f"{BS}node[font={BS}small,anchor=north] at ({x},{y_mid - 1.05}) {{{name}}};\n")

    for i, (_, who) in enumerate(UC):
        if "L" in who:
            out.append(f"{BS}draw[arr] ({-XA + 0.45},{y_mid}) -- (u{i}.west);\n")
        if "T" in who:
            out.append(f"{BS}draw[arr] ({XA - 0.45},{y_mid}) -- (u{i}.east);\n")

    out.append(f"{BS}end{{tikzpicture}}\n{BS}end{{document}}\n")
    (HERE / "bieu-do-use-case-tong-quat.tex").write_text("".join(out), encoding="utf8")
    print("ok")


if __name__ == "__main__":
    main()
