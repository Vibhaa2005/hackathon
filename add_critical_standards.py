"""Add critical missing BIS standards to bis_standards.json and rebuild FAISS index."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

CRITICAL = [
    {
        "id": "CC_9001", "standard_number": "IS 269:2015",
        "title": "Ordinary Portland Cement 33 Grade — Specification",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for ordinary portland cement 33 grade for general construction and masonry work. (Fifth Revision)",
        "scope": "OPC 33 grade cement for general construction, masonry, plastering and non-structural applications where high early strength is not required.",
        "key_requirements": [
            "Minimum 28-day compressive strength 33 MPa",
            "Minimum 7-day compressive strength 22 MPa",
            "Minimum 3-day compressive strength 16 MPa",
            "Fineness minimum 225 m2/kg by Blaine method",
            "Initial setting time not less than 30 minutes",
            "Final setting time not more than 600 minutes",
            "Soundness Le Chatelier expansion not more than 10 mm",
            "MgO content not more than 6%"
        ],
        "applicable_products": ["General construction", "Masonry work", "Plastering"],
        "year": 2015,
        "keywords": ["ordinary","portland","cement","33","grade","opc","general","construction","masonry","plastering"],
        "text": "IS 269:2015 | Ordinary Portland Cement 33 Grade Specification | Cement and Concrete | OPC 33 grade general construction masonry plastering compressive strength 33 MPa fineness soundness setting time"
    },
    {
        "id": "CC_9002", "standard_number": "IS 8112:2013",
        "title": "Ordinary Portland Cement 43 Grade — Specification",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for OPC 43 grade used in reinforced concrete, precast concrete and multi-storey buildings. (Second Revision)",
        "scope": "OPC 43 grade cement for reinforced concrete construction, precast elements, multi-storey buildings, bridges, and general structural applications requiring medium-high strength.",
        "key_requirements": [
            "Minimum 28-day compressive strength 43 MPa",
            "Minimum 7-day compressive strength 33 MPa",
            "Minimum 3-day compressive strength 23 MPa",
            "Fineness minimum 225 m2/kg by Blaine method",
            "Initial setting time not less than 30 minutes",
            "Final setting time not more than 600 minutes",
            "SO3 content not more than 3.5%",
            "MgO content not more than 6%"
        ],
        "applicable_products": ["Reinforced concrete", "Multi-storey buildings", "Bridges", "Precast elements"],
        "year": 2013,
        "keywords": ["ordinary","portland","cement","43","grade","opc","reinforced","concrete","rcc","multi-storey","bridge","precast"],
        "text": "IS 8112:2013 | Ordinary Portland Cement 43 Grade Specification | Cement and Concrete | OPC 43 grade reinforced concrete RCC multi-storey building bridge precast structural compressive strength 43 MPa"
    },
    {
        "id": "CC_9003", "standard_number": "IS 12269:2013",
        "title": "Ordinary Portland Cement 53 Grade — Specification",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for OPC 53 grade used in high-strength concrete, prestressed concrete and high-rise structures. (First Revision)",
        "scope": "OPC 53 grade cement for prestressed concrete, high-strength concrete grades M40 and above, high-rise buildings, and applications requiring rapid early strength gain.",
        "key_requirements": [
            "Minimum 28-day compressive strength 53 MPa",
            "Minimum 7-day compressive strength 37 MPa",
            "Minimum 3-day compressive strength 27 MPa",
            "Fineness minimum 225 m2/kg by Blaine method",
            "Initial setting time not less than 30 minutes",
            "C3A content not more than 10% for normal, 5% for moderate sulphate resistance",
            "MgO content not more than 6%",
            "Loss on ignition not more than 4%"
        ],
        "applicable_products": ["Prestressed concrete", "High-strength concrete M40+", "High-rise structures"],
        "year": 2013,
        "keywords": ["ordinary","portland","cement","53","grade","opc","high","strength","prestressed","concrete","high-rise","rapid"],
        "text": "IS 12269:2013 | Ordinary Portland Cement 53 Grade Specification | Cement and Concrete | OPC 53 grade high strength prestressed concrete high-rise building rapid strength gain M40 M50 M60"
    },
    {
        "id": "CC_9004", "standard_number": "IS 1489 (Part 1):2015",
        "title": "Portland Pozzolana Cement (Fly Ash Based) — Specification",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for PPC fly ash based cement for marine structures, mass concrete and underground foundations. (Third Revision)",
        "scope": "Portland Pozzolana Cement fly ash based for marine structures, mass concrete, underground foundations, hydraulic structures and general construction where reduced heat of hydration and improved durability are needed.",
        "key_requirements": [
            "Fly ash content 15 to 35 percent by mass",
            "Minimum 28-day compressive strength 33 MPa",
            "Fineness minimum 300 m2/kg by Blaine method",
            "Initial setting time not less than 30 minutes",
            "Final setting time not more than 600 minutes",
            "Soundness Le Chatelier expansion not more than 10 mm",
            "MgO content not more than 6%",
            "Loss on ignition not more than 5%"
        ],
        "applicable_products": ["Marine structures", "Mass concrete", "Underground foundations", "Hydraulic structures"],
        "year": 2015,
        "keywords": ["portland","pozzolana","cement","ppc","fly","ash","marine","mass","concrete","underground","foundation","hydraulic","durability"],
        "text": "IS 1489 (Part 1):2015 | Portland Pozzolana Cement Fly Ash Based Specification | Cement and Concrete | PPC fly ash marine structures mass concrete underground foundation reduced heat hydration durability"
    },
    {
        "id": "CC_9005", "standard_number": "IS 456:2000",
        "title": "Plain and Reinforced Concrete — Code of Practice",
        "category": "Cement and Concrete",
        "description": "Code of practice for plain and reinforced concrete covering structural design, materials, workmanship and durability. (Fourth Revision)",
        "scope": "Lays down general structural use of plain and reinforced concrete including mix design, cover requirements, durability criteria, workmanship and inspection for all concrete construction.",
        "key_requirements": [
            "Minimum cement content and maximum water-cement ratio per exposure condition",
            "Nominal cover 20mm mild, 30mm moderate, 45mm severe, 50mm very severe",
            "Concrete grades M10 to M80 by characteristic compressive strength",
            "Mix design as per IS 10262",
            "Maximum w/c ratio 0.45 moderate, 0.40 severe exposure",
            "Curing minimum 7 days for OPC, 10 days for PPC/GGBS",
            "Minimum grade M20 for reinforced concrete",
            "Slump limits 25-75mm for columns/beams, 50-100mm for slabs"
        ],
        "applicable_products": ["All reinforced concrete structures", "Foundations", "Columns", "Beams", "Slabs"],
        "year": 2000,
        "keywords": ["plain","reinforced","concrete","code","practice","rcc","design","mix","cover","durability","structural"],
        "text": "IS 456:2000 | Plain and Reinforced Concrete Code of Practice | Cement and Concrete | RCC design mix design cover reinforcement durability exposure structural all concrete grades M20 M25 M30"
    },
    {
        "id": "CC_9006", "standard_number": "IS 516:2018",
        "title": "Hardened Concrete — Methods of Test",
        "category": "Cement and Concrete",
        "description": "Methods of tests for hardened concrete including compressive strength, flexural strength and water absorption. (Second Revision)",
        "scope": "Methods of tests for determining strength and other properties of hardened concrete cubes, cylinders and beams for quality control and compliance testing at construction sites and laboratories.",
        "key_requirements": [
            "Cube specimen 150mm x 150mm x 150mm for compressive strength test",
            "Curing in water at 27 plus or minus 2 degrees Celsius",
            "Testing at 7 days and 28 days after casting",
            "Loading rate 140 kg/cm2 per minute for compression",
            "Minimum 3 specimens per sample for statistical validity",
            "Flexural strength by centre-point or third-point loading on beam",
            "Splitting tensile strength on cylinder specimen",
            "Water absorption on oven dried specimens"
        ],
        "applicable_products": ["Concrete quality control", "RCC construction", "Bridge testing", "Structural compliance"],
        "year": 2018,
        "keywords": ["concrete","test","compressive","strength","cube","hardened","flexural","quality","control","rcc","bridge","150mm","28","days"],
        "text": "IS 516:2018 | Hardened Concrete Methods of Test | Cement and Concrete | compressive strength cube test 150mm 28 days quality control RCC bridge flexural splitting tensile testing"
    },
    {
        "id": "CC_9007", "standard_number": "IS 383:2016",
        "title": "Coarse and Fine Aggregate for Concrete — Specification",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for natural and crushed coarse aggregate and fine aggregate for use in concrete. (Third Revision)",
        "scope": "Coarse and fine aggregate from natural sources or crushed rock for plain and reinforced concrete mix design, including 10mm, 16mm, 20mm and 40mm nominal sizes.",
        "key_requirements": [
            "Grading zones I to IV for fine aggregate",
            "Nominal sizes 10mm, 16mm, 20mm, 40mm for coarse aggregate",
            "Fineness modulus fine aggregate 2.0 to 3.5",
            "Los Angeles abrasion value not more than 30% for M35+ concrete",
            "Flakiness and elongation index combined not more than 35%",
            "Deleterious materials: silt not more than 3%, clay lumps not more than 1%",
            "Water absorption not more than 2% for coarse aggregate",
            "Aggregate impact value not more than 30%"
        ],
        "applicable_products": ["M25 concrete", "M30 concrete", "M35 concrete", "RCC mix design", "Foundations"],
        "year": 2016,
        "keywords": ["coarse","aggregate","fine","aggregate","concrete","crushed","stone","gravel","mix","design","grading","20mm","M30"],
        "text": "IS 383:2016 | Coarse and Fine Aggregate for Concrete Specification | Cement and Concrete | coarse aggregate 20mm crushed stone gravel concrete mix design M25 M30 grading zone flakiness abrasion"
    },
    {
        "id": "CR_9008", "standard_number": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification",
        "category": "Concrete Reinforcement",
        "description": "Specifies requirements for TMT/HYSD deformed steel bars Fe415 to Fe600 for reinforced concrete. (Fourth Revision)",
        "scope": "TMT and HYSD high strength deformed steel bars for RCC construction, including grades Fe415, Fe500, Fe500D, Fe550, Fe550D, Fe600 for general and seismic/earthquake resistant construction.",
        "key_requirements": [
            "Fe415: yield strength 415 MPa minimum, UTS 485 MPa, elongation 14.5%",
            "Fe500: yield strength 500 MPa minimum, UTS 545 MPa, elongation 12%",
            "Fe500D: yield 500 MPa, elongation 16%, UTS/YS ratio min 1.15 for seismic",
            "Fe550D: yield 550 MPa, elongation 14.5%, UTS/YS ratio min 1.15",
            "Fe600: yield strength 600 MPa minimum, UTS 660 MPa",
            "D grades: enhanced ductility for earthquake resistant seismic zone V structures",
            "Rebend test required for all grades",
            "Mandatory BIS certification mark"
        ],
        "applicable_products": ["TMT bars", "HYSD bars", "RCC reinforcement", "Earthquake resistant structures", "Seismic zone buildings"],
        "year": 2008,
        "keywords": ["tmt","hysd","deformed","steel","bars","reinforcement","fe415","fe500","fe500d","fe550","fe600","rcc","earthquake","seismic"],
        "text": "IS 1786:2008 | High Strength Deformed Steel Bars and Wires for Concrete Reinforcement | Concrete Reinforcement | TMT HYSD bars Fe500 Fe500D Fe415 Fe550 Fe600 RCC earthquake seismic zone ductility"
    },
    {
        "id": "SS_9009", "standard_number": "IS 2062:2011",
        "title": "Hot Rolled Medium and High Tensile Structural Steel — Specification",
        "category": "Structural Steels",
        "description": "Specifies requirements for structural steel plates, strips, shapes and sections for general structural purposes. (Seventh Revision)",
        "scope": "Hot rolled structural steel grades E165 to E650 for industrial buildings, roof trusses, bridges, transmission towers, warehouse structures and steel frames.",
        "key_requirements": [
            "Grade E250 (Fe410): yield 250 MPa, UTS 410 MPa for general structural use",
            "Grade E350: yield 350 MPa for heavy structural applications",
            "Grade E450: yield 450 MPa for high strength structural work",
            "Chemical composition limits for C, Mn, S, P, Si per grade",
            "Charpy V-notch impact test for sub-grade selection",
            "Weldability requirements for all grades",
            "Dimensional tolerances for plates and sections as per IS 1852",
            "Ultrasonic testing for plates above 40mm thickness"
        ],
        "applicable_products": ["Industrial buildings", "Roof trusses", "Bridges", "Transmission towers", "Warehouse structures"],
        "year": 2011,
        "keywords": ["structural","steel","hot","rolled","plates","sections","e250","e350","fe410","industrial","building","truss","bridge","warehouse"],
        "text": "IS 2062:2011 | Hot Rolled Medium and High Tensile Structural Steel Specification | Structural Steels | structural steel E250 E350 Fe410 plates sections industrial building roof truss bridge warehouse weldability"
    },
    {
        "id": "CC_9010", "standard_number": "IS 2185 (Part 1):2005",
        "title": "Concrete Masonry Units — Hollow and Solid Concrete Blocks",
        "category": "Cement and Concrete",
        "description": "Specifies requirements for hollow and solid concrete blocks for load bearing and non-load bearing wall construction. (Third Revision)",
        "scope": "Hollow and solid concrete blocks for load bearing and non-load bearing partition walls in residential and commercial buildings, apartment complexes.",
        "key_requirements": [
            "Grade A: minimum compressive strength 5.0 N/mm2 for load bearing walls",
            "Grade B: minimum compressive strength 3.5 N/mm2 for non-load bearing",
            "Standard block size 400mm x 200mm x 200mm",
            "Hollow blocks void area not more than 50% of gross cross-sectional area",
            "Water absorption not more than 10% by mass",
            "Drying shrinkage not more than 0.09%",
            "Shell and web minimum thickness 25mm",
            "Flatness deviation of face not more than 3mm"
        ],
        "applicable_products": ["Hollow concrete blocks", "Non-load bearing partition walls", "Load bearing walls", "Apartments"],
        "year": 2005,
        "keywords": ["hollow","concrete","blocks","solid","masonry","partition","wall","load","bearing","apartment","grade","non-load"],
        "text": "IS 2185 (Part 1):2005 | Concrete Masonry Units Hollow and Solid Concrete Blocks | Cement and Concrete | hollow concrete blocks non-load bearing partition wall apartment Grade A Grade B compressive strength"
    },
]

with open("data/bis_standards.json", encoding="utf-8") as f:
    stds = json.load(f)

existing = {s["standard_number"] for s in stds}
added = 0
for s in CRITICAL:
    if s["standard_number"] not in existing:
        stds.append(s)
        added += 1
        print(f"  + {s['standard_number']}")

print(f"\nAdded {added} standards. Total: {len(stds)}")

with open("data/bis_standards.json", "w", encoding="utf-8") as f:
    json.dump(stds, f, ensure_ascii=False, indent=2)
