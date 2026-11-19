"""Sinh biểu đồ lớp tổng quát (TikZ) từ bảng MySQL và struct của smart contract RentalManager,
theo mẫu 3 ngăn (tên lớp / thuộc tính / phương thức), bội số dạng 1, 0..n, 0..1.
Chạy: python gen_class.py -> bieu-do-lop-tong-quat.tex"""
import pathlib

HERE = pathlib.Path(__file__).parent
GAP = 1.0    # cm: khoảng cách dọc giữa 2 lớp cùng cột (đủ chỗ ghi bội số)
X = [0.0, 7.6, 15.2, 22.8]   # tâm các cột

# mỗi lớp: (thuộc tính, phương thức); phương thức lấy theo API backend / hàm của smart contract
CLS = {
    "User": (["id: Integer", "googleId: String", "email: String", "name: String", "nickname: String",
              "walletAddress: String", "createdAt: DateTime"],
             ["loginWithGoogle(): Session", "setNickname(): User", "linkWallet(): User", "logout(): void"]),
    "Session": (["token: String", "userId: Integer", "expiresAt: Long"],
                ["create(): String", "revoke(): void"]),
    "CashEntry": (["id: Integer", "ownerId: Integer", "entryDate: Date", "type: Thu|Chi", "category: String",
                   "amountWei: Decimal", "note: String"],
                  ["getCashflow(month): List", "addEntry(): void"]),
    "RoomRequest": (["id: Integer", "roomId: Integer", "userId: Integer", "message: String",
                     "status: RequestStatus", "createdAt: DateTime"],
                    ["send(roomId, message): void", "reject(): void", "withdraw(): void"]),
    "Room": (["id: Integer", "ownerId: Integer", "code: String", "name: String", "floor: Integer",
              "area: Decimal", "priceWei: Decimal", "depositWei: Decimal", "leaseId: Integer"],
             ["listRooms(): List<Room>", "create(): Room", "update(): Room", "linkLease(leaseId): void",
              "status(): Trống|Chờ ký|Đã thuê"]),
    "Equipment": (["id: Integer", "roomId: Integer", "name: String", "state: Tốt|Cần sửa|Hỏng", "note: String"],
                  ["add(): void", "updateState(): void"]),
    "Tenant": (["id: Integer", "code: String", "fullName: String", "idNumber: String", "phone: String",
                "email: String", "hometown: String", "roomId: Integer", "walletAddress: String", "peopleCount: Integer"],
               ["create(): Tenant", "update(): Tenant", "delete(): void"]),
    "Lease": (["leaseId: Uint256", "landlord: Address", "tenant: Address", "rent: Uint256", "deposit: Uint256",
               "periodLength: Uint64", "totalPeriods: Uint32", "paidPeriods: Uint32", "startDate: Uint64",
               "status: Status", "extensionPeriods: Uint32", "depositDeducted: Uint256"],
              ["createLease(): Uint256", "signLease(id): void", "payRent(id, n): void", "proposeExtension(id, n): void",
               "acceptExtension(id): void", "endLease(id, deduction, note): void", "terminateEarly(id): void",
               "claimDeposit(id): void"]),
    "Bill": (["billId: Uint256", "leaseId: Uint256", "rentPeriods: Uint32", "rentAmount: Uint256", "amount: Uint256",
              "memo: String", "paid: Bool", "cancelled: Bool"],
             ["issueBill(id, kỳ, dịch vụ, memo): Uint256", "payBill(billId): void", "cancelBill(billId): void"]),
    "Service": (["id: Integer", "name: String", "unit: String", "unitPriceWei: Decimal", "kind: Metered|Fixed"],
                ["listServices(): List", "update(): void"]),
    "ServiceUsage": (["id: Integer", "roomId: Integer", "serviceId: Integer", "month: String", "oldIndex: Integer",
                      "newIndex: Integer"],
                     ["saveUsage(): void", "usage(): Integer"]),
    "Invoice": (["id: Integer", "roomId: Integer", "leaseId: Integer", "month: String", "rentWei: Decimal",
                 "serviceTotalWei: Decimal", "totalWei: Decimal", "billId: Integer"],
                ["generate(month): List<Invoice>", "linkBill(billId): void", "status(): InvoiceStatus"]),
    "Payment": (["id: Integer", "invoiceId: Integer", "paidAt: DateTime", "amountWei: Decimal",
                 "method: Blockchain|Tiền mặt|Chuyển khoản", "txHash: String"],
                ["recordFromChain(): void", "addManual(): void"]),
}

# cột 1: tài khoản | cột 2: phòng | cột 3: hợp đồng & hoá đơn trên smart contract | cột 4: dịch vụ, hoá đơn (MySQL)
COLS = [["User", "Session", "CashEntry"], ["RoomRequest", "Room", "Equipment"], ["Tenant", "Lease", "Bill"],
        ["Service", "ServiceUsage", "Invoice", "Payment"]]

PRE = r"""\documentclass[border=8pt]{standalone}
\usepackage{fontspec}
\setmainfont{TeX Gyre Heros}
\usepackage{tikz}
\usetikzlibrary{shapes.multipart,calc}
\tikzset{
  cls/.style={rectangle split,rectangle split parts=3,draw,semithick,anchor=north,text width=6.1cm,font=\small,
              rectangle split part fill={white,white,white},inner sep=3pt},
  chain/.style={cls,rectangle split part fill={white,white,white}},
  as/.style={semithick},
  m/.style={font=\footnotesize,inner sep=1pt},
}
\begin{document}
\begin{tikzpicture}
"""
CHAIN = {"Lease", "Bill"}  # struct trên smart contract (tô nền tên lớp)


def esc(s):
    return s.replace("<", r"\textless{}").replace(">", r"\textgreater{}").replace("_", r"\_").replace("|", r"\textbar{}")


out = [PRE]
x = {}
for c, names in enumerate(COLS):
    prev = None
    for name in names:
        attrs, meths = CLS[name]
        rows = r"\\ ".join("- " + esc(a) for a in attrs)
        ops = r"\\ ".join("+ " + esc(o) for o in meths)
        at = f"({X[c]},0)" if prev is None else f"($({prev}.south)+(0,-{GAP})$)"
        style = "chain" if name in CHAIN else "cls"
        title = rf"\textbf{{{name}}}" + (r"\\ \footnotesize«smart contract»" if name in CHAIN else "")
        out.append(rf"\node[{style}] ({name}) at {at} {{\centering {title}"
                   rf"\nodepart{{two}}\raggedright {rows}\nodepart{{three}}\raggedright {ops}}};")
        prev = name
        x[name] = c

bus = lambda a, b: (X[a] + X[b]) / 2   # trục dọc giữa 2 cột


def link(src, dst, bx, m_src="1", m_dst="0..n"):
    """src.<cạnh hướng về bx> -- trục dọc x=bx -- dst.<cạnh hướng về bx>; bội số ghi ở 2 đầu."""
    s_side = "east" if bx > X[x[src]] else "west"
    d_side = "east" if bx > X[x[dst]] else "west"
    out.append(rf"\draw[as] ({src}.{s_side}) -| ({bx:.2f},0 |- {dst}.{d_side}) -- ({dst}.{d_side});")
    if m_dst:
        out.append(rf"\node[m,anchor=south {'east' if d_side == 'west' else 'west'}] at ($({dst}.{d_side})+({-0.08 if d_side == 'west' else 0.08},0.02)$) {{{m_dst}}};")
    if m_src:
        out.append(rf"\node[m,anchor=south {'west' if s_side == 'east' else 'east'}] at ($({src}.{s_side})+({0.08 if s_side == 'east' else -0.08},0.02)$) {{{m_src}}};")


def vertical(a, b, ma, mb):
    out.append(rf"\draw[as] ({a}.south) -- node[m,pos=0.15,right]{{{ma}}} node[m,pos=0.85,right]{{{mb}}} ({b}.north);")


vertical("User", "Session", "1", "0..n")                 # một tài khoản có nhiều phiên đăng nhập
link("User", "CashEntry", X[0] - 3.7, "1", "0..n")       # chủ nhà ghi sổ thu chi
link("User", "RoomRequest", bus(0, 1), "1", "0..n")     # khách gửi yêu cầu thuê
link("User", "Room", bus(0, 1), "", "0..n")              # chủ nhà sở hữu nhiều phòng
vertical("RoomRequest", "Room", "0..n", "1")
vertical("Room", "Equipment", "1", "0..n")               # thiết bị trong phòng
link("Room", "Tenant", bus(1, 2), "1", "0..n")           # khách đang ở phòng
link("Room", "Lease", bus(1, 2), "", "0..n")             # mỗi phòng có nhiều hợp đồng theo thời gian
vertical("Tenant", "Lease", "1", "0..n")
vertical("Lease", "Bill", "1", "0..n")                   # hoá đơn tháng phát hành trên contract
vertical("Service", "ServiceUsage", "1", "0..n")         # chỉ số theo dịch vụ
vertical("ServiceUsage", "Invoice", "0..n", "1")         # hoá đơn tính từ chỉ số tháng
vertical("Invoice", "Payment", "1", "0..n")              # phiếu thu
link("Lease", "Invoice", bus(2, 3), "1", "0..n")
link("Bill", "Invoice", bus(2, 3), "0..1", "")           # hoá đơn MySQL gắn với hoá đơn trên chain

out.append(r"\end{tikzpicture}" + "\n" + r"\end{document}" + "\n")
(HERE / "bieu-do-lop-tong-quat.tex").write_text("\n".join(out), encoding="utf-8")
print("done")
