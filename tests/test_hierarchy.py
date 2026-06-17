import pytest
from src.perception.hierarchy_parser import HierarchyParser

def test_parse_bounds():
    bounds = "[100,200][900,400]"
    left, top, right, bottom = HierarchyParser.parse_bounds(bounds)
    assert left == 100
    assert top == 200
    assert right == 900
    assert bottom == 400

def test_get_center_coord():
    bounds = "[100,200][900,400]"
    cx, cy = HierarchyParser.get_center_coord(bounds)
    assert cx == 500  # (100 + 900) // 2
    assert cy == 300  # (200 + 400) // 2

def test_find_nodes_with_criteria():
    xml_data = """<?xml version="1.0" encoding="utf-8"?>
    <hierarchy>
        <node index="0" text="Netflix Games" resource-id="com.netflix:id/title" bounds="[100,200][900,400]" clickable="false" />
        <node index="1" text="SIGN IN" resource-id="com.netflix:id/btn_login" bounds="[300,1000][700,1100]" clickable="true" />
    </hierarchy>
    """
    
    # 1. Find SIGN IN node
    btn = HierarchyParser.find_node_by_text(xml_data, "SIGN IN")
    assert btn is not None
    assert btn["resource-id"] == "com.netflix:id/btn_login"
    assert btn["center_x"] == 500
    assert btn["center_y"] == 1050

    # 2. Find node by id
    title = HierarchyParser.find_node_by_id(xml_data, "com.netflix:id/title")
    assert title is not None
    assert title["text"] == "Netflix Games"

    # 3. Find non-existent node
    none_node = HierarchyParser.find_node_by_text(xml_data, "PLAY")
    assert none_node is None

def test_get_actionable_elements():
    xml_data = """<?xml version="1.0" encoding="utf-8"?>
    <hierarchy>
        <node index="0" text="Title" clickable="false" bounds="[0,0][100,100]" />
        <node index="1" text="" clickable="true" bounds="[100,100][200,200]" />
        <node index="2" class="android.widget.RelativeLayout" clickable="false" bounds="[200,200][300,300]" />
    </hierarchy>
    """
    actionables = HierarchyParser.get_actionable_elements(xml_data)
    # Node 0 has text, Node 1 is clickable. Node 2 is a Layout container with no text or desc (should be ignored).
    assert len(actionables) == 2
    assert actionables[0]["text"] == "Title"
    assert actionables[1]["clickable"] == "true"
