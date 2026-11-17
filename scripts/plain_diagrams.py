# Plain black-and-white report diagrams (textbook / Visio style).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import sys, os

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Arial", "font.size": 10})
GREY = "#E6E6E6"


def box(ax, x, y, w, h, text, fill="white", bold=False, fs=10, lw=1.0):
    ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec="black", lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                                 color="black", lw=1.0))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- Fig 3.1 defence in depth ----
layers = [
    ("7  Availability", "HSRP v2 failover, LACP EtherChannel, Rapid-PVST, dual-homed access"),
    ("6  Management & audit", "TACACS+ AAA with local fallback, SSH v2 only, VTY ACL 15, syslog and NTP"),
    ("5  Transport encryption", "Site-to-site IPsec VPN: IKE AES-256 / SHA / DH group 5, ESP AES-256"),
    ("4  Perimeter", "ASA 5506-X with DMZ, IOS IPS (signature 2004), zone-based firewall, NAT/PAT"),
    ("3  Segmentation & RBAC", "7 VLANs, inbound ACLs on core SVIs, native VLAN 999, parked ports (VLAN 998)"),
    ("2  Layer-2 edge", "Port security (sticky, 1 MAC), DHCP snooping, BPDU guard, PortFast"),
    ("1  Physical / IoT", "RFID reader, smart door and siren in the interview hall, isolated IoT VLAN 60"),
]
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.set_xlim(0, 100); ax.set_ylim(0, 75); ax.axis("off")
for i, (name, desc) in enumerate(layers):
    y = 66 - i * 9.5
    box(ax, 0, y, 27, 8, name, fill=GREY, bold=True, fs=10)
    box(ax, 27, y, 73, 8, desc, fs=9.5)
ax.text(50, -1.5, "Traffic from an untrusted source must pass every layer below its target asset.",
        ha="center", fontsize=9, style="italic")
save(fig, "fig3_1_defence_layers.png")

# ---- Fig 3.2 methodology ----
phases = [
    ("1. Requirement\nanalysis", "Actors, assets,\nthreats"),
    ("2. Network\ndesign", "2 sites, 7 VLANs,\nIP plan, zones"),
    ("3. Core\nimplementation", "VLANs, trunks, HSRP,\nEtherChannel, OSPF"),
    ("4. Security\nhardening", "ACLs, ASA, IPS,\nIPsec, ZBF, AAA"),
    ("5. Services\n& IoT", "DNS, DHCP, mail,\nportal, RFID hall"),
    ("6. Attack &\nfailure testing", "T1-T8 and\nB1-B3"),
    ("7. Evaluation\n& report", "Results, fixes,\nreport, demo"),
]
fig, ax = plt.subplots(figsize=(11, 3.2))
ax.set_xlim(0, 140); ax.set_ylim(0, 40); ax.axis("off")
for i, (p, d) in enumerate(phases):
    x = i * 20
    box(ax, x, 20, 16, 13, p, fill=GREY, bold=True, fs=8.5)
    ax.text(x + 8, 16, d, ha="center", va="top", fontsize=8)
    if i < len(phases) - 1:
        arrow(ax, x + 16, 26.5, x + 20, 26.5)
ax.plot([0, 96], [36, 36], color="black", lw=0.8); ax.text(48, 37, "Review 1: design and implementation", ha="center", fontsize=8.5)
ax.plot([100, 136], [36, 36], color="black", lw=0.8); ax.text(118, 37, "Review 2: testing and evaluation", ha="center", fontsize=8.5)
save(fig, "fig3_2_methodology.png")

# ---- Fig 3.4 RBAC matrix ----
cols = ["Placement\nportal", "Resume\nFTP", "E-mail", "Student\nrecords DB", "Other campus\nVLANs", "Internet", "Device\nCLI (SSH)"]
rows = [
    ("Students (VLAN 10)", "AAAAXAX".replace("X", "N")),
    ("Placement cell (VLAN 20)", "AAAAAAN"),
    ("Interview rooms (VLAN 30)", "ANANPAN"),
    ("Recruiter Wi-Fi (VLAN 40)", "ANANPAN"),
    ("Recruiter HQ (IPsec VPN)", "ANANPAN"),
    ("IoT devices (VLAN 60)", "NNNNNNN"),
    ("Network admin (VLAN 99)", "AAAAAAA"),
    ("Internet (public)", "ANNNN-N"),
]
rows[0] = ("Students (VLAN 10)", "AAANNAN")
sym = {"A": "Yes", "N": "No", "P": "Partial*", "-": "-"}
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.axis("off")
cell = [[sym[c] for c in r[1]] for r in rows]
t = ax.table(cellText=cell, rowLabels=[r[0] for r in rows], colLabels=cols, loc="center", cellLoc="center")
t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 2.0)
for (r, c), cl in t.get_celld().items():
    cl.set_edgecolor("black"); cl.set_linewidth(0.6)
    if r == 0 or c == -1:
        cl.set_facecolor(GREY); cl.set_text_props(fontweight="bold")
    elif cl.get_text().get_text() == "No":
        cl.set_facecolor("#F4F4F4")
ax.text(0.5, -0.02, "* Partial: interview rooms only. IoT devices may only reply to the placement cell and admins; they never start a connection.",
        ha="center", transform=ax.transAxes, fontsize=8.5, style="italic")
save(fig, "fig3_4_rbac_matrix.png")

# ---- Fig 4.1 packet journey ----
hops = [
    ("HQ-HR-PC", "Sends offer-letter\nmail to student1"),
    ("R-RECRUITER", "ZBF inspects,\nVPN ACL 110 matches,\nESP AES-256"),
    ("ISP", "Sees only ESP\n198.51.100.2 to\n203.0.113.2"),
    ("R-EDGE", "Decrypts, IPS bypass\nlist 130, NAT\nexempt (ACL 120)"),
    ("CORE-1", "HSRP active\ngateway, routes to\nFW-DC"),
    ("FW-DC (ASA)", "CAMPUS_IN permits\nTCP 25 from\n192.168.50.0/24"),
    ("MAIL-SRV", "Stores mail;\nSTU-PC1 reads\nit over POP3"),
]
fig, ax = plt.subplots(figsize=(11, 2.8))
ax.set_xlim(0, 140); ax.set_ylim(0, 30); ax.axis("off")
for i, (h, d) in enumerate(hops):
    x = i * 20
    box(ax, x, 18, 15, 8, h, fill=GREY, bold=True, fs=8.5)
    ax.text(x + 7.5, 15.5, d, ha="center", va="top", fontsize=7.8)
    if i < len(hops) - 1:
        arrow(ax, x + 15, 22, x + 20, 22)
ax.add_patch(Rectangle((19, 16.5), 57, 11, fill=False, ec="black", lw=0.8, ls="--"))
ax.text(47.5, 28.3, "IPsec tunnel (encrypted)", ha="center", fontsize=8.5)
save(fig, "fig4_1_packet_journey.png")

# ---- Fig 5.1 threat-control-test ----
tm = [
    ("Unauthorised access to student records", "ASA CAMPUS_IN + core SVI ACLs", "FW-DC, CORE-1/2", "T2"),
    ("Recruiter guest reaching student devices", "VLAN 40 + WIFI_IN ACL", "CORE-1/2", "T3"),
    ("Rogue DHCP server (man-in-the-middle)", "DHCP snooping, trusted uplinks", "Access switches", "T4"),
    ("Unknown device plugged into a port", "Port security, sticky MAC, shutdown", "Access switches", "T5"),
    ("ICMP flood / reconnaissance from Internet", "IOS IPS signature 2004, deny inline", "R-EDGE", "T6"),
    ("Sniffing recruiter-campus traffic", "IPsec AES-256 site-to-site VPN", "R-EDGE, R-RECRUITER", "T7"),
    ("Core switch or link failure", "HSRP, EtherChannel, Rapid-PVST", "CORE-1/2", "T8"),
    ("Tailgating into the interview hall", "RFID reader, door lock, siren", "IoT VLAN 60", "B1"),
    ("Credential theft / Telnet sniffing", "SSH v2, TACACS+, VTY ACL", "All network devices", "B2"),
    ("Campus probing the recruiter LAN", "Zone-based policy firewall", "R-RECRUITER", "B3"),
]
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.axis("off")
t = ax.table(cellText=[list(r) for r in tm], colLabels=["Threat", "Control", "Where", "Test"],
             loc="center", cellLoc="left", colWidths=[0.36, 0.33, 0.21, 0.07])
t.auto_set_font_size(False); t.set_fontsize(8.8); t.scale(1, 1.75)
for (r, c), cl in t.get_celld().items():
    cl.set_edgecolor("black"); cl.set_linewidth(0.6)
    if c == 3: cl.get_text().set_horizontalalignment("center")
    if r == 0:
        cl.set_facecolor(GREY); cl.set_text_props(fontweight="bold")
save(fig, "fig5_1_threat_matrix.png")
print("ok")
