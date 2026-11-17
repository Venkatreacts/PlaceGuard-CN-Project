# Rebuild PlaceGuard report: real PT screenshots/outputs, results, plain diagrams, fixed configs.
import copy, re, shutil, io
from docx import Document
from docx.shared import Inches, Pt, Emu
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from PIL import Image

ROOT = "D:/SRMIST Projects/CN Case Study LLJ2/"  # local project folder; change to your path
SRC = ROOT + "04 Report/PlaceGuard_Case_Study_Report (Repaired).docx"
OUT = ROOT + "04 Report/PlaceGuard_Case_Study_Report.docx"
SS = ROOT + "06 Screenshots/"
DG = SS + "diagrams_plain/"
TO = ROOT + "02 Packet Tracer/test_outputs/"
CF = ROOT + "03 Configs/"

d = Document(SRC)
P = list(d.paragraphs)


def find(text, style=None, start=0):
    for i, p in enumerate(P[start:], start):
        if text in p.text and (style is None or p.style.name == style):
            return p
    raise KeyError(text)


def set_text(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def replace_in(p, old, new):
    assert old in p.text, (old, p.text[:80])
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return
    set_text(p, p.text.replace(old, new))


def clone_after(anchor_el, template_p, text=None):
    el = copy.deepcopy(template_p._p)
    anchor_el.addnext(el)
    np_ = Paragraph(el, template_p._parent)
    if text is not None:
        set_text(np_, text)
    return np_


def remove(p):
    p._p.getparent().remove(p._p)


def picture_para(anchor_el, files, width):
    """Centered paragraph holding one or more pictures side by side."""
    el = copy.deepcopy(PIC_TEMPLATE._p)
    for r in el.findall(qn("w:r")):
        el.remove(r)
    anchor_el.addnext(el)
    p = Paragraph(el, PIC_TEMPLATE._parent)
    for k, f in enumerate(files):
        if k:
            p.add_run("  ")
        p.add_run().add_picture(f, width=Inches(width))
    return p


def swap_image(p, path, width_in):
    blip = p._p.xpath(".//a:blip")[0]
    rid = blip.get(qn("r:embed"))
    part = d.part.related_parts[rid]
    part._blob = open(path, "rb").read()
    w, h = Image.open(path).size
    cx = int(Inches(width_in)); cy = int(cx * h / w)
    for ext in p._p.xpath(".//wp:extent") + p._p.xpath(".//a:ext"):
        ext.set("cx", str(cx)); ext.set("cy", str(cy))


PIC_TEMPLATE = find("", start=329) if False else P[329]
CODE_T = P[231]          # Courier New code line
CAP_T = find("Figure 4.1:", "Figure Caption")
BODY_T = P[227]          # justified body paragraph

# ---------------- Front matter ----------------
set_text(P[9], "Dr. Poorvadevi R"); P[9].runs[0].font.highlight_color = None
replace_in(P[13], "Batchelor Of Technology", "Bachelor of Technology")
set_text(P[15], "COMPUTER SCIENCE AND ENGINEERING WITH SPECIALIZATION IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING")
replace_in(P[23], "SRM INSTITUTION OF", "SRM INSTITUTE OF")
for c in d.tables[0]._cells:
    for cp in c.paragraphs:
        if "Poorva" in cp.text:
            set_text(cp, "Dr. Poorvadevi R")
replace_in(P[36], "students of the B.Tech programme", "students of the B.Tech programme in Computer Science and Engineering with specialization in Artificial Intelligence and Machine Learning")
replace_in(P[36], "under the guidance of our faculty in-charge", "under the guidance of Dr. Poorvadevi R, Assistant Professor, Department of Computational Intelligence")
replace_in(P[43], "our faculty in-charge for the 21CSC302J – Computer Networks course", "our faculty in-charge, Dr. Poorvadevi R, Assistant Professor, Department of Computational Intelligence,")
replace_in(P[47], "The design is validated through eight attack and failure scenarios and three additional demonstrations, showing",
           "All eight attack and failure scenarios and three additional demonstrations passed in the simulation, showing")

# ---------------- Chapter 2: drop designed "before/after" figure ----------------
replace_in(P[171], ", illustrated in Figure 2.1", "")
remove(P[172]); remove(P[173])

# ---------------- Chapter 3: plain diagrams + real topology ----------------
swap_image(P[178], DG + "fig3_1_defence_layers.png", 6.0)
swap_image(P[181], DG + "fig3_2_methodology.png", 6.2)
swap_image(P[202], SS + "PT_topology_full.png", 6.4)
set_text(P[203], "Figure 3.3: PlaceGuard topology as built in Cisco Packet Tracer 9.0.1")
swap_image(P[211], DG + "fig3_4_rbac_matrix.png", 6.0)

# ---------------- Chapter 4 ----------------
replace_in(P[214], "using both Realtime and Simulation modes", "in Realtime mode, with the evidence captured from device show commands and the PCs' desktop tools")

# 4.1 Step 11 – verification listings
s4 = open(TO + "STEP4_checks.txt", encoding="utf-8").read().splitlines()
t8 = open(TO + "T8_output.txt", encoding="utf-8").read().splitlines()


def block(lines, start_pat, n, drop=()):
    i = next(k for k, l in enumerate(lines) if start_pat in l)
    out = [l.rstrip() for l in lines[i:i + n]]
    return [l for l in out if not any(x in l for x in drop)]


vlan = block(s4, "show vlan brief", 18, drop=("fddi", "token-ring", "trnet"))
ech = ["CORE-1# show etherchannel summary", "Number of channel-groups in use: 1",
       "Number of aggregators:           1", "",
       "Group  Port-channel  Protocol    Ports",
       "------+-------------+-----------+----------------------------------",
       "1      Po1(SU)           LACP   Fa0/23(P) Fa0/24(P)"]
hsrp = [l.rstrip() for l in t8[5:16]]
ospf = block(s4, "show ip ospf neighbor", 6) + [""] + ["R-EDGE# show ip route ospf  (extract)"] + \
       [l.rstrip() for l in s4 if l.startswith(("O       10.10.10.0", "O E2"))]
dhcp = block(s4, "show ip dhcp snooping", 15)
psec = block(s4, "show port-security", 9)
fw = ["FW-DC# show access-list CAMPUS_IN"]
for l in s4:
    if l.startswith("access-list CAMPUS_IN line"):
        l = re.sub(r"\s0x[0-9a-f]+$", "", l).replace("access-list CAMPUS_IN ", "").replace(" extended", "")
        fw.append(l)

listings = [
    (vlan, "Figure 4.1: show vlan brief on ACC-STUDENT – user ports in VLAN 10, unused ports parked in VLAN 998"),
    (ech, "Figure 4.2: show etherchannel summary on CORE-1 – LACP Port-channel 1 in use (SU)"),
    (hsrp, "Figure 4.3: show standby brief on CORE-2 – Standby for all seven HSRP groups, CORE-1 active"),
    (ospf, "Figure 4.4: OSPF adjacencies on R-EDGE and routes learned from both core switches"),
    (dhcp + [""] + psec, "Figure 4.5: DHCP snooping and port security on ACC-STUDENT"),
    (fw, "Figure 4.6: CAMPUS_IN on FW-DC with hit counters – final deny matched 131 packets"),
]
anchor = P[227]._p
p = clone_after(anchor, BODY_T, "Step 11 – Verification. Before the attack tests, every layer was checked with show commands. "
                "Figures 4.1 to 4.6 are the actual console outputs captured from the devices in Packet Tracer, and Figure 4.7 "
                "shows the IoT rules stored on the registration server. One problem found here (both cores active for "
                "VLAN 60) and two found during testing were corrected and are described in Section 4.3.")
set_text(p, "Step 11 – Verification.")
p.runs[0].bold = True
r2 = p.add_run(" Before the attack tests, every layer was checked with show commands. Figures 4.1 to 4.6 are the actual console "
               "outputs captured from the devices in Packet Tracer, and Figure 4.7 shows the IoT rules stored on the registration "
               "server. One problem found here (both cores active for VLAN 60) and two found during testing were corrected and are "
               "described in Section 4.3.")
r2.bold = False; r2.font.size = p.runs[0].font.size; r2.font.name = p.runs[0].font.name
anchor = p._p
for lines, cap in listings:
    for l in lines:
        cp = clone_after(anchor, CODE_T, l if l else " ")
        for r in cp.runs:
            r.font.size = Pt(8)
        cp.paragraph_format.space_after = Pt(0); cp.paragraph_format.space_before = Pt(0); cp.paragraph_format.keep_with_next = True
        anchor = cp._p
    c = clone_after(anchor, CAP_T, cap); anchor = c._p
pp = picture_para(anchor, [SS + "B1_iot_rules.png"], 5.6); anchor = pp._p
clone_after(anchor, CAP_T, "Figure 4.7: ACCESS-GRANTED and ACCESS-DENIED conditions on the IoT registration server (IOT-SRV)")

# 4.2.2 – DMZ return-traffic lines
p258 = P[258]
assert p258.text.startswith("access-list DMZ_IN extended permit tcp host 172.16.70.10 host 172.16.50.14")
a = p258._p
for l in ["access-list DMZ_IN extended permit icmp host 172.16.70.10 any echo-reply",
          "access-list DMZ_IN extended permit tcp host 172.16.70.10 eq www any",
          "access-list DMZ_IN extended permit tcp host 172.16.70.10 eq 443 any",
          "access-list DMZ_IN extended permit tcp host 172.16.70.10 eq ftp any"]:
    a = clone_after(a, P[258], l)._p
# 4.2.4 – IPS bypass list for trusted VPN traffic
assert P[286].text == "ip ips name PG-IPS"
set_text(P[286], "ip ips name PG-IPS list 130")
a = P[285]._p
for l in ["access-list 130 deny ip 192.168.50.0 0.0.0.255 10.10.0.0 0.0.255.255",
          "access-list 130 deny ip 192.168.50.0 0.0.0.255 172.16.50.0 0.0.0.255",
          "access-list 130 permit ip any any"]:
    a = clone_after(a, P[285], l)._p

# 4.2.7 packet journey -> Figure 4.8
swap_image(P[329], DG + "fig4_1_packet_journey.png", 6.2)
set_text(P[330], "Figure 4.8: Packet journey of an offer-letter e-mail from recruiter HQ to a student")
replace_in(P[328], "Figure 4.1", "Figure 4.8")

# 4.3 challenges table
ct = d.tables[8]
for r in ct.rows:
    if r.cells[0].text.startswith("IPS placement"):
        set_text(r.cells[1].paragraphs[0], "Signature 2004 dropped HQ → campus pings inside the decrypted tunnel (seen in T7)")
        set_text(r.cells[2].paragraphs[0], "ACL 130 and ip ips name PG-IPS list 130: trusted VPN traffic skips IPS, Internet traffic is still inspected")
new_rows = [
    ("ASA checks DMZ replies against DMZ_IN", "Portal replies were dropped by the final deny, so T1 failed at first", "Permit only traffic sourced from the portal's service ports (80, 443, 21, echo-reply); the portal still cannot open new connections"),
    ("HSRP hellos blocked by IOT_IN", "Both cores became Active for VLAN 60 (split brain)", "permit udp any host 224.0.0.102 eq 1985 added at the top of IOT_IN on both cores"),
    ("Packet Tracer ASA keeps stale ARP after failover", "Campus → portal traffic did not recover when CORE-1 was powered off", "Failover measured towards an Internet host; on real hardware gratuitous ARP from the new HSRP active resolves this"),
    ("Features missing in Packet Tracer's ASA", "logging and no dhcpd commands rejected", "Removed from the ASA script; routers and switches still send syslog to LOG-NTP-SRV"),
]
last = ct.rows[-1]._tr
for vals in new_rows:
    tr = copy.deepcopy(ct.rows[-1]._tr)
    last.addnext(tr); last = tr
    from docx.table import _Row
    row = _Row(tr, ct)
    for c, v in zip(row.cells, vals):
        set_text(c.paragraphs[0], v)

# ---------------- Chapter 5 ----------------
replace_in(P[337], "Figures 5.2 to 5.9", "Figures 5.2 to 5.12")
obs = {
    "T1": "PASS – placement.srm.edu → 172.16.70.10; portal page loaded",
    "T2": "PASS – 4/4 timed out; FW-DC deny hitcnt 405 → 436",
    "T3": "PASS – student: Destination host unreachable; INT-ROOM-1: 3/4 replies",
    "T4": "PASS – STU-PC2 got 10.10.10.103, GW 10.10.10.1 from 172.16.50.10",
    "T5": "PASS – Fa0/1 err-disabled; violation count 1",
    "T6": "PASS – pings dropped; Sig:2004 alert logged; HTTP via 203.0.113.5 works",
    "T7": "PASS – mail delivered; SA QM_IDLE, esp-aes 256; encaps 7 / decaps 10",
    "T8": "PASS – 5 of 40 pings lost; CORE-2 Active for all 7 groups",
    "B1": "PASS – 1001: Valid, Unlocked; 2002: Invalid, Locked, siren on",
    "B2": "PASS – student: connection timed out; admin: CORE-1> via TACACS+",
    "B3": "PASS – 4/4 timed out at the ZBF",
}
for r in d.tables[9].rows[1:]:
    k = r.cells[0].text.strip()
    set_text(r.cells[4].paragraphs[0], obs[k])
    if k == "T7":
        set_text(r.cells[2].paragraphs[0], "HQ-HR-PC mails student1; IPsec SA counters checked on R-EDGE")
        set_text(r.cells[3].paragraphs[0], "Mail delivered; tunnel up with ESP AES-256; encaps/decaps counters increase")
    if k == "T8":
        set_text(r.cells[2].paragraphs[0], "STU-PC1 sends 40 pings to 45.10.20.10; CORE-1 powered off mid-test")

set_text(P[342], "All eleven tests passed in Cisco Packet Tracer 9.0.1 on 13–14 November 2026. "
         "Figures 5.2 to 5.12 are screenshots taken directly from the simulation.")

shots = {
    "Figure 5.2:": ([SS + "T1.png"], 4.2, None),
    "Figure 5.3:": ([SS + "T2.png"], 4.2, None),
    "Figure 5.4:": ([SS + "T3.png"], 4.2, None),
    "Figure 5.5:": ([SS + "T4.png"], 4.2, None),
    "Figure 5.6:": ([SS + "T5.png"], 4.2, None),
    "Figure 5.7:": ([SS + "T6.png", SS + "T6_ips_log.png"], 2.8, "Figure 5.7: T6 – ICMP flood from the Internet (left: ATTACKER-PC; right: IPS alert on R-EDGE)"),
    "Figure 5.8:": ([SS + "T7.png", SS + "T7_vpn.png"], 2.8, "Figure 5.8: T7 – Offer letter over the VPN (left: STU-PC1 inbox; right: IPsec SA on R-EDGE)"),
    "Figure 5.9:": ([SS + "T8.png"], 4.2, "Figure 5.9: T8 – Core switch failure: five pings lost, then replies via CORE-2"),
}
body = d.element.body
for key, (files, w, newcap) in shots.items():
    cap = find(key, "Figure Caption")
    tbl = cap._p.getprevious()
    assert tbl.tag == qn("w:tbl") and "Insert Packet Tracer" in tbl.xpath("string(.)")
    pic = picture_para(tbl, files, w)
    body.remove(tbl)
    if newcap:
        set_text(cap, newcap)
anchor = find("Figure 5.9:", "Figure Caption")._p
for files, w, cap in [
    ([SS + "B1_card1001_granted.png", SS + "B1_card2002_denied.png"], 2.8, "Figure 5.10: B1 – Smart interview hall (left: card 1001 granted; right: card 2002 denied, siren on)"),
    ([SS + "B2_student_blocked.png", SS + "B2.png"], 2.8, "Figure 5.11: B2 – Management access (left: student SSH timed out; right: NETADMIN-PC via TACACS+)"),
    ([SS + "B3.png"], 4.2, "Figure 5.12: B3 – Campus cannot open sessions into the recruiter LAN (zone-based firewall)"),
]:
    pp = picture_para(anchor, files, w)
    c = clone_after(pp._p, CAP_T, cap); anchor = c._p

swap_image(P[338], DG + "fig5_1_threat_matrix.png", 6.0)

set_text(P[354], "The VPN test shows that the tunnel between 203.0.113.2 and 198.51.100.2 reached QM_IDLE with esp-aes 256 "
         "esp-sha-hmac, and the encapsulation and decapsulation counters rose with every message, so the ISP only carries ESP "
         "packets and shortlists and offer letters cannot be read in transit. The zone-based firewall at the recruiter site adds "
         "a property often missing in partner VPNs: the tunnel is not a two-way open door, because the campus cannot initiate "
         "sessions into the company's LAN (B3). Finally, the failover test demonstrates availability: when CORE-1 was powered "
         "off during a 40-ping run, five pings were lost and replies resumed through CORE-2, which became Active for all seven "
         "HSRP groups; with pre-emption, CORE-1 takes the role back when it returns.")
set_text(P[355], "Testing also exposed limits of the simulator and three design errors. Packet Tracer's ASA has no logging "
         "command and checks DMZ replies against the DMZ_IN ACL, which made the first T1 run fail until return traffic from "
         "the portal's service ports was permitted. After failover the simulated ASA kept its ARP entries pointing at CORE-1, so "
         "campus-to-portal traffic did not recover in Packet Tracer even though HSRP moved correctly; T8 was therefore measured "
         "towards an Internet host. The IoT ACL initially blocked HSRP hellos, and the inline IPS dropped trusted pings inside "
         "the VPN; both were fixed (Section 4.3). Simulation-mode packet captures were not used; encryption was proven with the "
         "IPsec SA counters. Timing values in Packet Tracer are indicative and not equal to real hardware.")
replace_in(P[366], "Each control was validated by a dedicated attack or failure scenario, showing",
           "Each control was validated by a dedicated attack or failure scenario, and all eleven tests passed in Packet Tracer, showing")

# ---------------- Appendix B: replace config blocks with the final files ----------------
heads = [p for p in d.paragraphs if p.style.name == "Heading 1" and p.text.startswith("APPENDIX B")]
for h in heads:
    fname = {"R-EDGE": "02_R-EDGE.txt", "CORE-1": "04_CORE-1.txt", "FW-DC": "12_FW-DC_ASA.txt"}.get(
        next((k for k in ("R-EDGE", "CORE-1", "FW-DC") if h.text.endswith(k) or k + " " in h.text), None))
    if not fname:
        continue
    new = open(CF + fname, encoding="utf-8").read().rstrip("\n").splitlines()
    paras = []
    el = h._p.getnext()
    while el is not None and not (el.tag == qn("w:p") and el.xpath("string(.)").startswith("APPENDIX")):
        paras.append(el); el = el.getnext()
    # keep the trailing empty paragraphs (page layout); replace the code lines
    code = [e for e in paras if e.tag == qn("w:p")]
    while code and not code[-1].xpath("string(.)").strip():
        code.pop()
    tmpl = Paragraph(copy.deepcopy(code[1]), h._parent)
    anchor_el = code[0].getprevious()
    for e in code:
        e.getparent().remove(e)
    a = anchor_el
    for l in new:
        np_ = copy.deepcopy(tmpl._p); a.addnext(np_); a = np_
        q = Paragraph(np_, h._parent)
        if q.runs:
            set_text(q, l)
        else:
            q.add_run(l)

d.save(OUT)
print("saved", OUT)
