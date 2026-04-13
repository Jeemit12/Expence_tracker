import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, csv
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── COLORS & FONT ────────────────────────────────────────────────
BG    = "#1a1a2e"; PANEL = "#16213e"; ENTRY = "#0f3460"
GREEN = "#22C55E"; BLUE  = "#3B82F6"; RED   = "#EF4444"
GOLD  = "#F59E0B"; WHITE = "#F1F5F9"; GRAY  = "#94A3B8"
FONT  = "Segoe UI"
CATS  = ["Food","Travel","Shopping","Bills","Health","Education","Other"]
CLRS  = [GREEN, BLUE, GOLD, RED, "#A78BFA", "#F472B6", "#34D399"]

# ── DATABASE ─────────────────────────────────────────────────────
db = sqlite3.connect("expenses.db")
c  = db.cursor()
c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT);
    CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, amount REAL, category TEXT, date TEXT, description TEXT);
    CREATE TABLE IF NOT EXISTS budget(user_id INTEGER PRIMARY KEY, amount REAL);
"""); db.commit()

# ── HELPERS ──────────────────────────────────────────────────────
def btn(p, text, cmd, bg=GREEN, fg="white", w=0):
    b = tk.Button(p, text=text, command=cmd, bg=bg, fg=fg,
                  font=(FONT,9,"bold"), relief="flat", cursor="hand2", padx=10, pady=6, width=w)
    hov = {GREEN:"#16A34A",BLUE:"#2563EB",RED:"#DC2626",PANEL:"#1e2d50",GOLD:"#D97706"}
    b.bind("<Enter>", lambda e: b.config(bg=hov.get(bg,bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def lbl(p, text, size=9, fg=GRAY, bold=False):
    return tk.Label(p, text=text, bg=p.cget("bg"), fg=fg,
                    font=(FONT, size, "bold" if bold else "normal"))

def ent(p, show=""):
    return tk.Entry(p, bg=ENTRY, fg=WHITE, insertbackground=WHITE,
                    font=(FONT,10), relief="flat", bd=8, show=show)

def sep(p): tk.Frame(p, bg="#334155", height=1).pack(fill="x", pady=8)

def q(sql, params=()): c.execute(sql, params); return c.fetchall()

# ── APP ──────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.configure(bg=BG)
        self.uid = None
        s = ttk.Style(); s.theme_use("clam")
        s.configure("Treeview", background=PANEL, foreground=WHITE,
                    fieldbackground=PANEL, rowheight=28, font=(FONT,9))
        s.configure("Treeview.Heading", background=BG, foreground=GRAY, font=(FONT,8,"bold"))
        s.map("Treeview", background=[("selected", BLUE)])
        s.configure("TCombobox", fieldbackground=ENTRY, background=ENTRY, foreground=WHITE)
        s.map("TCombobox", fieldbackground=[("readonly", ENTRY)])
        self.login_screen()

    def clr(self):
        for w in self.root.winfo_children(): w.destroy()

    # ════════ LOGIN ══════════════════════════════════════════════
    def login_screen(self):
        self.clr(); self.root.geometry("360x460")
        tk.Label(self.root, text="💰", bg=BG, font=(FONT,34)).pack(pady=(36,4))
        lbl(self.root,"Expense Tracker",18,WHITE,True).pack()
        lbl(self.root,"Track. Save. Grow.",9).pack(pady=(2,18))
        frm = tk.Frame(self.root, bg=PANEL, padx=26, pady=22); frm.pack(padx=28, fill="x")
        row = tk.Frame(frm, bg=PANEL); row.pack(fill="x", pady=(0,14))
        self.tl = tk.Button(row, text="Login", bg=GREEN, fg="white", font=(FONT,9,"bold"),
                            relief="flat", padx=14, pady=5, cursor="hand2",
                            command=lambda: self._tab("in"))
        self.tl.pack(side="left")
        self.tr = tk.Button(row, text="Register", bg=PANEL, fg=GRAY, font=(FONT,9),
                            relief="flat", padx=14, pady=5, cursor="hand2",
                            command=lambda: self._tab("reg"))
        self.tr.pack(side="left", padx=(6,0))
        self.form = tk.Frame(frm, bg=PANEL); self.form.pack(fill="x")
        self._tab("in")

    def _tab(self, t):
        for w in self.form.winfo_children(): w.destroy()
        self.tl.config(bg=GREEN if t=="in" else PANEL, fg="white" if t=="in" else GRAY)
        self.tr.config(bg=GREEN if t=="reg" else PANEL, fg="white" if t=="reg" else GRAY)
        lbl(self.form,"USERNAME",8,GRAY,True).pack(anchor="w",pady=(0,2))
        self.ue = ent(self.form); self.ue.pack(fill="x", pady=(0,10))
        lbl(self.form,"PASSWORD",8,GRAY,True).pack(anchor="w",pady=(0,2))
        self.pe = ent(self.form, show="*"); self.pe.pack(fill="x", pady=(0,16))
        if t == "in": btn(self.form,"  Login →",self.do_login).pack(fill="x")
        else:         btn(self.form,"  Create Account",self.do_register).pack(fill="x")

    def do_login(self):
        u,p = self.ue.get().strip(), self.pe.get().strip()
        r = q("SELECT id FROM users WHERE username=? AND password=?", (u,p))
        if r: self.uid = r[0][0]; self.uname = u; self.main_screen()
        else: messagebox.showerror("Error","Wrong username or password.")

    def do_register(self):
        u,p = self.ue.get().strip(), self.pe.get().strip()
        if len(u)<3 or len(p)<4:
            messagebox.showerror("Error","Username ≥ 3 chars, Password ≥ 4 chars."); return
        try:
            c.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p)); db.commit()
            messagebox.showinfo("Done","Account created! Please login."); self._tab("in")
        except sqlite3.IntegrityError: messagebox.showerror("Error","Username taken.")

    # ════════ SHELL ══════════════════════════════════════════════
    def main_screen(self):
        self.clr(); self.root.geometry("1000x650")
        side = tk.Frame(self.root, bg=PANEL, width=185)
        side.pack(side="left", fill="y"); side.pack_propagate(False)
        lbl(side,"💰 Expense",13,WHITE,True).pack(pady=(20,0),padx=14,anchor="w")
        lbl(side,"Tracker",13,GREEN,True).pack(padx=14,anchor="w")
        tk.Frame(side,bg="#334155",height=1).pack(fill="x",pady=12,padx=10)
        lbl(side,f"👤 {self.uname}",9,WHITE).pack(padx=14,anchor="w",pady=(0,12))
        self.con = tk.Frame(self.root, bg=BG); self.con.pack(side="right",fill="both",expand=True)
        nav = [("🏠  Dashboard",self.pg_dash),("➕  Add Expense",self.pg_add),
               ("📋  Expenses", self.pg_list),("📊  Analytics",  self.pg_analytics),
               ("💼  Budget",   self.pg_budget),("💾  Save to File",self.pg_save)]
        self.nbs = []
        for txt,cmd in nav:
            b = tk.Button(side,text=txt,bg=PANEL,fg=GRAY,font=(FONT,9),relief="flat",
                          anchor="w",padx=14,pady=9,cursor="hand2",
                          command=lambda c2=cmd: self._nav(c2))
            b.pack(fill="x"); self.nbs.append((b,cmd))
        tk.Frame(side,bg="#334155",height=1).pack(fill="x",pady=10,padx=10)
        btn(side,"  Logout",self.logout,bg=PANEL,fg=GRAY).pack(fill="x",padx=10,pady=4)
        self._nav(self.pg_dash)

    def _nav(self, cmd):
        for b,c2 in self.nbs:
            b.config(bg=BG if c2==cmd else PANEL,
                     fg=WHITE if c2==cmd else GRAY,
                     font=(FONT,9,"bold" if c2==cmd else "normal"))
        for w in self.con.winfo_children(): w.destroy()
        cmd()

    def hdr(self, title, sub=""):
        h = tk.Frame(self.con, bg=BG); h.pack(fill="x",padx=26,pady=(20,0))
        lbl(h,title,15,WHITE,True).pack(anchor="w")
        if sub: lbl(h,sub).pack(anchor="w",pady=(2,0))
        tk.Frame(self.con,bg="#334155",height=1).pack(fill="x",padx=26,pady=10)

    # ════════ DASHBOARD ══════════════════════════════════════════
    def pg_dash(self):
        self.hdr("Dashboard", f"Welcome {self.uname}  ·  {date.today().strftime('%B %d, %Y')}")
        total  = q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=?",(self.uid,))[0][0]
        mon    = q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=strftime('%Y-%m','now')",(self.uid,))[0][0]
        br     = q("SELECT amount FROM budget WHERE user_id=?",(self.uid,))
        budget = br[0][0] if br else 0
        rem    = max(budget-mon,0); cnt = q("SELECT COUNT(*) FROM expenses WHERE user_id=?",(self.uid,))[0][0]
        pct    = int(mon/budget*100) if budget else 0

        row = tk.Frame(self.con,bg=BG); row.pack(fill="x",padx=20,pady=(0,10))
        for title,val,color,sub in [("Total Spent",f"₹{total:,.0f}",WHITE,f"{cnt} records"),
                                     ("This Month", f"₹{mon:,.0f}",  GREEN, date.today().strftime("%B")),
                                     ("Budget Left",f"₹{rem:,.0f}",  GREEN if rem>0 else RED,"remaining"),
                                     ("Budget Set", f"₹{budget:,.0f}",GOLD,"per month")]:
            cf = tk.Frame(row,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
            cf.pack(side="left",fill="both",expand=True,padx=4,pady=2)
            lbl(cf,title,8).pack(anchor="w",padx=12,pady=(10,0))
            lbl(cf,val,17,color,True).pack(anchor="w",padx=12)
            lbl(cf,sub).pack(anchor="w",padx=12,pady=(0,8))

        if budget:
            bf = tk.Frame(self.con,bg=BG); bf.pack(fill="x",padx=28,pady=(0,10))
            lbl(bf,f"BUDGET USAGE  {pct}%",7,GRAY,True).pack(anchor="w")
            tr = tk.Frame(bf,bg="#334155",height=7); tr.pack(fill="x",pady=3)
            tr.update_idletasks(); w = tr.winfo_width() or 700
            clr = GREEN if pct<80 else (GOLD if pct<100 else RED)
            tk.Frame(tr,bg=clr,height=7,width=int(pct/100*w)).place(x=0,y=0)

        lbl(self.con,"RECENT TRANSACTIONS",7,GRAY,True).pack(anchor="w",padx=28,pady=(4,4))
        tc = tk.Frame(self.con,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        tc.pack(fill="both",expand=True,padx=26,pady=(0,18))
        self._tree(tc, limit=8)

    # ════════ ADD EXPENSE ════════════════════════════════════════
    def pg_add(self):
        self.hdr("Add Expense","Record a new expense")
        frm = tk.Frame(self.con,bg=PANEL,padx=26,pady=24); frm.pack(padx=28,anchor="w")
        lbl(frm,"AMOUNT (₹)",8,GRAY,True).grid(row=0,column=0,sticky="w",pady=(0,2))
        self.ae = ent(frm); self.ae.grid(row=1,column=0,pady=(0,12),ipadx=50)
        lbl(frm,"CATEGORY",8,GRAY,True).grid(row=0,column=1,sticky="w",padx=(18,0),pady=(0,2))
        self.cv = tk.StringVar(value=CATS[0])
        ttk.Combobox(frm,textvariable=self.cv,values=CATS,state="readonly",
                     font=(FONT,9),width=16).grid(row=1,column=1,padx=(18,0),pady=(0,12))
        lbl(frm,"DATE",8,GRAY,True).grid(row=2,column=0,sticky="w",pady=(0,2))
        self.de = ent(frm); self.de.grid(row=3,column=0,pady=(0,12),ipadx=50)
        self.de.insert(0,str(date.today()))
        lbl(frm,"DESCRIPTION",8,GRAY,True).grid(row=2,column=1,sticky="w",padx=(18,0),pady=(0,2))
        self.dse = ent(frm); self.dse.grid(row=3,column=1,padx=(18,0),pady=(0,12),ipadx=50)
        btn(frm,"  Submit Expense",self.do_add).grid(row=4,column=0,pady=(6,0),sticky="w")

    def do_add(self):
        try:
            amt = float(self.ae.get().replace(",","")); assert amt > 0
        except: messagebox.showerror("Error","Enter a valid positive amount."); return
        c.execute("INSERT INTO expenses(user_id,amount,category,date,description) VALUES(?,?,?,?,?)",
                  (self.uid,amt,self.cv.get(),self.de.get().strip() or str(date.today()),self.dse.get().strip()))
        db.commit(); self._budget_alert()
        messagebox.showinfo("Added",f"₹{amt:,.2f} under '{self.cv.get()}' saved.")
        self._nav(self.pg_dash)

    # ════════ EXPENSE LIST ═══════════════════════════════════════
    def pg_list(self):
        self.hdr("My Expenses","View, edit or delete expenses")
        tb = tk.Frame(self.con,bg=BG); tb.pack(fill="x",padx=26,pady=(0,6))
        lbl(tb,"Filter:",9,GRAY).pack(side="left")
        self.fv = tk.StringVar(value="All")
        ttk.Combobox(tb,textvariable=self.fv,values=["All"]+CATS,
                     state="readonly",font=(FONT,9),width=12).pack(side="left",padx=6)
        btn(tb,"Apply",self._reload_list,bg=BLUE,w=6).pack(side="left")
        self.lcard = tk.Frame(self.con,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        self.lcard.pack(fill="both",expand=True,padx=26,pady=(0,6))
        self._reload_list()
        act = tk.Frame(self.con,bg=BG); act.pack(fill="x",padx=26,pady=(2,14))
        lbl(act,"Select a row:").pack(side="left")
        btn(act,"✏ Edit",  self.do_edit,  bg=BLUE).pack(side="left",padx=(10,6))
        btn(act,"🗑 Delete",self.do_delete,bg=RED ).pack(side="left")

    def _reload_list(self):
        for w in self.lcard.winfo_children(): w.destroy()
        cat = self.fv.get() if hasattr(self,"fv") else "All"
        sql = "SELECT id,date,category,amount,description FROM expenses WHERE user_id=?"
        p   = [self.uid]
        if cat != "All": sql += " AND category=?"; p.append(cat)
        self._tree(self.lcard, query=sql+" ORDER BY date DESC", params=p)

    def _tree(self, parent, limit=None, query=None, params=None):
        cols = ("ID","Date","Category","Amount","Description")
        tv = ttk.Treeview(parent,columns=cols,show="headings",selectmode="browse")
        sb = ttk.Scrollbar(parent,orient="vertical",command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        for col,w in zip(cols,(0,100,140,100,260)):
            tv.heading(col,text="" if col=="ID" else col)
            tv.column(col,width=w,stretch=(col=="Description"),anchor="e" if col=="Amount" else "w")
        if not query:
            query  = "SELECT id,date,category,amount,description FROM expenses WHERE user_id=? ORDER BY date DESC"
            params = [self.uid]
        if limit: query += f" LIMIT {limit}"
        c.execute(query,params)
        for i,(eid,dt,cat,amt,desc) in enumerate(c.fetchall()):
            tv.insert("","end",iid=str(eid),values=(eid,dt,cat,f"₹{amt:,.2f}",desc or "—"),
                      tags=("e" if i%2 else "o",))
        tv.tag_configure("o",background=PANEL)
        tv.tag_configure("e",background="#1a2744")
        tv.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        self.tree = tv

    def do_edit(self):
        if not self.tree.selection(): messagebox.showinfo("Info","Select a row first."); return
        eid = int(self.tree.selection()[0])
        row = q("SELECT amount,category,date,description FROM expenses WHERE id=?",(eid,))
        if not row: return
        amt,cat,dt,desc = row[0]
        win = tk.Toplevel(self.root); win.title("Edit Expense")
        win.configure(bg=PANEL); win.resizable(False,False); win.grab_set(); win.geometry("320x260")
        f = tk.Frame(win,bg=PANEL,padx=22,pady=18); f.pack(fill="both")
        lbl(f,"Edit Expense",11,WHITE,True).pack(anchor="w",pady=(0,10))
        lbl(f,"AMOUNT",8,GRAY,True).pack(anchor="w",pady=(0,2))
        ae2=ent(f); ae2.pack(fill="x",pady=(0,8)); ae2.insert(0,str(amt))
        lbl(f,"CATEGORY",8,GRAY,True).pack(anchor="w",pady=(0,2))
        cv2=tk.StringVar(value=cat)
        ttk.Combobox(f,textvariable=cv2,values=CATS,state="readonly",font=(FONT,9)).pack(fill="x",pady=(0,8))
        lbl(f,"DESCRIPTION",8,GRAY,True).pack(anchor="w",pady=(0,2))
        de2=ent(f); de2.pack(fill="x",pady=(0,14))
        if desc: de2.insert(0,desc)
        def save():
            try: a=float(ae2.get())
            except ValueError: messagebox.showerror("Error","Invalid amount.",parent=win); return
            c.execute("UPDATE expenses SET amount=?,category=?,description=? WHERE id=?",
                      (a,cv2.get(),de2.get().strip(),eid)); db.commit()
            win.destroy(); self._reload_list(); messagebox.showinfo("Updated","Expense updated.")
        btn(f,"Save Changes",save).pack(anchor="w")

    def do_delete(self):
        if not self.tree.selection(): messagebox.showinfo("Info","Select a row first."); return
        eid = int(self.tree.selection()[0])
        if messagebox.askyesno("Confirm","Delete this expense?"):
            c.execute("DELETE FROM expenses WHERE id=?",(eid,)); db.commit()
            self._reload_list(); messagebox.showinfo("Deleted","Expense removed.")

    # ════════ ANALYTICS — pie chart ══════════════════════════════
    def pg_analytics(self):
        self.hdr("Analytics","Spending breakdown by category")
        rows = q("SELECT category,SUM(amount) FROM expenses WHERE user_id=? GROUP BY category ORDER BY 2 DESC",(self.uid,))
        if not rows:
            lbl(self.con,"No data yet. Add some expenses!",12,GRAY).pack(expand=True,pady=40); return

        total  = sum(a for _,a in rows)
        labels = [r[0] for r in rows]
        sizes  = [r[1] for r in rows]

        body = tk.Frame(self.con,bg=BG); body.pack(fill="both",expand=True,padx=26)

        # Pie chart (matplotlib embedded)
        fig, ax = plt.subplots(figsize=(4.5,4), facecolor="#1a1a2e")
        ax.set_facecolor("#16213e")
        wedges,_,autos = ax.pie(sizes, labels=None, autopct="%1.1f%%", startangle=90,
            colors=CLRS[:len(rows)],
            wedgeprops=dict(width=0.55, edgecolor="#1a1a2e", linewidth=2),
            pctdistance=0.78)
        for t in autos: t.set(color=WHITE, fontsize=8, fontweight="bold")
        ax.legend(labels, loc="lower center", bbox_to_anchor=(0.5,-0.12),
                  ncol=2, fontsize=7.5, framealpha=0, labelcolor=GRAY)
        ax.set_title("Category Split", color=WHITE, fontsize=11, fontweight="bold", pad=10)
        plt.tight_layout(pad=1.5)
        cf = tk.Frame(body,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        cf.pack(side="left",fill="both",expand=True,padx=(0,8),pady=(0,16))
        FigureCanvasTkAgg(fig,master=cf).get_tk_widget().pack(fill="both",expand=True,padx=4,pady=4)
        plt.close(fig)

        # Summary table
        sf = tk.Frame(body,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        sf.pack(side="left",fill="y",pady=(0,16))
        si = tk.Frame(sf,bg=PANEL,padx=20,pady=20); si.pack()
        lbl(si,"SUMMARY",9,WHITE,True).pack(anchor="w",pady=(0,10))
        for (cat,amt),clr in zip(rows,CLRS):
            r = tk.Frame(si,bg=PANEL); r.pack(fill="x",pady=3)
            tk.Frame(r,bg=clr,width=10,height=10).pack(side="left",padx=(0,6))
            lbl(r,cat,9,GRAY).pack(side="left")
            lbl(r,f"₹{amt:,.0f}",9,WHITE,True).pack(side="right",padx=(16,0))
        sep(si)
        r = tk.Frame(si,bg=PANEL); r.pack(fill="x")
        lbl(r,"TOTAL",9,WHITE,True).pack(side="left")
        lbl(r,f"₹{total:,.0f}",9,GREEN,True).pack(side="right")

    # ════════ BUDGET ═════════════════════════════════════════════
    def pg_budget(self):
        self.hdr("Budget","Set your monthly spending limit")
        br     = q("SELECT amount FROM budget WHERE user_id=?",(self.uid,))
        budget = br[0][0] if br else 0
        spent  = q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=strftime('%Y-%m','now')",(self.uid,))[0][0]
        rem    = max(budget-spent,0); pct = int(spent/budget*100) if budget else 0
        body   = tk.Frame(self.con,bg=BG); body.pack(fill="both",expand=True,padx=26)

        lf = tk.Frame(body,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        lf.pack(side="left",fill="y",padx=(0,10),pady=(0,18))
        li = tk.Frame(lf,bg=PANEL,padx=22,pady=22); li.pack()
        lbl(li,"SET BUDGET",9,WHITE,True).pack(anchor="w",pady=(0,10))
        lbl(li,"AMOUNT (₹)",8,GRAY,True).pack(anchor="w",pady=(0,2))
        self.be = ent(li); self.be.pack(fill="x",pady=(0,14))
        self.be.insert(0,str(int(budget)) if budget else "")
        btn(li,"  Save Budget",self.save_budget).pack(anchor="w")
        if budget:
            sep(li); clr = GREEN if pct<80 else (GOLD if pct<100 else RED)
            for lt,val,fg in [("Budget",f"₹{budget:,.0f}",GRAY),("Spent",f"₹{spent:,.0f}",clr),
                               ("Remaining",f"₹{rem:,.0f}",GREEN),("Used",f"{pct}%",clr)]:
                r = tk.Frame(li,bg=PANEL); r.pack(fill="x",pady=2)
                lbl(r,lt,9,GRAY).pack(side="left"); lbl(r,val,9,fg,True).pack(side="right")
            sep(li)
            tr = tk.Frame(li,bg="#334155",height=8,width=200); tr.pack(anchor="w",pady=2)
            if pct>0: tk.Frame(tr,bg=clr,height=8,width=int(pct/100*200)).place(x=0,y=0)

        rf = tk.Frame(body,bg=PANEL,highlightbackground="#334155",highlightthickness=1)
        rf.pack(side="left",fill="both",expand=True,pady=(0,18))
        ri = tk.Frame(rf,bg=PANEL,padx=22,pady=22); ri.pack(fill="both")
        lbl(ri,"THIS MONTH BY CATEGORY",9,WHITE,True).pack(anchor="w",pady=(0,10))
        cats = q("SELECT category,SUM(amount) FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=strftime('%Y-%m','now') GROUP BY category ORDER BY 2 DESC",(self.uid,))
        if cats:
            for cat,amt in cats:
                r = tk.Frame(ri,bg=PANEL); r.pack(fill="x",pady=3)
                lbl(r,cat,9,GRAY).pack(side="left"); lbl(r,f"₹{amt:,.0f}",9,GREEN,True).pack(side="right")
        else: lbl(ri,"No expenses this month.",9,GRAY).pack(pady=16)

    # ════════ SAVE TO FILE ═══════════════════════════════════════
    def pg_save(self):
        self.hdr("Save to File","Export your expenses as CSV or TXT")
        cnt = q("SELECT COUNT(*) FROM expenses WHERE user_id=?",(self.uid,))[0][0]
        frm = tk.Frame(self.con,bg=PANEL,padx=28,pady=28); frm.pack(padx=28,pady=8,anchor="w")
        lbl(frm,f"You have {cnt} expense record(s) saved.",10,WHITE,True).pack(anchor="w",pady=(0,20))
        for title,sub,clr,cmd in [
            ("Save as CSV","Spreadsheet format — open in Excel / Google Sheets",BLUE, self.save_csv),
            ("Save as TXT","Formatted plain-text report — easy to read & share", GREEN,self.save_txt)]:
            ef = tk.Frame(frm,bg=ENTRY,highlightbackground="#334155",highlightthickness=1)
            ef.pack(fill="x",pady=5)
            row = tk.Frame(ef,bg=ENTRY); row.pack(fill="x",padx=14,pady=10)
            lbl(row,title,10,WHITE,True).pack(anchor="w")
            lbl(row,sub,8).pack(anchor="w",pady=(2,6))
            btn(row,"⬇  Export",cmd,bg=clr).pack(anchor="w")

    def save_csv(self):
        if self._no_data(): return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
               filetypes=[("CSV","*.csv")], initialfile=f"expenses_{date.today()}.csv")
        if not path: return
        rows = q("SELECT date,category,amount,description FROM expenses WHERE user_id=? ORDER BY date DESC",(self.uid,))
        with open(path,"w",newline="",encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Date","Category","Amount","Description"])
            w.writerows(rows)
        messagebox.showinfo("Saved",f"CSV saved:\n{path}")

    def save_txt(self):
        if self._no_data(): return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
               filetypes=[("Text","*.txt")], initialfile=f"expenses_{date.today()}.txt")
        if not path: return
        rows   = q("SELECT date,category,amount,description FROM expenses WHERE user_id=? ORDER BY date DESC",(self.uid,))
        total  = q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=?",(self.uid,))[0][0]
        br     = q("SELECT amount FROM budget WHERE user_id=?",(self.uid,))
        budget = br[0][0] if br else 0
        lines  = ["="*58,"  EXPENSE REPORT  —  "+self.uname,
                  f"  Date: {date.today().strftime('%B %d, %Y')}","="*58,"",
                  f"  Total Spent : Rs {total:,.2f}",
                  f"  Budget Set  : Rs {budget:,.2f}",
                  f"  Remaining   : Rs {max(budget-total,0):,.2f}","",
                  "-"*58,f"{'Date':<13}{'Category':<16}{'Amount':>10}  Description","-"*58]
        for dt,cat,amt,desc in rows:
            lines.append(f"{dt:<13}{cat:<16}Rs{amt:>8,.2f}  {desc or ''}")
        lines += ["","-"*58,f"  TOTAL: Rs {total:,.2f}","="*58]
        with open(path,"w",encoding="utf-8") as f: f.write("\n".join(lines))
        messagebox.showinfo("Saved",f"Report saved:\n{path}")

    def _no_data(self):
        if q("SELECT COUNT(*) FROM expenses WHERE user_id=?",(self.uid,))[0][0]==0:
            messagebox.showinfo("No Data","No expenses to export yet."); return True
        return False

    # ════════ SHARED ACTIONS ═════════════════════════════════════
    def save_budget(self):
        try:
            amt = float(self.be.get().replace(",","").replace("₹","").strip()); assert amt >= 0
        except: messagebox.showerror("Error","Enter a valid amount."); return
        c.execute("INSERT OR REPLACE INTO budget(user_id,amount) VALUES(?,?)",(self.uid,amt))
        db.commit(); messagebox.showinfo("Saved",f"Budget set to ₹{amt:,.0f}/month.")
        self._nav(self.pg_budget)

    def _budget_alert(self):
        spent = q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=?",(self.uid,))[0][0]
        br    = q("SELECT amount FROM budget WHERE user_id=?",(self.uid,))
        if not br: return
        pct = spent / br[0][0] * 100 if br[0][0] else 0
        if   pct >= 100: messagebox.showwarning("Over Budget!","You've exceeded your budget!")
        elif pct >=  80: messagebox.showinfo("Budget Alert",f"Used {pct:.0f}% of your budget.")

    def logout(self):
        if messagebox.askyesno("Logout","Are you sure?"):
            self.uid = None; self.login_screen()

# ── RUN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()