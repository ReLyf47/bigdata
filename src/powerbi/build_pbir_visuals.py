import os
import json
import shutil

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = str(PROJECT_ROOT / 'tugas' / 'minggu10' / 'powerbi_project')
REPORT_DIR = os.path.join(BASE_DIR, 'BigData.Report')
PAGE_DIR = os.path.join(REPORT_DIR, 'definition', 'pages', 'd7e0562ac201fd4176a6')
VISUALS_DIR = os.path.join(PAGE_DIR, 'visuals')

SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"
ENTITY_NAME = "public nhtsa_crash_analytics"

def create_card_visual(name, x, y, width, height, tab_order, measure_name):
    return {
        "$schema": SCHEMA_URL,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.{measure_name}",
                                "nativeQueryRef": measure_name
                            }
                        ]
                    }
                }
            }
        }
    }

def create_slicer_visual(name, x, y, width, height, tab_order, column_name):
    return {
        "$schema": SCHEMA_URL,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": column_name
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.{column_name}",
                                "nativeQueryRef": column_name
                            }
                        ]
                    }
                }
            }
        }
    }

def create_line_chart(name, x, y, width, height, tab_order):
    return {
        "$schema": SCHEMA_URL,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "HierarchyLevel": {
                                        "Expression": {
                                            "Hierarchy": {
                                                "Expression": {
                                                    "PropertyVariationSource": {
                                                        "Expression": {
                                                            "SourceRef": {
                                                                "Entity": ENTITY_NAME
                                                            }
                                                        },
                                                        "Name": "Variation",
                                                        "Property": "crash_date"
                                                    }
                                                },
                                                "Hierarchy": "Date Hierarchy"
                                            }
                                        },
                                        "Level": "Year"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.crash_date.Variation.Date Hierarchy.Year",
                                "nativeQueryRef": "crash_date Year",
                                "active": True
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": "Total Fatalities"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.Total Fatalities",
                                "nativeQueryRef": "Total Fatalities"
                            }
                        ]
                    }
                }
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_donut_chart(name, x, y, width, height, tab_order):
    return {
        "$schema": SCHEMA_URL,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "donutChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": "weather_category"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.weather_category",
                                "nativeQueryRef": "weather_category",
                                "active": True
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": "Total Fatalities"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.Total Fatalities",
                                "nativeQueryRef": "Total Fatalities"
                            }
                        ]
                    }
                }
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_bar_chart(name, x, y, width, height, tab_order):
    return {
        "$schema": SCHEMA_URL,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": "state_name"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.state_name",
                                "nativeQueryRef": "state_name",
                                "active": True
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": ENTITY_NAME
                                            }
                                        },
                                        "Property": "Total Fatalities"
                                    }
                                },
                                "queryRef": f"{ENTITY_NAME}.Total Fatalities",
                                "nativeQueryRef": "Total Fatalities"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Measure": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Entity": ENTITY_NAME
                                        }
                                    },
                                    "Property": "Total Fatalities"
                                }
                            },
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": True
                }
            },
            "drillFilterOtherVisuals": True
        }
    }

def build_all_visuals():
    os.makedirs(VISUALS_DIR, exist_ok=True)
    
    # 1. KPI Cards
    cards = [
        ("a1000000000000000001", 30, 30, 330, 150, 1, "Total Cases"),
        ("a1000000000000000002", 380, 30, 330, 150, 2, "Total Fatalities"),
        ("a1000000000000000003", 730, 30, 330, 150, 3, "Total Vehicles"),
        ("a1000000000000000004", 1080, 30, 330, 150, 4, "Avg Fatalities"),
    ]
    for cid, x, y, w, h, t, m in cards:
        v = create_card_visual(cid, x, y, w, h, t, m)
        cdir = os.path.join(VISUALS_DIR, cid)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "visual.json"), "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)
        print(f"Created card: {m} -> {cid}")

    # 2. Slicer (State Filter)
    slicer_id = "a1000000000000000005"
    s_vis = create_slicer_visual(slicer_id, 1430, 30, 460, 150, 5, "state_name")
    sdir = os.path.join(VISUALS_DIR, slicer_id)
    os.makedirs(sdir, exist_ok=True)
    with open(os.path.join(sdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(s_vis, f, indent=2)
    print(f"Created slicer -> {slicer_id}")

    # 3. Line Chart (Trend over time)
    line_id = "a2000000000000000001"
    l_vis = create_line_chart(line_id, 30, 200, 1180, 470, 6)
    ldir = os.path.join(VISUALS_DIR, line_id)
    os.makedirs(ldir, exist_ok=True)
    with open(os.path.join(ldir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(l_vis, f, indent=2)
    print(f"Created line chart -> {line_id}")

    # 4. Donut Chart (Weather Category)
    donut_id = "a2000000000000000002"
    d_vis = create_donut_chart(donut_id, 1230, 200, 660, 470, 7)
    ddir = os.path.join(VISUALS_DIR, donut_id)
    os.makedirs(ddir, exist_ok=True)
    with open(os.path.join(ddir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(d_vis, f, indent=2)
    print(f"Created donut chart -> {donut_id}")

    # 5. Clustered Bar Chart (Fatalities by State)
    bar_id = "a3000000000000000001"
    b_vis = create_bar_chart(bar_id, 30, 690, 600, 360, 8)
    bdir = os.path.join(VISUALS_DIR, bar_id)
    os.makedirs(bdir, exist_ok=True)
    with open(os.path.join(bdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(b_vis, f, indent=2)
    print(f"Created bar chart -> {bar_id}")

    # 6. Reposition existing County Column Chart
    county_file = os.path.join(VISUALS_DIR, "b88309762287b41e60e1", "visual.json")
    if os.path.exists(county_file):
        with open(county_file, "r", encoding="utf-8") as f:
            cdata = json.load(f)
        cdata["position"] = {
            "x": 650,
            "y": 690,
            "z": 9,
            "height": 360,
            "width": 590,
            "tabOrder": 9
        }
        with open(county_file, "w", encoding="utf-8") as f:
            json.dump(cdata, f, indent=2)
        print("Updated position for county column chart (b88309762287b41e60e1).")

    # 7. Reposition existing Case Details Table
    table_file = os.path.join(VISUALS_DIR, "ca0dec2de616ab19f157", "visual.json")
    if os.path.exists(table_file):
        with open(table_file, "r", encoding="utf-8") as f:
            tdata = json.load(f)
        tdata["position"] = {
            "x": 1260,
            "y": 690,
            "z": 10,
            "height": 360,
            "width": 630,
            "tabOrder": 10
        }
        with open(table_file, "w", encoding="utf-8") as f:
            json.dump(tdata, f, indent=2)
        print("Updated position for case details table (ca0dec2de616ab19f157).")

if __name__ == '__main__':
    build_all_visuals()
