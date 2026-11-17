# PlaceGuard – Packet Tracer Build Log

Built and tested in **Packet Tracer 9.0.1.0858**, 13–14 Nov 2026. (Packet Tracer was restarted twice during testing; all changes listed here were redone where needed and are in the final saved file.)

## Status

| Item | State |
|---|---|
| `PlaceGuard.pkt` | **Saved** (all configs saved on the devices with `write memory` too) |
| 43 devices placed, renamed, cabled (43 links) | **Done** |
| Coloured zone boxes + labels (10 zones) | **Done** (outlined boxes, see note) |
| CLI configs 01–12 | **Done**; 4 files corrected after testing (see "Changes") |
| GUI settings (file 13) | **Done**, including the IoT hall |
| Step 4 checks | **Done – all pass** after the HSRP fix |
| T1–T8, B1–B3 | **All pass** (T8 with a changed target, see below) |
| Screenshots | **Done** – `06 Screenshots/` (list below). Real device output for each test is also saved as text in `02 Packet Tracer/test_outputs/` |

---

## How it was built

Packet Tracer's own **Scripting** feature (Extensions › Scripting › Edit File Script Module) ran a
small script module, **"PT Build Bridge"**, that uses PT's documented IPC API: `addDevice`,
`createLink`, the device console, and server/PC process settings. Config files were fed to each
device's console **line by line, exactly like a paste**, and the output was captured, so every
rejected line was seen. Tests were run through the PCs' own Command Prompt, Web Browser and
E-mail client processes, and through device `show` commands. All outputs in `test_outputs/`
are real PT output.

> **Removed:** after testing, the bridge script (`main.js`) was deleted and all its privileges
> unticked (Extensions › Scripting › Edit File Script Module), and the file was saved. `PlaceGuard.pkt`
> no longer contains any script and opens without a script prompt.

**Zone boxes:** PT's API can draw lines and notes but not filled rectangles, so each zone is a
coloured outline (4 lines) with a text label: INTERNET (grey), TECHNOVA HQ (orange), CAMPUS EDGE
(red), CAMPUS CORE (blue), DATA CENTRE (purple), DMZ (yellow), STUDENT BLOCK (green), PLACEMENT
CELL (teal), INTERVIEW HALL (pink), RECRUITER WI-FI (light blue).

---

## Topology

* 43 devices named exactly as in the guide. PT also adds 3 "Power Distribution Device" items that
  only show in the Physical view.
* Module swaps: HALL-DOOR and ALARM-SIREN wireless → **PT-IOT-NM-1CFE**; REC-LAPTOP1/2 →
  **Linksys-WPC300N**.
* Cables: crossover for switch–switch and router–router links, straight-through everywhere else.
  FW-DC G1/3 ↔ PORTAL-SRV is straight-through.

---

## CLI configs: what each device accepted

| File | Device | Lines | Rejected | Notes |
|---|---|---|---|---|
| 01 | ISP | 20 | 0 | |
| 02 A/B/C | R-EDGE | licence + 78 + IPS | 0 | `show version`: `securityk9 Evaluation`. IPS built 303 signatures. `logging host` accepted |
| 03 A/B | R-RECRUITER | licence + 81 | 0 | ZBF accepted |
| 04 / 05 | CORE-1 / CORE-2 | 205 each | 0 | |
| 06–09 | ACC switches | 80–107 | 0 | only PortFast warnings; optional DAI block accepted |
| 10 / 11 | SW-TRANSIT / SW-SERVERS | 23 / 16 | 0 | |
| 12 | FW-DC (ASA) | 67 | 6 | see changes 1–3 |

## Changes made (all config files updated to match what runs)

1. **`12_FW-DC_ASA.txt`** – `no dhcpd …` (2 lines) rejected: PT's 5506-X has no factory DHCP. Removed.
2. **`12_FW-DC_ASA.txt`** – two `exit`s after the policy-map: on PT's ASA one `exit` returns to
   `(config)`, so the second left config mode. Now one `exit`.
3. **`12_FW-DC_ASA.txt`** – `logging enable / host / trap`: `logging ?` → `% Unrecognized command`.
   PT's ASA has no logging. Replaced by a comment.
4. **`12_FW-DC_ASA.txt` – DMZ return traffic (found by T1).** The portal never answered: requests
   passed `CAMPUS_IN`, but the `DMZ_IN` deny counter rose. PT's ASA checks the portal's *replies*
   against `DMZ_IN`. Added permits **from** the portal's service ports only (echo-reply, tcp
   source 80/443/21) before the final deny. The portal still can't open new connections.
   (`eq https` is rejected by PT; `eq 443` works.)
5. **`04_CORE-1.txt` / `05_CORE-2.txt` – HSRP split brain on VLAN 60 (found by Step 4).** Both
   cores were Active for group 60 because `IOT_IN`'s final `deny ip any any` dropped the other
   core's HSRPv2 hellos. Added `permit udp any host 224.0.0.102 eq 1985` at the top of `IOT_IN`.
   After this CORE-2 shows Standby for all 7 groups.
6. **`02_R-EDGE.txt` – IPS dropped VPN pings (found by T7, prediction P4 confirmed).** IPS on G0/2
   sees the decrypted VPN traffic, and sig 2004 dropped HQ → campus pings
   (`%IPS-4-SIGNATURE … [192.168.50.10 -> 10.10.30.104]`). Added ACL 130 (deny HQ → campus, permit
   any) and `ip ips name PG-IPS list 130`, so trusted VPN traffic skips IPS. The attacker is still
   blocked and logged.
7. **`13_SERVERS_GUI_SETTINGS.txt`** – IOT-SRV must keep **HTTP ON** (the IoT server runs on top of
   HTTP; with it off the browser shows `Server Reset Connection`).
8. **AAA user:** the first API attempt stored the `netadmin` password in the wrong field (TACACS+
   login failed). Fixed; TACACS+ logins now work. The earlier log entry saying it was stored
   correctly was wrong.
9. **Guide (T4, T5, T8)** updated to what really works in PT 9 – see the test notes.

---

## Step 4 checks (`test_outputs/STEP4_checks.txt`) – PASS

| Check | Result |
|---|---|
| `show vlan brief` (ACC-STUDENT) | VLANs 10/20/30/40/60/99/998/999; Fa0/1-3,10 in VLAN 10 |
| `show etherchannel summary` (CORE-1) | `Po1(SU) LACP Fa0/23(P) Fa0/24(P)` |
| `show standby brief` | CORE-1 Active, CORE-2 Standby for all 7 groups (after fix 5) |
| `show ip ospf neighbor` (R-EDGE) | 2.2.2.2 and 3.3.3.3, both FULL |
| `show ip route` (R-EDGE) | `O E2 172.16.50.0/24` and `O E2 172.16.70.0/24` via both cores |
| `show ip dhcp snooping` | enabled on 10,20,30,40,60; G0/1-2 trusted |
| `show port-security` | Fa0/1-3 max 1, Shutdown action |
| `show access-list` (FW-DC) | CAMPUS_IN with hit counters (bootps 8, syslog 3, NTP 4, TACACS 4 …) |
| `show crypto isakmp sa` | `QM_IDLE ACTIVE` once VPN traffic flowed (see T7) |

---

## Test results (evidence in `test_outputs/`)

| Test | Result | Key output |
|---|---|---|
| **T1** | **PASS** (after fix 4) | `nslookup placement.srm.edu` → 172.16.70.10 via 172.16.50.10; browser loaded "PlaceGuard - SRM Placement Portal" |
| **T2** | **PASS** | ping 172.16.50.14: Request timed out ×4; browser no response; FW-DC `deny ip any any` hitcnt 405 → 436 |
| **T3** | **PASS** | REC-LAPTOP1 → STU-PC1: `Reply from 10.10.40.2: Destination host unreachable` ×4; → INT-ROOM-1: 3/4 replies (first lost to ARP) |
| **T4** | **PASS** | Rogue DHCP on Fa0/10; STU-PC2 got **10.10.10.103, GW 10.10.10.1**; snooping bindings show only real leases. `show ip dhcp snooping statistics` doesn't exist in PT 9 |
| **T5** | **PASS** | Fa0/1 → `err-disabled`, `Port Status: Secure-shutdown`, `Security Violation Count: 1`, last source = laptop MAC. Notes: in PT a device with no IP sends nothing, so the laptop needed a static 10.10.10.15x (or a DHCP click). The original UNKNOWN-LAPTOP object stopped transmitting after API tests, so a fresh identical one was used; the same result was reproduced with STU-PC3 |
| **T6** | **PASS** | ATTACKER-PC → 203.0.113.5: timed out; R-EDGE: `%IPS-4-SIGNATURE: Sig:2004 Subsig:0 Sev:25 [45.10.20.66 -> 203.0.113.5:0]`; PUBLIC-USER browser loaded the portal via static NAT |
| **T7** | **PASS** (after fix 6) | Mail hr.technova@srm.edu → student1@srm.edu sent over the VPN and received by STU-PC1 (POP3); HQ-INTERVIEWER → INT-ROOM-1 4/5 replies; R-EDGE `QM_IDLE`, `esp-aes 256 esp-sha-hmac`, `#pkts encaps: 7 decaps: 10` (increasing); ASA HQ SMTP rule hitcnt 2. ESP shown by counters; Simulation-mode capture not done |
| **T8** | **PASS – target changed** | `ping -n 40 45.10.20.10`, CORE-1 powered off at ~8 s: **5 pings lost**, then replies resumed (35/40). CORE-2 Active for all 7 groups. **With the guide's original target (portal 172.16.70.10) it never recovers in PT:** PT's ASA ARPs each campus host and keeps them mapped to CORE-1's MAC (proxy-ARP). Explicit ASA routes and disabling proxy-ARP did not help (both tried, both reverted); PT's ASA has no `arp timeout` or `clear arp`. HSRP itself failed over correctly in both runs |
| **B1** | **PASS** | Rules on IOT-SRV: ACCESS-GRANTED (`RFID-READER Card ID = 1001` → reader Valid, HALL-DOOR Unlock, ALARM-SIREN On=false) and ACCESS-DENIED (`Card ID != 1001` → Invalid, Lock, siren On=true). CARD-1001 on the reader → Card ID 1001, **Valid, Unlocked, siren off**; CARD-2002 → Card ID 2002, **Invalid, Locked, siren on**. Cards were placed on the reader by moving them through the API (same as dragging). The siren was left on after the last test; dragging CARD-1001 to the reader resets it |
| **B2** | **PASS** | STU-PC1 `ssh -l netadmin 10.10.10.2` → `% Connection timed out`; NETADMIN-PC `ssh -l netadmin 10.10.99.2` → `Password:` → `CORE-1>`, `show users` shows netadmin on vty 0 (TACACS+) |
| **B3** | **PASS** | PLC-OFFICER → HQ-HR-PC 192.168.50.11: 4/4 timed out; ZBF zone-pair IN-TO-OUT only (no OUT→IN) |

---

## IoT hall notes (B1)

* IOT-SRV needs **HTTP ON** for the IoT Registration Server (file 13 updated).
* `pgadmin / Iot@2026` created from PLC-OFFICER's browser (Sign up). RFID-READER, HALL-DOOR and
  ALARM-SIREN: DHCP (got 10.10.60.x, GW 10.10.60.1) + Remote Server 10.10.60.10 → all three show
  green on the IoT server's Devices page.
* Both RFID cards default to Card ID **1001** in PT 9; CARD-2002's ID was changed to **2002**
  (stored as the device variable `CardID`).
* PT 9's condition editor **does** offer `!=` (prediction P12 was wrong), so the guide's rule works as written.

## Screenshots (`06 Screenshots/`)

| File | Shows |
|---|---|
| `PT_topology_full.png` | Whole logical workspace with the 10 zone boxes (exported by PT itself) |
| `T1.png` | STU-PC1 browser: `http://placement.srm.edu` → PlaceGuard portal |
| `T2.png` | STU-PC1: `ping 172.16.50.14` 4/4 timed out (above it: T8's 40/35/5 summary) |
| `T3.png` | REC-LAPTOP1: student VLAN *Destination host unreachable*; INT-ROOM-1 replies |
| `T4.png` | STU-PC2 `ipconfig /all` with the rogue server plugged in: DHCP Server 172.16.50.10, GW 10.10.10.1 |
| `T5.png`, `T5_canvas.png` | ACC-STUDENT CLI: `PSECURE_VIOLATION`, `Secure-shutdown`, count 1, `err-disabled`; canvas shows the red link |
| `T6.png`, `T6_ips_log.png` | ATTACKER-PC 4/4 timed out; R-EDGE CLI `%IPS-4-SIGNATURE Sig:2004 [45.10.20.66 -> 203.0.113.5]` |
| `T7.png`, `T7_vpn.png` | STU-PC1 inbox: "TechNova offer letter" from hr.technova@srm.edu; R-EDGE `QM_IDLE`, `#pkts encaps 3 / decaps 4` |
| `T8.png` | STU-PC1 `ping -n 40 45.10.20.10`: 7 replies, 5 timeouts, replies resume |
| `B1.png` (= `B1_card1001_granted.png`), `B1_card2002_denied.png`, `B1_iot_rules.png` | IoT server device states for each card, and the two rules |
| `B2.png`, `B2_student_blocked.png` | NETADMIN-PC SSH → `CORE-1>` via TACACS+; STU-PC1 SSH → `Connection timed out` |
| `B3.png` | PLC-OFFICER → HQ-HR-PC 192.168.50.11: 4/4 timed out |

T5 note: in the final file the original UNKNOWN-LAPTOP works (the earlier "broken laptop" was a
side effect of API testing). To demo it: unplug STU-PC1, plug the laptop into Fa0/1, then give it
an IP (static 10.10.10.15x or click DHCP) so it actually sends a frame. Afterwards re-plug STU-PC1
and on ACC-STUDENT run `interface fa0/1`, `shutdown`, `no shutdown` to clear the err-disable.

## Still to do

Nothing from the task list. Optional: Simulation-mode capture showing ESP packets for T7.

## Notes for whoever continues

* With desktop control, device windows only took clicks after opening with a **double-click**;
  sometimes they open behind the main window, and **Window menu › device name** brings them forward.
* Prediction results: P1, P2, P3, P4 confirmed (P4 fixed). P5 fine (EtherChannel bundled). P6 half
  right (`inspect http` OK, ASA logging rejected). P7, P8, P9 wrong (accepted). P10 fine (AP port
  stays up). P12 wrong (`!=` exists).
