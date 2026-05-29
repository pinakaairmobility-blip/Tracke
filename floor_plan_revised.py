import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import matplotlib.lines as mlines
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(28, 20))
ax.set_xlim(0, 37.15)
ax.set_ylim(0, 28.38)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor('white')

# ── helpers ──────────────────────────────────────────────────────────────────
def ft(feet, inches=0):
    return (feet + inches / 12) * 0.3048

def room(ax, x, y, w, h, label, dim, color='white', fs=6.5, dim_fs=5.5, revised=False):
    ec = '#CC2200' if revised else '#222222'
    lw = 1.8 if revised else 1.2
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor=ec,
                               facecolor='#FFF5F5' if revised else color, zorder=2)
    ax.add_patch(rect)
    cx, cy = x + w / 2, y + h / 2
    ax.text(cx, cy + 0.08, label, ha='center', va='center',
            fontsize=fs, fontweight='bold', color='#111111')
    ax.text(cx, cy - 0.22, dim, ha='center', va='center',
            fontsize=dim_fs, color='#CC2200' if revised else '#444444',
            style='italic')

def wall(ax, x1, y1, x2, y2, lw=2.0):
    ax.plot([x1, x2], [y1, y2], color='#111111', linewidth=lw, zorder=3)

def hatch_rect(ax, x, y, w, h, color='#DDDDDD'):
    rect = patches.Rectangle((x, y), w, h, linewidth=0.8, edgecolor='#999999',
                               facecolor=color, hatch='////', zorder=1)
    ax.add_patch(rect)

def label_only(ax, x, y, txt, fs=6, color='#333333'):
    ax.text(x, y, txt, ha='center', va='center', fontsize=fs, color=color)

# ── overall building outline ──────────────────────────────────────────────────
# building sits on plot; road widening is shown outside
bldg_x, bldg_y = 1.5, 3.5
bldg_w, bldg_h = 34.0, 21.0

# road strips
# bottom road
ax.add_patch(patches.Rectangle((0, 0), 37.15, 3.5, facecolor='#E8E8E8', edgecolor='none'))
ax.text(18.5, 1.75, '--- PROPOSED ROAD 9.00 MT WIDE ---', ha='center', va='center',
        fontsize=7, color='#555555', style='italic')

# right road
ax.add_patch(patches.Rectangle((35.65, 3.5), 1.5, 18, facecolor='#E8E8E8', edgecolor='none'))
ax.text(36.4, 12.5, 'EXISTING ROAD\n6.00 MT WIDE', ha='center', va='center',
        fontsize=5.5, color='#555555', style='italic', rotation=90)

ax.add_patch(patches.Rectangle((34.15, 3.5), 1.5, 18, facecolor='#F0F0F0', edgecolor='none'))
ax.text(34.9, 12.5, 'ROAD\nWIDENING\n1.50 MT', ha='center', va='center',
        fontsize=5, color='#888888', rotation=90)

# left road
ax.add_patch(patches.Rectangle((0, 3.5), 1.5, 18, facecolor='#E8E8E8', edgecolor='none'))
ax.text(0.75, 12.5, '--- PROPOSED ROAD 9.00 MT WIDE ---', ha='center', va='center',
        fontsize=5.5, color='#555555', style='italic', rotation=90)

# ─────────────────────────────────────────────────────────────────────────────
# PASSAGE / CORE  (central horizontal corridor)
# ─────────────────────────────────────────────────────────────────────────────
pass_y = bldg_y + 9.0
pass_h = ft(8)          # 8'0" passage
passage_x = bldg_x
passage_w = bldg_w

ax.add_patch(patches.Rectangle((passage_x, pass_y), passage_w, pass_h,
             facecolor='#F5F5F0', edgecolor='#333333', linewidth=1.2, zorder=2))
ax.text(passage_x + passage_w/2, pass_y + pass_h/2,
        "PASSAGE  8'0\" WIDE", ha='center', va='center', fontsize=7.5,
        fontweight='bold', color='#333333')

# mailbox strip (revised — 1'6" of passage used for built-in mailboxes)
mb_w = ft(1, 6)
ax.add_patch(patches.Rectangle((passage_x, pass_y), mb_w, pass_h,
             facecolor='#D8EAD8', edgecolor='#3A7A3A', linewidth=1.0,
             hatch='||', zorder=3))
ax.text(passage_x + mb_w/2, pass_y + pass_h/2,
        "MAIL\nBOX\n1'6\"", ha='center', va='center', fontsize=5, color='#3A7A3A')

# LIFT + STAIR CORE (centred in building)
core_x = bldg_x + bldg_w/2 - 1.8
core_w = 3.6
lift_w = ft(6)           # REVISED: 6'0"×7'6" (NBC compliant)
lift_h = ft(7, 6)
lift_x = core_x + 0.2
lift_y = pass_y + (pass_h - lift_h) / 2

ax.add_patch(patches.Rectangle((lift_x, lift_y), lift_w, lift_h,
             facecolor='#E0E8F0', edgecolor='#222288', linewidth=1.5, zorder=4))
ax.text(lift_x + lift_w/2, lift_y + lift_h/2 + 0.15, 'LIFT', ha='center',
        va='center', fontsize=6.5, fontweight='bold', color='#222288')
ax.text(lift_x + lift_w/2, lift_y + lift_h/2 - 0.2, "6'0\"×7'6\"",
        ha='center', va='center', fontsize=5.5, color='#CC2200', style='italic')
ax.text(lift_x + lift_w/2, lift_y + lift_h/2 - 0.45, "(NBC REVISED)",
        ha='center', va='center', fontsize=5, color='#CC2200')

# stair boxes
stair_x = lift_x + lift_w + 0.15
stair_w = core_x + core_w - stair_x
stair_h = pass_h
ax.add_patch(patches.Rectangle((stair_x, pass_y), stair_w, stair_h,
             facecolor='#F0F0E8', edgecolor='#444444', linewidth=1.0, zorder=3))
ax.text(stair_x + stair_w/2, pass_y + stair_h/2 + 0.1, 'UP', ha='center',
        va='center', fontsize=6, color='#444444')
ax.text(stair_x + stair_w/2, pass_y + stair_h/2 - 0.2, 'DN', ha='center',
        va='center', fontsize=6, color='#444444')

# shafts
for sx in [bldg_x + 7.8, bldg_x + 20.0]:
    ax.add_patch(patches.Rectangle((sx, pass_y), 0.6, pass_h,
                 facecolor='#CCCCCC', edgecolor='#555555', linewidth=0.8,
                 hatch='xx', zorder=3))
    ax.text(sx + 0.3, pass_y + pass_h/2, 'S\nH\nA\nF\nT', ha='center',
            va='center', fontsize=4.5, color='#555555')

# ─────────────────────────────────────────────────────────────────────────────
# FLAT 104 — 3BHK  (1320 sqft) LEFT side, below passage
# ─────────────────────────────────────────────────────────────────────────────
f4_x = bldg_x
f4_y = bldg_y
f4_w = 8.4
f4_top = pass_y

# balcony bottom (REVISED 5'0")
bal4_h = ft(5)           # REVISED from 4'0" to 5'0"
room(ax, f4_x, f4_y, ft(4), bal4_h, 'UTILITY', "4'0\" WIDE", color='#F0F5FF')
room(ax, f4_x + ft(4), f4_y, f4_w - ft(4), bal4_h,
     'BALCONY', "5'0\" WIDE ★", color='#E8F5E8', revised=True)

# rooms above balcony
room_y = f4_y + bal4_h
living_h = ft(17)
# Living
room(ax, f4_x, room_y, ft(10), ft(17),
     'LIVING', "10'0\"×17'0\"", color='#FFFDE8')
# Kitchen REVISED (reduced 1'9" to give balcony)
room(ax, f4_x + ft(10), room_y, ft(10), ft(13, 6),
     'KITCHEN', "10'0\"×13'6\" ★", color='#FFF5F5', revised=True)

# bedrooms above living/kitchen (upper portion of flat 104 block)
bed_y = room_y + ft(11)
room(ax, f4_x, bed_y, ft(10), ft(10, 6),
     'M.BEDROOM', "10'0\"×10'6\"", color='#F8F0FF')
room(ax, f4_x + ft(10), bed_y, ft(10), ft(11, 6),
     'BEDROOM', "10'0\"×11'6\"", color='#F8F0FF')

# toilets strip
tlt_y = room_y + ft(13, 6)
room(ax, f4_x + ft(10), tlt_y, ft(4), ft(4), 'A.TOILET', "7'0\"×4'0\"",
     color='#EEF5FF')
room(ax, f4_x + ft(10) + ft(4), tlt_y, ft(4), ft(4), 'C.TOILET', "7'3\"×4'0\"",
     color='#EEF5FF')

ax.text(f4_x + f4_w/2, f4_y + (f4_top - f4_y)/2 + 0.3,
        'FLAT NO\n104,204,304\n404,504,604',
        ha='center', va='center', fontsize=6, color='#880000', fontweight='bold')
ax.text(f4_x + f4_w/2, f4_y + (f4_top - f4_y)/2 - 0.45,
        '1320.00 SQFT', ha='center', va='center', fontsize=6, color='#555555')

# flat 104 boundary
ax.add_patch(patches.Rectangle((f4_x, f4_y), f4_w, f4_top - f4_y,
             linewidth=2.2, edgecolor='#111111', facecolor='none', zorder=5))

# ─────────────────────────────────────────────────────────────────────────────
# FLAT 103 — 2BHK  (1060 sqft) second from left, below passage
# ─────────────────────────────────────────────────────────────────────────────
f3_x = f4_x + f4_w
f3_w = 7.5
f3_y = bldg_y

bal3_h = ft(5)           # REVISED from 3'3" to 5'0"
room(ax, f3_x, f3_y, f3_w - ft(5), bal3_h,
     'BALCONY', "5'0\" WIDE ★", color='#E8F5E8', revised=True)
room(ax, f3_x + f3_w - ft(5), f3_y, ft(5), bal3_h,
     'UTILITY', "5'0\" WIDE", color='#F0F5FF')

room_y3 = f3_y + bal3_h
# Kitchen REVISED (reduced by 1'9")
room(ax, f3_x, room_y3, f3_w, ft(11, 6),
     'KITCHEN', "9'0\"×11'6\" ★", color='#FFF5F5', revised=True)
# Living
room(ax, f3_x, room_y3 + ft(11, 6), f3_w, ft(18, 3),
     'LIVING', "10'0\"×18'3\"", color='#FFFDE8')

# Upper portion bedrooms
top_y3 = f3_y + (f4_top - f4_y) - ft(10)
room(ax, f3_x, top_y3, ft(11, 6), ft(10),
     'M.BEDROOM', "11'6\"×10'0\"", color='#F8F0FF')
room(ax, f3_x + ft(11, 6), top_y3, f3_w - ft(11, 6), ft(10),
     'BEDROOM', "10'0\"×10'3\"", color='#F8F0FF')

room(ax, f3_x, top_y3 - ft(5, 3), f3_w, ft(5, 3),
     'A.TOILET / C.TOILET', "6'3\"×5'3\"", color='#EEF5FF')

ax.text(f3_x + f3_w/2, f3_y + (f4_top - f4_y)/2,
        'FLAT NO\n103,203,303\n403,503,603\n1060.00 SQFT',
        ha='center', va='center', fontsize=6, color='#880000', fontweight='bold')

ax.add_patch(patches.Rectangle((f3_x, f3_y), f3_w, f4_top - f4_y,
             linewidth=2.2, edgecolor='#111111', facecolor='none', zorder=5))

# ─────────────────────────────────────────────────────────────────────────────
# FLAT 102 — 2BHK  (1050 sqft) second from right, ABOVE passage
# ─────────────────────────────────────────────────────────────────────────────
f2_x = f3_x + f3_w + core_w + 0.2
f2_w = 7.3
f2_y = pass_y + pass_h
f2_top = bldg_y + bldg_h

# rooms from bottom (above passage)
room(ax, f2_x, f2_y, f2_w, ft(10, 6),
     'M.BEDROOM', "10'6\"×10'6\"", color='#F8F0FF')
room(ax, f2_x, f2_y + ft(10, 6), ft(11, 6), ft(10),
     'BEDROOM', "11'6\"×10'0\"", color='#F8F0FF')
room(ax, f2_x + ft(11, 6), f2_y + ft(10, 6), f2_w - ft(11, 6), ft(10),
     'C.TOILET', "4'0\"×7'6\"", color='#EEF5FF')

# kitchen REVISED (reduced 1'9")
room(ax, f2_x, f2_y + ft(10, 6) + ft(10), f2_w, ft(11, 6),
     'KITCHEN', "10'0\"×11'6\" ★", color='#FFF5F5', revised=True)

room(ax, f2_x, f2_y + ft(10, 6) + ft(10) + ft(11, 6), f2_w, ft(18, 6),
     'LIVING', "10'0\"×18'6\"", color='#FFFDE8')

# balcony top REVISED 5'0"
bal2_h = ft(5)
room(ax, f2_x, f2_top - bal2_h, ft(4), bal2_h, 'UTILITY', "4'0\" WIDE", color='#F0F5FF')
room(ax, f2_x + ft(4), f2_top - bal2_h, f2_w - ft(4), bal2_h,
     'BALCONY', "5'0\" WIDE ★", color='#E8F5E8', revised=True)

ax.text(f2_x + f2_w/2, f2_y + (f2_top - f2_y)/2,
        'FLAT NO\n102,202,302\n402,502,602\n1050.00 SQFT',
        ha='center', va='center', fontsize=6, color='#880000', fontweight='bold')

ax.add_patch(patches.Rectangle((f2_x, f2_y), f2_w, f2_top - f2_y,
             linewidth=2.2, edgecolor='#111111', facecolor='none', zorder=5))

# ─────────────────────────────────────────────────────────────────────────────
# FLAT 101 — 3BHK  (1420 sqft) RIGHT, ABOVE passage
# ─────────────────────────────────────────────────────────────────────────────
f1_x = f2_x + f2_w
f1_w = bldg_x + bldg_w - f1_x
f1_y = pass_y + pass_h
f1_top = bldg_y + bldg_h

# rooms from bottom up
room(ax, f1_x, f1_y, ft(10, 6), ft(11, 3),
     'M.BEDROOM', "10'6\"×11'3\"", color='#F8F0FF')
room(ax, f1_x + ft(10, 6), f1_y, f1_w - ft(10, 6), ft(11, 3),
     'BEDROOM', "11'6\"×11'3\"", color='#F8F0FF')

room(ax, f1_x, f1_y + ft(11, 3), ft(4), ft(7), 'A.TOILET', "4'0\"×7'0\"",
     color='#EEF5FF')
room(ax, f1_x + ft(4), f1_y + ft(11, 3), ft(4), ft(7), 'C.TOILET', "4'0\"×7'0\"",
     color='#EEF5FF')
room(ax, f1_x + ft(8), f1_y + ft(11, 3), ft(10, 3), ft(9),
     'CHILD ROOM', "10'3\"×9'0\"", color='#F8F0FF')

# kitchen REVISED (reduced 1'9")
room(ax, f1_x, f1_y + ft(11, 3) + ft(9), f1_w, ft(12),
     'KITCHEN', "10'0\"×12'0\" ★", color='#FFF5F5', revised=True)

room(ax, f1_x, f1_y + ft(11, 3) + ft(9) + ft(12), f1_w, ft(18),
     'LIVING', "10'9\"×18'0\"", color='#FFFDE8')

# balcony top REVISED 5'0"
bal1_h = ft(5)
room(ax, f1_x, f1_top - bal1_h, ft(4), bal1_h, 'UTILITY', "4'0\" WIDE", color='#F0F5FF')
room(ax, f1_x + ft(4), f1_top - bal1_h, f1_w - ft(4) - ft(3, 3), bal1_h,
     'BALCONY', "5'0\" WIDE ★", color='#E8F5E8', revised=True)
room(ax, f1_top - ft(3, 3), f1_top - bal1_h, ft(3, 3), bal1_h,
     'BAL', "5'0\" ★", color='#E8F5E8', revised=True)

ax.text(f1_x + f1_w/2, f1_y + (f1_top - f1_y)/2,
        'FLAT NO\n101,201,301\n401,501,601\n1420.00 SQFT',
        ha='center', va='center', fontsize=6, color='#880000', fontweight='bold')

ax.add_patch(patches.Rectangle((f1_x, f1_y), f1_w, f1_top - f1_y,
             linewidth=2.2, edgecolor='#111111', facecolor='none', zorder=5))

# ─────────────────────────────────────────────────────────────────────────────
# building outline
# ─────────────────────────────────────────────────────────────────────────────
ax.add_patch(patches.Rectangle((bldg_x, bldg_y), bldg_w, bldg_h,
             linewidth=3.0, edgecolor='#000000', facecolor='none', zorder=6))

# ─────────────────────────────────────────────────────────────────────────────
# DIMENSIONS
# ─────────────────────────────────────────────────────────────────────────────
# overall width
ax.annotate('', xy=(bldg_x + bldg_w, 25.0), xytext=(bldg_x, 25.0),
            arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.2))
ax.text(bldg_x + bldg_w/2, 25.3, '37.15 m', ha='center', va='bottom', fontsize=8)

# overall height
ax.annotate('', xy=(0.3, bldg_y + bldg_h), xytext=(0.3, bldg_y),
            arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.2))
ax.text(0.1, bldg_y + bldg_h/2, '28.38 m', ha='center', va='center',
        fontsize=8, rotation=90)

# ─────────────────────────────────────────────────────────────────────────────
# COMPASS
# ─────────────────────────────────────────────────────────────────────────────
cx, cy, cr = 34.5, 23.5, 1.0
circle = plt.Circle((cx, cy), cr, color='#DDDDDD', fill=True, zorder=7)
ax.add_patch(circle)
ax.annotate('', xy=(cx, cy + cr), xytext=(cx, cy),
            arrowprops=dict(arrowstyle='->', color='#111111', lw=2))
ax.text(cx, cy + cr + 0.1, 'N', ha='center', va='bottom', fontsize=10,
        fontweight='bold', color='#111111')
ax.text(cx + cr + 0.1, cy, 'E', ha='left', va='center', fontsize=8, color='#444444')
ax.text(cx - cr - 0.1, cy, 'W', ha='right', va='center', fontsize=8, color='#444444')
ax.text(cx, cy - cr - 0.15, 'S', ha='center', va='top', fontsize=8, color='#444444')

# ─────────────────────────────────────────────────────────────────────────────
# LEGEND
# ─────────────────────────────────────────────────────────────────────────────
leg_x, leg_y = 1.6, 23.5
ax.add_patch(patches.Rectangle((leg_x, leg_y), 0.35, 0.25,
             facecolor='#E8F5E8', edgecolor='#CC2200', linewidth=1.5))
ax.text(leg_x + 0.45, leg_y + 0.12, '★  REVISED dimension (area-neutral)',
        ha='left', va='center', fontsize=6.5, color='#CC2200')

ax.add_patch(patches.Rectangle((leg_x, leg_y - 0.45), 0.35, 0.25,
             facecolor='#D8EAD8', edgecolor='#3A7A3A', linewidth=1.0, hatch='||'))
ax.text(leg_x + 0.45, leg_y - 0.32, 'Built-in mailbox unit (1\'6\" of passage)',
        ha='left', va='center', fontsize=6.5, color='#3A7A3A')

ax.add_patch(patches.Rectangle((leg_x, leg_y - 0.9), 0.35, 0.25,
             facecolor='#E0E8F0', edgecolor='#222288', linewidth=1.5))
ax.text(leg_x + 0.45, leg_y - 0.77, 'Lift upgraded: 6\'0\"×7\'6\" (NBC compliant)',
        ha='left', va='center', fontsize=6.5, color='#222288')

# ─────────────────────────────────────────────────────────────────────────────
# REVISION NOTES BOX
# ─────────────────────────────────────────────────────────────────────────────
notes_x, notes_y = 1.6, 19.8
ax.add_patch(patches.Rectangle((notes_x, notes_y), 11, 3.3,
             facecolor='#FFFFF0', edgecolor='#888800', linewidth=1.2, zorder=7))
ax.text(notes_x + 5.5, notes_y + 3.0, 'REVISION NOTES (AREA-NEUTRAL)',
        ha='center', va='center', fontsize=7.5, fontweight='bold', color='#333300')

notes = [
    "1. Balconies widened: 3'3\" → 5'0\" (all flats). Kitchen depth reduced by 1'9\" to compensate.",
    "2. Kitchens remain CLOSED. Internal layout: L/U-shape work triangle. Chimney provision on far wall.",
    "3. Lift upgraded: 5'6\"×6'6\" → 6'0\"×7'6\" (NBC wheelchair + stretcher compliance).",
    "4. Passage: 1'6\" on one side used for built-in mailbox + parcel shelf unit.",
    "5. Bathrooms: retain size. Wall-hung WC + dual-flush + backlit mirror + exhaust fan.",
    "6. Total sellable area: 29,100 sqft UNCHANGED. Plot boundary: 37.15m×28.38m UNCHANGED.",
    "7. Vastu: verify kitchen in SE, master bed in SW, main entry from N/NE/E on revised drawings.",
]
for i, note in enumerate(notes):
    ax.text(notes_x + 0.2, notes_y + 2.65 - i * 0.35, note,
            ha='left', va='center', fontsize=5.8, color='#333333')

# ─────────────────────────────────────────────────────────────────────────────
# TITLE BLOCK
# ─────────────────────────────────────────────────────────────────────────────
tb_x, tb_y, tb_w, tb_h = 0, 0, 37.15, 3.3
ax.add_patch(patches.Rectangle((tb_x, tb_y - tb_h), tb_w, tb_h,
             facecolor='#F8F8F8', edgecolor='#333333', linewidth=1.5, zorder=8,
             clip_on=False))

ax.text(1.0, -0.3, 'OWNER: MR DYANESHWAR SATBHAI SIR', ha='left', va='top',
        fontsize=8, fontweight='bold', color='#111111', clip_on=False)
ax.text(1.0, -0.85, 'PROJECT: PROPOSED RESIDENTIAL BLDG, PLOT NO.7B, SR.NO.56, DASAK SHIWAR, NASHIK',
        ha='left', va='top', fontsize=7, color='#333333', clip_on=False)
ax.text(1.0, -1.35, 'TITLE: FLOOR PLAN (REVISED)   |   TOTAL SELABLE AREA = 29100.00 SQFT',
        ha='left', va='top', fontsize=7.5, fontweight='bold', color='#111111', clip_on=False)
ax.text(1.0, -1.85, 'SCALE = 1:100   |   DATE = 29/05/2026   |   DRN BY: ER. KIRAN   |   REV: R-1',
        ha='left', va='top', fontsize=7, color='#333333', clip_on=False)

ax.text(28.0, -0.4, 'GURU BUILDCON', ha='left', va='top', fontsize=10,
        fontweight='bold', color='#111111', clip_on=False)
ax.text(28.0, -0.9, 'BUILDING PLANNER & DESIGNER', ha='left', va='top',
        fontsize=7, color='#444444', clip_on=False)
ax.text(28.0, -1.35, 'Er. Kiran Satbhai - 7843028287', ha='left', va='top',
        fontsize=6.5, color='#444444', clip_on=False)
ax.text(28.0, -1.75, 'Er. Vinod Shinde  - 7745002561', ha='left', va='top',
        fontsize=6.5, color='#444444', clip_on=False)
ax.text(28.0, -2.2, 'Office: 02, Gopalkrushna, Dasak, Jailroad,\nNashik Road, Nashik - 422101',
        ha='left', va='top', fontsize=6, color='#666666', clip_on=False)

# ─────────────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
plt.savefig('/home/user/Tracke/floor_plan_revised.pdf', format='pdf',
            bbox_inches='tight', dpi=200, facecolor='white')
plt.savefig('/home/user/Tracke/floor_plan_revised.png', format='png',
            bbox_inches='tight', dpi=200, facecolor='white')
print("Saved: floor_plan_revised.pdf and floor_plan_revised.png")
