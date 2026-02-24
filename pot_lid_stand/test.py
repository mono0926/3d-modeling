import cadquery as cq
import os

STAND_WIDTH = 160.0
ARM_HEIGHT = 80.0
VALLEY_WIDTH = 100.0

def make_wire(z, y_under, y_valley):
    v2 = VALLEY_WIDTH / 2.0
    s2 = STAND_WIDTH / 2.0
    return (
        cq.Workplane("XY", origin=(0, 0, z))
        .moveTo(-s2, y_under)
        .lineTo(s2, y_under)
        .lineTo(s2, ARM_HEIGHT)
        .lineTo(v2, ARM_HEIGHT)
        .threePointArc((0, y_valley), (-v2, ARM_HEIGHT))
        .lineTo(-s2, ARM_HEIGHT)
        .close()
    )

w0 = make_wire(z=0.0, y_under=0.0, y_valley=35.0)
w1 = make_wire(z=35.0, y_under=8.0, y_valley=10.0)
w2 = make_wire(z=48.0, y_under=11.0, y_valley=45.0)
w3 = make_wire(z=55.0, y_under=12.0, y_valley=45.0)

wires = [w0.wires().val(), w1.wires().val(), w2.wires().val(), w3.wires().val()]
body = cq.Solid.makeLoft(wires, ruled=False)

# Optional: Add small fillets to the sharp outer edges (X edges and Y edges)
body_wp = cq.Workplane("XY").add(body)
try:
    body_wp = body_wp.edges("|Z or |X or |Y").fillet(2.0)
except Exception as e:
    pass

cq.exporters.export(body_wp, "test_loft.step")
