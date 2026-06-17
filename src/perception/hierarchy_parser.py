import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

class HierarchyParser:
    """
    Parses Android UI Automator XML layout trees to locate elements and calculate click coordinates.
    """

    @staticmethod
    def parse_bounds(bounds_str: str) -> Tuple[int, int, int, int]:
        """
        Parse bounds string of format '[left,top][right,bottom]' to (left, top, right, bottom).
        """
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
        if not match:
            raise ValueError(f"Invalid bounds format: {bounds_str}")
        return tuple(map(int, match.groups()))

    @staticmethod
    def get_center_coord(bounds_str: str) -> Tuple[int, int]:
        """
        Calculate center coordinates of a bounds string.
        """
        left, top, right, bottom = HierarchyParser.parse_bounds(bounds_str)
        return (left + right) // 2, (top + bottom) // 2

    @classmethod
    def find_nodes(cls, xml_content: str, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search XML content for nodes matching all criteria.
        Criteria keys can be: 'text', 'resource-id', 'class', 'content-desc'.
        Returns list of matched node attribute dicts with center_x, center_y added.
        """
        if not xml_content.strip():
            return []

        try:
            root = ET.fromstring(xml_content.strip())
        except ET.ParseError as e:
            print(f"[HierarchyParser] XML Parsing Error: {e}")
            return []

        matched_nodes = []
        
        # Traverse all elements
        for elem in root.iter("node"):
            match = True
            for attr, val in criteria.items():
                node_val = elem.get(attr, "")
                if val.startswith("contains:"):
                    # Support partial matching
                    actual_val = val.split("contains:", 1)[1]
                    if actual_val.lower() not in node_val.lower():
                        match = False
                        break
                else:
                    # Strict matching
                    if node_val != val:
                        match = False
                        break
            
            if match:
                attribs = dict(elem.attrib)
                bounds = attribs.get("bounds")
                if bounds:
                    try:
                        cx, cy = cls.get_center_coord(bounds)
                        attribs["center_x"] = cx
                        attribs["center_y"] = cy
                        matched_nodes.append(attribs)
                    except ValueError:
                        pass
        
        return matched_nodes

    @classmethod
    def find_node_by_text(cls, xml_content: str, text: str) -> Dict | None:
        """
        Find first node matching text (exact or containing prefix).
        """
        nodes = cls.find_nodes(xml_content, {"text": text})
        return nodes[0] if nodes else None

    @classmethod
    def find_node_by_id(cls, xml_content: str, resource_id: str) -> Dict | None:
        """
        Find first node matching resource-id.
        """
        nodes = cls.find_nodes(xml_content, {"resource-id": resource_id})
        return nodes[0] if nodes else None

    @classmethod
    def get_actionable_elements(cls, xml_content: str) -> List[Dict]:
        """
        Extract list of all interactive elements (clickable = true or has buttons/text input).
        Used to build a text description of the screen layout for the VLM agent.
        """
        if not xml_content.strip():
            return []

        try:
            root = ET.fromstring(xml_content.strip())
        except ET.ParseError:
            return []

        interactive_elements = []
        for elem in root.iter("node"):
            clickable = elem.get("clickable", "false") == "true"
            text = elem.get("text", "").strip()
            desc = elem.get("content-desc", "").strip()
            res_id = elem.get("resource-id", "").strip()
            class_name = elem.get("class", "").strip()
            bounds = elem.get("bounds", "")

            # If it is clickable, or has text, or is a button/input field
            if clickable or text or desc:
                # Ignore background layout containers with no text/description
                if not text and not desc and "Layout" in class_name:
                    continue
                
                attribs = dict(elem.attrib)
                if bounds:
                    try:
                        cx, cy = cls.get_center_coord(bounds)
                        attribs["center_x"] = cx
                        attribs["center_y"] = cy
                        interactive_elements.append(attribs)
                    except ValueError:
                        pass

        return interactive_elements
