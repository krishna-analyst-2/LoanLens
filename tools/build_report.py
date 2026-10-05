"""Generate the LoanLens report pages (PBIR format) inside LoanLens.Report.

Run with Power BI Desktop closed, then open LoanLens.pbip:

    python tools/build_report.py

Layout and visuals follow docs/04_Dashboard_Build_Guide.md. Existing pages are replaced.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "LoanLens.Report"
DEFINITION = REPORT / "definition"
PAGES_DIR = DEFINITION / "pages"

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
PAGES_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

W, H = 1280, 720
M = 16          # outer margin
G = 8           # gap between visuals
BLUE, RED, GREY, GREEN, WHITE = "#1F4E79", "#C0392B", "#8C8C8C", "#2E7D32", "#FFFFFF"


# ---------------------------------------------------------------- expression helpers

def lit(value):
    if isinstance(value, bool):
        v = "true" if value else "false"
    elif isinstance(value, int):
        v = f"{value}L"
    elif isinstance(value, float):
        v = f"{value}D"
    else:
        v = "'" + str(value).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": v}}}


def color(hex_code):
    return {"solid": {"color": lit(hex_code)}}


def col(table, name):
    return {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def mea(name, table="Loans"):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def ref(field):
    kind = "Column" if "Column" in field else "Measure"
    f = field[kind]
    return f"{f['Expression']['SourceRef']['Entity']}.{f['Property']}"


def proj(field, active=False):
    p = {"field": field, "queryRef": ref(field), "nativeQueryRef": field[next(iter(field))]["Property"]}
    if active:
        p["active"] = True
    return p


def props(**kwargs):
    return {"properties": {k: v for k, v in kwargs.items()}}


def gradient(measure, low=WHITE, high=RED, mid=None, mid_value=None):
    rule = {"min": {"color": {"Literal": {"Value": f"'{low}'"}}},
            "max": {"color": {"Literal": {"Value": f"'{high}'"}}},
            "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}}
    kind = "linearGradient2"
    if mid:
        kind = "linearGradient3"
        rule["mid"] = {"color": {"Literal": {"Value": f"'{mid}'"}},
                       "value": {"Literal": {"Value": f"{mid_value}D"}}}
    return {"solid": {"color": {"expr": {"FillRule": {"Input": measure, "FillRule": {kind: rule}}}}}}


# ---------------------------------------------------------------- visual builders

class Page:
    def __init__(self, name, display_name, hidden=False):
        self.name = name
        self.display_name = display_name
        self.hidden = hidden
        self.visuals = []
        self.extra = {}

    def add(self, x, y, w, h, visual, title=None, alt=None, container=None):
        n = len(self.visuals) + 1
        vco = {**visual.get("visualContainerObjects", {}), **(container or {})}
        if title is not None:
            vco["title"] = [props(show=lit(True), text=lit(title))]
            vco["subTitle"] = [props(show=lit(False))]
        if alt or title:
            vco.setdefault("general", []).append(props(altText=lit(alt or title)))
        if vco:
            visual["visualContainerObjects"] = vco
        self.visuals.append({
            "$schema": VISUAL_SCHEMA,
            "name": f"{self.name}_v{n:02d}",
            "position": {"x": x, "y": y, "z": n * 1000, "height": h, "width": w, "tabOrder": n * 1000},
            "visual": visual,
        })


def query(roles, sort=None):
    q = {"queryState": {role: {"projections": [proj(f, active=(role in ("Category", "Rows"))) for f in fields]}
                        for role, fields in roles.items() if fields}}
    if sort:
        field, direction = sort
        q["sortDefinition"] = {"sort": [{"field": field, "direction": direction}], "isDefaultSort": True}
    return q


def visual(vtype, roles=None, objects=None, sort=None, **extra):
    v = {"visualType": vtype}
    if roles:
        v["query"] = query(roles, sort)
    if objects:
        v["objects"] = objects
    v["drillFilterOtherVisuals"] = True
    v.update(extra)
    return v


def card(measure, units=None, font_color=None, precision=None):
    label = {"fontSize": lit(20.0)}
    if units:
        label["labelDisplayUnits"] = lit(float(units))
    if precision is not None:
        label["labelPrecision"] = lit(precision)
    if font_color:
        label["color"] = color(font_color)
    return visual("card", {"Values": [measure]},
                  {"labels": [{"properties": label}],
                   "categoryLabels": [props(show=lit(True), fontSize=lit(10.0))]})


def textbox(paragraphs):
    """paragraphs: list of (text, {style}) runs per paragraph."""
    out = []
    for para in paragraphs:
        runs = para if isinstance(para, list) else [para]
        out.append({"textRuns": [{"value": t, "textStyle": s} if s else {"value": t} for t, s in runs]})
    return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": out}}]}}


def button(label, action, icon=None, fill=None):
    default = {"selector": {"id": "default"}}
    objects = {
        "text": [props(show=lit(True)),
                 {"properties": {"text": lit(label), "fontColor": color(WHITE), "fontSize": lit(10.0)}, **default}],
        "icon": [props(show=lit(icon is not None))],
        "fill": [props(show=lit(fill is not None))],
    }
    if icon:
        objects["icon"].append({"properties": {"shapeType": lit(icon), "lineColor": color(WHITE)}, **default})
    if fill:
        objects["fill"].append({"properties": {"fillColor": color(fill), "transparency": lit(0.0)}, **default})
    return {"visualType": "actionButton", "objects": objects,
            "visualContainerObjects": {"visualLink": [props(show=lit(True), type=lit(action))]}}


def slicer(field, group):
    return visual("slicer", {"Values": [field]},
                  {"data": [props(mode=lit("Dropdown"))],
                   "header": [props(show=lit(True), fontSize=lit(9.0))]},
                  syncGroup={"groupName": group, "fieldChanges": True, "filterChanges": True})


def rate_combo(category, sort_desc=False):
    """Default Rate as red columns, Overall Default Rate as a grey dashed line on the same axis."""
    overall = mea("Overall Default Rate")
    rate = mea("Default Rate")
    objects = {
        "dataPoint": [
            props(fill=color(RED)),
            {"properties": {"fill": color(RED)}, "selector": {"metadata": ref(rate)}},
            {"properties": {"fill": color(GREY)}, "selector": {"metadata": ref(overall)}},
        ],
        "lineStyles": [
            {"properties": {"lineStyle": lit("dashed"), "strokeWidth": lit(2)},
             "selector": {"metadata": ref(overall)}},
        ],
        "labels": [
            props(show=lit(True), labelPrecision=lit(1), fontSize=lit(8.0)),
            {"properties": {"showSeries": lit(False)}, "selector": {"metadata": ref(overall)}},
        ],
        "valueAxis": [props(show=lit(True), secShow=lit(False))],
        "categoryAxis": [props(axisType=lit("Categorical"))],
        "legend": [props(show=lit(False))],
    }
    return visual("lineClusteredColumnComboChart",
                  {"Category": [category], "Y": [rate], "Y2": [overall],
                   "Tooltips": [mea("Total Loans"), mea("Risk Index")]},
                  objects, sort=(rate, "Descending") if sort_desc else None)


# ---------------------------------------------------------------- shared page chrome

SLICERS = [
    (col("Date", "Year"), "Year"),
    (col("Loans", "LoanPurpose"), "LoanPurpose"),
    (col("Customers", "EmploymentType"), "EmploymentType"),
    (col("Customers", "Education"), "Education"),
]


def chrome(page, subtitle):
    page.add(0, 0, W, 48, textbox([[("LoanLens  ", {"fontWeight": "bold", "fontSize": "18pt", "color": WHITE}),
                                    (subtitle, {"fontSize": "12pt", "color": WHITE})]]),
             alt=f"LoanLens - {subtitle}",
             container={"background": [props(show=lit(True), color=color(BLUE), transparency=lit(0.0))]})
    page.add(560, 6, 704, 36, visual("pageNavigator", objects={"pages": [props(showHiddenPages=lit(False))]}), alt="Page navigation",
             container={"background": [props(show=lit(False))]})
    sw = 240
    for i, (field, group) in enumerate(SLICERS):
        page.add(M + i * (sw + G), 56, sw, 56, slicer(field, group), alt=f"{group} slicer")
    page.add(M + 4 * (sw + G), 64, 150, 40, button("Reset filters", "ClearAllSlicers", fill=BLUE),
             alt="Reset all slicers")


def kpi_row(page, items, y=120, h=84):
    n = len(items)
    w = (W - 2 * M - (n - 1) * G) // n
    for i, (measure, kwargs) in enumerate(items):
        page.add(M + i * (w + G), y, w, h, card(measure, **kwargs), alt=measure["Measure"]["Property"])


# ---------------------------------------------------------------- pages

def overview():
    p = Page("overview", "Overview")
    chrome(p, "Overview")
    kpi_row(p, [
        (mea("Total Loans"), {"units": 1}),
        (mea("Total Customers"), {"units": 1}),
        (mea("Total Loan Amount"), {"units": 1000000, "precision": 1}),
        (mea("Defaulted Loans"), {}),
        (mea("Default Rate"), {"font_color": RED}),
        (mea("Defaulted Amount"), {"units": 1000000, "precision": 1}),
    ])
    y1, h1 = 212, 250
    p.add(M, y1, 400, h1, visual("donutChart", {"Category": [col("Loans", "LoanStatus")], "Y": [mea("Total Loans")]},
                                 {"dataPoint": [props(fill=color(BLUE)),
                                                {"properties": {"fill": color(RED)},
                                                 "selector": {"data": [{"scopeId": {"Comparison": {
                                                     "ComparisonKind": 0,
                                                     "Left": col("Loans", "LoanStatus"),
                                                     "Right": {"Literal": {"Value": "'Default'"}}}}}]}}],
                                  "labels": [props(show=lit(True), labelStyle=lit("Category, percent of total"))]}),
          title="Loans by status")
    rate, overall = mea("Default Rate"), mea("Overall Default Rate")
    p.add(M + 400 + G, y1, W - 2 * M - 400 - G, h1,
          visual("lineChart", {"Category": [col("Date", "Year Quarter")], "Y": [rate, overall]},
                 {"dataPoint": [{"properties": {"fill": color(RED)}, "selector": {"metadata": ref(rate)}},
                                {"properties": {"fill": color(GREY)}, "selector": {"metadata": ref(overall)}}],
                  "lineStyles": [{"properties": {"lineStyle": lit("dashed")}, "selector": {"metadata": ref(overall)}}]}),
          title="Default rate by quarter vs overall")
    y2, h2 = y1 + h1 + G, H - (y1 + h1 + G) - M
    p.add(M, y2, 820, h2, rate_combo(col("Loans", "LoanPurpose"), sort_desc=True),
          title="Default rate by loan purpose")
    p.add(M + 820 + G, y2, W - 2 * M - 820 - G, h2,
          visual("card", {"Values": [mea("Default Rate Headline")]},
                 {"labels": [props(fontSize=lit(16.0), color=color(RED), wordWrap=lit(True))],
                  "categoryLabels": [props(show=lit(False))]}),
          title="Summary", alt="Default rate headline that updates with the slicers")
    return p


def risk_factors():
    p = Page("risk_factors", "Risk Factors")
    chrome(p, "Risk Factors")
    charts = [
        (rate_combo(col("Customers", "Age Group")), "Default rate by age group"),
        (rate_combo(col("Loans", "Interest Rate Band")), "Default rate by interest rate"),
        (rate_combo(col("Customers", "Income Band")), "Default rate by income"),
        (rate_combo(col("Customers", "Employment Length")), "Default rate by employment length"),
        (rate_combo(col("Loans", "Loan Amount Band")), "Default rate by loan amount"),
        (rate_combo(col("Customers", "Credit Score Band")), "Default rate by credit score"),
    ]
    grid_w = 840
    cw = (grid_w - 2 * G) // 3
    ch = (H - 120 - M - G) // 2
    for i, (v, title) in enumerate(charts):
        r, c = divmod(i, 3)
        p.add(M + c * (cw + G), 120 + r * (ch + G), cw, ch, v, title=title)
    risk = mea("Risk Index")
    p.add(M + grid_w + G, 120, W - 2 * M - grid_w - G, H - 120 - M,
          visual("tableEx", {"Values": [col("Customers", "Age Group"), mea("Total Loans"), mea("Default Rate"), risk]},
                 {"values": [{"properties": {"backColor": gradient(risk, low=GREEN, mid=WHITE, mid_value=1.0, high=RED)},
                              "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                                           "metadata": ref(risk)}}]}),
          title="Risk index by age group (1 = average)")
    return p


def trends():
    p = Page("trends", "Trends")
    chrome(p, "Trends")
    top_h = 290
    rate, rolling = mea("Default Rate"), mea("Default Rate 12M Rolling")
    p.add(M, 120, 940, top_h,
          visual("lineChart", {"Category": [col("Date", "Year Month")], "Y": [rate, rolling]},
                 {"dataPoint": [{"properties": {"fill": color("#F5B7B1")}, "selector": {"metadata": ref(rate)}},
                                {"properties": {"fill": color(RED)}, "selector": {"metadata": ref(rolling)}}]}),
          title="Monthly default rate and 12-month rolling average")
    side_x, side_w = M + 940 + G, W - 2 * M - 940 - G
    p.add(side_x, 120, side_w, 120, visual("card", {"Values": [mea("Default Rate vs Prior Year")]},
                 {"labels": [props(fontSize=lit(16.0), wordWrap=lit(True))],
                  "categoryLabels": [props(show=lit(True), fontSize=lit(10.0))]}),
          alt="Default rate change versus the previous year (pick a year in the slicer)")
    p.add(side_x, 120 + 120 + G, side_w, top_h - 120 - G,
          textbox([("About the dates", {"fontWeight": "bold"}),
                   ("IssueDate was added synthetically (2019-2024), so a flat default rate over time is "
                    "expected and should not be read as a real trend. Pick a year in the Year slicer to "
                    "see its change versus the year before.", {"fontSize": "10pt"})]),
          alt="Note about synthetic issue dates")
    y2 = 120 + top_h + G
    h2 = H - y2 - M
    half = (W - 2 * M - G) // 2
    p.add(M, y2, half, h2,
          visual("clusteredColumnChart", {"Category": [col("Date", "Year")], "Y": [mea("Total Loans")],
                                          "Tooltips": [mea("Loan Growth YoY %")]},
                 {"dataPoint": [props(fill=color(BLUE))], "labels": [props(show=lit(True))]}),
          title="Loans issued per year")
    p.add(M + half + G, y2, half, h2,
          visual("lineChart", {"Category": [col("Date", "Year")], "Y": [rate], "Series": [col("Customers", "Age Group")]}),
          title="Default rate by year and age group")
    return p


def borrower_profile():
    p = Page("borrower_profile", "Borrower Profile")
    chrome(p, "Borrower Profile")
    rate = mea("Default Rate")
    heat = {"values": [{"properties": {"backColor": gradient(rate)},
                        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": ref(rate)}}]}
    top_h = 290
    half = (W - 2 * M - G) // 2
    p.add(M, 120, half, top_h,
          visual("pivotTable", {"Rows": [col("Customers", "Age Group")], "Columns": [col("Customers", "Income Band")],
                                "Values": [rate]}, heat),
          title="Default rate by age group and income")
    p.add(M + half + G, 120, half, top_h,
          visual("pivotTable", {"Rows": [col("Customers", "Education")], "Columns": [col("Customers", "EmploymentType")],
                                "Values": [rate]}, heat),
          title="Default rate by education and employment type")
    y2 = 120 + top_h + G
    h2 = H - y2 - M
    w5 = (W - 2 * M - 4 * G) // 5
    items = [
        (col("Customers", "EmploymentType"), "By employment type"),
        (col("Loans", "HasCoSigner"), "By co-signer"),
        (col("Customers", "HasDependents"), "By dependents"),
        (col("Customers", "HasMortgage"), "By mortgage"),
        (col("Loans", "LoanTerm"), "By loan term (months)"),
    ]
    for i, (field, title) in enumerate(items):
        p.add(M + i * (w5 + G), y2, w5, h2, rate_combo(field), title=f"Default rate {title.lower()}")
    return p


def data_quality():
    p = Page("data_quality", "Data Quality")
    chrome(p, "Data Quality")
    kpi_row(p, [(mea(n), {}) for n in (
        "Imputed Income Count", "Imputed Interest Rate Count", "Unknown Age Count",
        "Unknown Credit Score Count", "Unknown Loan Term Count")])
    y2 = 212
    h2 = H - y2 - M
    w3 = (W - 2 * M - 2 * G) // 3
    p.add(M, y2, w3, h2,
          visual("tableEx", {"Values": [col("Cleaning Summary", "Step"), col("Cleaning Summary", "Customers"),
                                        col("Cleaning Summary", "Loans")]},
                 {"total": [props(totals=lit(False))]}),
          title="Cleaning summary (rows)")
    p.add(M + w3 + G, y2, w3, h2,
          visual("donutChart", {"Category": [col("Loans", "InterestRateImputed")], "Y": [mea("Total Loans")]},
                 {"labels": [props(show=lit(True), labelStyle=lit("Category, percent of total"))]}),
          title="Loans with an imputed interest rate")
    b = {"fontSize": "10pt"}
    p.add(M + 2 * (w3 + G), y2, w3, h2, textbox([
        ("Problems found and how they were fixed", {"fontWeight": "bold", "fontSize": "12pt"}),
        ("- Duplicate rows: 458 customers and 250 loans removed", b),
        ("- Extra spaces and empty strings: trimmed, blanks set to null", b),
        ("- Inconsistent categories (case, spelling): mapped to one label, rest to Unknown", b),
        ("- Yes/No flags in mixed formats (Y, true, 1): standardised to Yes/No", b),
        ("- Interest rates stored as text with %: converted to numbers", b),
        ("- Missing Income (687) and InterestRate (398): filled with the median and flagged", b),
        ("- Impossible Age, CreditScore and LoanTerm values: blanked and shown as Unknown", b),
        ("- Mixed date formats (yyyy-MM-dd and dd/MM/yyyy): parsed, 0 failures", b),
        ("Full list: docs/01_Data_Dictionary.md", {"fontSize": "9pt", "fontStyle": "italic"}),
    ]), alt="List of data quality problems and fixes")
    return p


def loan_details():
    p = Page("loan_details", "Loan Details", hidden=True)
    p.add(0, 0, W, 48, textbox([[("Loan Details  ", {"fontWeight": "bold", "fontSize": "18pt", "color": WHITE}),
                                 ("drill-through from any risk chart", {"fontSize": "12pt", "color": WHITE})]]),
          alt="Loan details title",
          container={"background": [props(show=lit(True), color=color(BLUE), transparency=lit(0.0))]})
    p.add(1150, 8, 110, 32, button("Back", "Back", icon="back"), alt="Back to the previous page")
    fields = [col("Loans", c) for c in ("LoanID", "CustomerID", "IssueDate", "LoanAmount", "InterestRate",
                                        "LoanTerm", "Monthly Payment", "Payment to Income", "LoanStatus")]
    p.add(M, 64, W - 2 * M, H - 64 - M, visual("tableEx", {"Values": fields}), title="Loans in the selection")
    drill = [col("Customers", "Age Group"), col("Loans", "Interest Rate Band"), col("Loans", "LoanPurpose")]
    filters = [{"name": f"drill{i}", "field": f, "type": "Categorical", "howCreated": "Drillthrough"}
               for i, f in enumerate(drill, 1)]
    p.extra = {
        "filterConfig": {"filters": filters},
        "pageBinding": {"name": "loan_details_binding", "type": "Drillthrough", "referenceScope": "Default",
                        "parameters": [{"name": f"param{i}", "boundFilter": f"drill{i}", "fieldExpr": f}
                                       for i, f in enumerate(drill, 1)]},
    }
    return p


# ---------------------------------------------------------------- write

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def register_theme():
    report_json = DEFINITION / "report.json"
    report = json.loads(report_json.read_text(encoding="utf-8"))
    theme_name = "LoanLens_theme.json"
    target = REPORT / "StaticResources" / "RegisteredResources" / theme_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "theme" / theme_name, target)
    base = report["themeCollection"]["baseTheme"]
    report["themeCollection"]["customTheme"] = {
        "name": theme_name, "reportVersionAtImport": base["reportVersionAtImport"], "type": "RegisteredResources"}
    packages = [p for p in report.get("resourcePackages", []) if p["type"] != "RegisteredResources"]
    packages.append({"name": "RegisteredResources", "type": "RegisteredResources",
                     "items": [{"name": theme_name, "path": theme_name, "type": "CustomTheme"}]})
    report["resourcePackages"] = packages
    report.setdefault("settings", {})["defaultFilterActionIsDataFilter"] = True
    write_json(report_json, report)


def main():
    pages = [overview(), risk_factors(), trends(), borrower_profile(), data_quality(), loan_details()]
    for old in PAGES_DIR.glob("*"):
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    for page in pages:
        page_json = {"$schema": PAGE_SCHEMA, "name": page.name, "displayName": page.display_name,
                     "displayOption": "FitToPage", "height": H, "width": W, **page.extra}
        if page.hidden:
            page_json["visibility"] = "HiddenInViewMode"
        write_json(PAGES_DIR / page.name / "page.json", page_json)
        for v in page.visuals:
            write_json(PAGES_DIR / page.name / "visuals" / v["name"] / "visual.json", v)
    write_json(PAGES_DIR / "pages.json", {"$schema": PAGES_SCHEMA, "pageOrder": [p.name for p in pages],
                                          "activePageName": pages[0].name})
    register_theme()
    print(f"Wrote {len(pages)} pages, {sum(len(p.visuals) for p in pages)} visuals")


if __name__ == "__main__":
    main()
