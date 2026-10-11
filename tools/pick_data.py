"""Excel -> data/pick.json   (one-off conversion, see tools/README.md)

usage:  python3 tools/pick_data.py "<folder with the 'Prep Week N - Day - Recipes.xlsx' files>" <output folder>

 * DRY list   : copied row-for-row from sheet 2 ("Dry Store Pick") of each workbook (already built by hand/Claude with Husain's rules).
 * FREEZER list: derived here = recipe ingredients located in the Freezer (summed per ingredient) + prep-list rows that
                 mention freezer/frozen (VEG and SOUPS rows are skipped).
 * EARLY      : dishes prepped a day early are picked on the earlier day (Wk2 Friday Moroccan Lamb Tagine + Beef Lasagne -> Thursday).
 * UNITS      : "liter"/"l" -> "kg" is deliberate (Husain's rule: 1 L = 1 kg). mL and g stay as they are.
WARNING: the JSON in data/ is now the source of truth. Write to a scratch folder and diff before copying over data/.
"""
import openpyxl, glob, json, re, os, sys, collections
if len(sys.argv) != 3:
    sys.exit(__doc__)
SRC, OUT = sys.argv[1], sys.argv[2]
DAYS={"monday":"mon","tuesday":"tue","wednesday":"wed","thursday":"thu","friday":"fri"}
DAYNAME={"mon":"Monday","tue":"Tuesday","wed":"Wednesday","thu":"Thursday","fri":"Friday"}
EARLY={(2,"fri"):("thu",{"Moroccan Lamb Tagine","Beef Lasagne"})}   # prepped Thursday, picked Thursday
UNITS={"kilogram":"kg","kg":"kg","liter":"kg","l":"kg","gram":"g","g":"g","milliliter":"mL","ml":"mL","each":"each","piece":"pc","box":"box","bag":"bag","serve":"serve","sheets":"sheets"}
def num(x): return str(int(x)) if float(x).is_integer() else ("%g" % round(x,2))
def amt(a,u):
    if a is None: return ""
    u=(u or "").strip(); 
    if "/" in u:
        b,p=u.split("/",1); return f"{num(a)} {b.lower()} ({p})"
    return f"{num(a)} {UNITS.get(u.lower(),u.lower())}".strip()
def isfreezer(v): return bool(v) and "freezer" in str(v).lower()

entries=[]   # dicts
freezer_src=collections.defaultdict(list)   # (week,day) -> [(dish, ing)]
prep_rows=collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(SRC,"*.xlsx"))):
    m=re.search(r"Week (\d) - (\w+) - Recipes",os.path.basename(f)); week,day=int(m.group(1)),DAYS[m.group(2).lower()]
    wb=openpyxl.load_workbook(f,data_only=True)
    # ---- dry store: copy the user's own sheet
    ws=wb.worksheets[1]; group=None; mode="ing"
    for r in ws.iter_rows(min_row=2,values_only=True):
        a,b,c,d=(list(r)+[None]*4)[:4]
        if a is None: continue
        a=str(a).strip()
        if a=="Ingredient": mode="ing"; continue
        if a=="Item": mode="item"; continue
        if not b and not c and not d: group=a; continue
        entries.append({"week":week,"day":day,"list":"dry","group":group or "","item":a,"pick":str(b or "").strip(),
            "forDish":str(c or "").strip() if mode=="ing" else "","note":str(c or "").strip() if mode=="item" else "",
            "skip": d=="–"})
    # ---- freezer: derive from recipes + prep rows
    bip=set(); dishes={}
    for s in wb.worksheets[2:]:
        title=s.cell(1,1).value.strip(); rows=[]
        if str(s.cell(2,1).value or "").upper().startswith("BIP"): bip.add(title)
        for r in s.iter_rows(min_row=5,values_only=True):
            a,b,c,d,e=(list(r)+[None]*5)[:5]
            if isinstance(a,str) and a.strip() and isinstance(b,(int,float)) and isfreezer(e): rows.append((a.strip(),b,c))
        dishes[title]=rows
    section=None
    for r in wb.worksheets[0].iter_rows(min_row=4,values_only=True):
        a,b,c,d,e=(list(r)+[None]*5)[:5]
        if a in (None,"Item"): continue
        if b is None and c is None and d is None and e is None and a.isupper(): section=a; continue
        if section in ("VEG","SOUPS"): continue
        prep_rows[(week,day)].append((a.strip(),(c or "") if isinstance(c,str) else (num(c) if c else ""),(d or "")))
    freezer_src[(week,day)]=(dishes,bip)

def freezer_for(week,day,dish_filter=None,skip_dishes=()):
    dishes,bip=freezer_src[(week,day)]
    agg=collections.OrderedDict()   # ingredient -> {unit: total}, dishes
    have_ing_rows=set()
    for t,rows in dishes.items():
        if t in skip_dishes or (dish_filter and t not in dish_filter) or t in bip: continue
        for name,a,u in rows:
            have_ing_rows.add(t)
            e=agg.setdefault(name,{"tot":collections.OrderedDict(),"for":[]})
            key=(u or "").strip()
            e["tot"][key]=e["tot"].get(key,0)+a
            e["for"].append(f"{t} ({amt(a,u)})")
    out=[]
    for name in sorted(agg,key=str.lower):
        e=agg[name]; tot=" + ".join(amt(v,k) for k,v in e["tot"].items())
        out.append({"group":"Freezer","item":name,"pick":tot,"forDish":", ".join(e["for"]) if len(e["for"])>1 else e["for"][0].rsplit(" (",1)[0],"note":"","skip":False})
    return out,have_ing_rows,bip

for (week,day),_ in sorted(freezer_src.items()):
    skip=EARLY.get((week,day),(None,set()))[1]
    rows,have,bip=freezer_for(week,day,skip_dishes=skip)
    for x in rows: entries.append({"week":week,"day":day,"list":"freezer",**x})
    for item,qty,notes in prep_rows[(week,day)]:
        low=(item+" "+qty+" "+notes).lower()
        if ("freezer" in low or "frozen" in low) and item not in have and item not in skip:
            if (week,day,item)==(1,"mon","Noodle Singapore (frozen)"): notes=(notes+" · " if notes else "")+"Includes the 3 pkt for Tofu Noodle Stirfry (listed above)"
            entries.append({"week":week,"day":day,"list":"freezer","group":"From the prep list","item":item,"pick":qty,"forDish":"","note":notes,"skip":False})
# early-pick dishes
for (week,day),(to,names) in EARLY.items():
    rows,_,_=freezer_for(week,day,dish_filter=names)
    label="For Friday prep – pick today ("+", ".join(sorted(names))+")"
    for x in rows: entries.append({"week":week,"day":to,"list":"freezer","group":"For Friday prep – pick today","item":x["item"],"pick":x["pick"],"forDish":x["forDish"],"note":"","skip":False})
order={"mon":0,"tue":1,"wed":2,"thu":3,"fri":4}
entries.sort(key=lambda e:(e["week"],order[e["day"]],e["list"]!="dry"))  # stable: keeps source order inside
json.dump(entries,open(os.path.join(OUT,"pick.json"),"w"),indent=1,ensure_ascii=False)
c=collections.Counter((e["list"]) for e in entries); print(c, len(entries))
for k in [(1,"tue"),(2,"thu"),(2,"fri")]:
    print("FREEZER",k,[ (e["group"][:12],e["item"],e["pick"]) for e in entries if (e["week"],e["day"])==k and e["list"]=="freezer"])
