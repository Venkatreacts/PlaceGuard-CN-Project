# PlaceGuard: Packet Tracer Build and Demo Guide
**Packet Tracer 9.0.1** · Save the file as `D:\CN Case Study LLJ2\02 Packet Tracer\PlaceGuard.pkt`

All configurations are in `..\03 Configs\`. To configure a device, open it, go to the **CLI** tab, answer `no` to the setup dialog, then copy and paste the whole file.

---

## Step 1: Place the devices (≈45 devices)
Use **Edit › Rename** (or click the label) to name each device exactly as shown.

| Area (draw a coloured rectangle + label with the Note tool) | Device to drag in | Names |
|---|---|---|
| **INTERNET** (grey) | Router 2911 | `ISP` |
| | Switch 2960-24TT | `SW-INTERNET` |
| | PC ×2 | `PUBLIC-USER`, `ATTACKER-PC` |
| **TECHNOVA RECRUITER HQ** (orange) | Router 2911 | `R-RECRUITER` |
| | Switch 2960-24TT | `SW-HQ` |
| | PC ×2 | `HQ-HR-PC`, `HQ-INTERVIEWER` |
| **CAMPUS EDGE** (red) | Router 2911 | `R-EDGE` |
| **CAMPUS CORE** (blue) | Multilayer Switch 3560-24PS ×2 | `CORE-1`, `CORE-2` |
| **DATA CENTRE** (purple) | Security › ASA 5506-X | `FW-DC` |
| | Switch 2960-24TT ×2 | `SW-TRANSIT`, `SW-SERVERS` |
| | Server ×5 | `DHCP-DNS-SRV`, `AAA-SRV`, `LOG-NTP-SRV`, `MAIL-SRV`, `DB-SRV` |
| **DMZ** (yellow) | Server | `PORTAL-SRV` |
| **STUDENT BLOCK** (green) | Switch 2960-24TT | `ACC-STUDENT` |
| | PC ×3, Laptop ×1, Server ×1 | `STU-PC1..3`, `UNKNOWN-LAPTOP`, `ROGUE-DHCP` |
| **PLACEMENT CELL** (teal) | Switch 2960-24TT | `ACC-PLACEMENT` |
| | PC ×3 | `PLC-OFFICER`, `PLC-COORD`, `NETADMIN-PC` |
| **INTERVIEW HALL** (pink) | Switch 2960-24TT | `ACC-INTERVIEW` |
| | PC ×2, Server ×1 | `INT-ROOM-1`, `INT-ROOM-2`, `IOT-SRV` |
| | RFID Reader, Door, Siren, RFID Card ×2 | `RFID-READER`, `HALL-DOOR`, `ALARM-SIREN`, `CARD-1001`, `CARD-2002` |
| **RECRUITER WI-FI** (light blue) | Switch 2960-24TT, AccessPoint-PT, Laptop ×2 | `ACC-WIFI`, `AP-RECRUITER`, `REC-LAPTOP1`, `REC-LAPTOP2` |

## Step 2: Cabling
Use **Copper Straight-Through** cables everywhere. Packet Tracer auto-corrects them, and the wireless laptops need no cable.

| From | Port | To | Port |
|---|---|---|---|
| ISP | G0/0 | R-EDGE | G0/2 |
| ISP | G0/1 | R-RECRUITER | G0/0 |
| ISP | G0/2 | SW-INTERNET | G0/1 |
| SW-INTERNET | Fa0/1, Fa0/2 | PUBLIC-USER, ATTACKER-PC | Fa0 |
| R-RECRUITER | G0/1 | SW-HQ | G0/1 |
| SW-HQ | Fa0/1, Fa0/2 | HQ-HR-PC, HQ-INTERVIEWER | Fa0 |
| R-EDGE | G0/0 | CORE-1 | G0/1 |
| R-EDGE | G0/1 | CORE-2 | G0/1 |
| CORE-1 | Fa0/23 | CORE-2 | Fa0/23 |
| CORE-1 | Fa0/24 | CORE-2 | Fa0/24 |
| CORE-1 / CORE-2 | Fa0/1 | ACC-STUDENT | G0/1 / G0/2 |
| CORE-1 / CORE-2 | Fa0/2 | ACC-PLACEMENT | G0/1 / G0/2 |
| CORE-1 / CORE-2 | Fa0/3 | ACC-INTERVIEW | G0/1 / G0/2 |
| CORE-1 / CORE-2 | Fa0/4 | ACC-WIFI | G0/1 / G0/2 |
| CORE-1 / CORE-2 | Fa0/5 | SW-TRANSIT | Fa0/2 / Fa0/3 |
| SW-TRANSIT | Fa0/1 | FW-DC | G1/1 |
| FW-DC | G1/2 | SW-SERVERS | Fa0/1 |
| SW-SERVERS | Fa0/2 … Fa0/6 | DHCP-DNS, AAA, LOG-NTP, MAIL, DB servers | Fa0 |
| FW-DC | G1/3 | PORTAL-SRV | Fa0 |
| ACC-STUDENT | Fa0/1, Fa0/2, Fa0/3 | STU-PC1, 2, 3 | Fa0 |
| ACC-PLACEMENT | Fa0/1, Fa0/2, Fa0/5 | PLC-OFFICER, PLC-COORD, NETADMIN-PC | Fa0 |
| ACC-INTERVIEW | Fa0/1, Fa0/2, Fa0/10 | INT-ROOM-1, INT-ROOM-2, IOT-SRV | Fa0 |
| ACC-INTERVIEW | Fa0/11, 12, 13 | RFID-READER, HALL-DOOR, ALARM-SIREN | Fa0 |
| ACC-WIFI | Fa0/1 | AP-RECRUITER | Port 0 |

> Leave **ROGUE-DHCP** and **UNKNOWN-LAPTOP** uncabled. They are only plugged in during the demo.

## Step 3: Configuration order (important)
1. `01_ISP.txt`
2. `02_R-EDGE.txt`: **Part A** (enables the security licence and reloads), then **Part B**, then **Part C** (IPS).
3. `03_R-RECRUITER.txt`: Part A (reload), then Part B.
4. `04_CORE-1.txt`, `05_CORE-2.txt`
5. `06`…`09` access switches, `10_SW-TRANSIT.txt`, `11_SW-SERVERS.txt`
6. `12_FW-DC_ASA.txt`
7. Servers, PCs, wireless and IoT: follow `13_SERVERS_GUI_SETTINGS.txt`
8. On every DHCP PC, go to **Desktop › IP Configuration** and click **DHCP** again to renew the lease.
9. Press **Fast Forward Time** a few times so STP, OSPF and HSRP converge, then save.

## Step 4: Check that everything is up
| Command (device) | You should see |
|---|---|
| `show vlan brief` (any ACC switch) | VLANs 10/20/30/40/60/99 with ports assigned |
| `show etherchannel summary` (CORE-1) | `Po1(SU)` with `Fa0/23(P) Fa0/24(P)` |
| `show standby brief` (CORE-1) | **Active** for every group; CORE-2 shows **Standby** |
| `show ip ospf neighbor` (R-EDGE) | 2 neighbours, both FULL |
| `show ip route` (R-EDGE) | `O E2` routes for 172.16.50.0 and 172.16.70.0 |
| `show ip dhcp snooping` (ACC-STUDENT) | Snooping enabled; G0/1-2 trusted |
| `show port-security` (ACC-STUDENT) | Fa0/1-3 Secure-up, max 1 |
| `show access-list` (FW-DC) | `CAMPUS_IN` with hit counters |
| `show crypto isakmp sa` (R-EDGE) | `QM_IDLE` once VPN traffic has flowed |

---

## Step 5: Review-2 live demo script (8 tests)
Take a screenshot of every result and save it in `06 Screenshots\` as `T1.png` … `T8.png`.

| # | Scenario | How to run it | Expected result |
|---|---|---|---|
| **T1** | Legitimate student access | STU-PC1 › Web Browser › `http://placement.srm.edu` | The PlaceGuard portal page loads, and DNS resolves through the server farm. |
| **T2** | Student tries to read the confidential database | STU-PC1 › Web Browser › `http://172.16.50.14`, and `ping 172.16.50.14` | **Request Timeout.** On FW-DC, `show access-list` shows the `deny ip any any` counter going up. |
| **T3** | Recruiter Wi-Fi tries to reach the student VLAN | REC-LAPTOP1 › `ping` STU-PC1's IP | **Destination host unreachable / timeout**, blocked by WIFI_IN on the core. REC-LAPTOP1 › `ping` INT-ROOM-1 **succeeds**. |
| **T4** | Rogue DHCP server plugged into a student port | Cable ROGUE-DHCP › ACC-STUDENT Fa0/10. On STU-PC2, set IP Configuration to Static, then back to DHCP. | STU-PC2 still gets a **10.10.10.1xx address with gateway 10.10.10.1**, never 10.10.10.10. `show ip dhcp snooping binding` lists only the real leases (`show ip dhcp snooping statistics` does not exist in PT 9). |
| **T5** | Unknown laptop plugged in place of a student PC | Remove STU-PC1's cable from Fa0/1 and plug UNKNOWN-LAPTOP into Fa0/1. Give the laptop a static 10.10.10.15x address (or click DHCP in its IP Configuration) so it actually sends traffic, then ping 10.10.10.1. | The port turns **red (err-disabled)**. `show port-security interface fa0/1` shows `Secure-shutdown`, violation count 1. |
| **T6** | Ping flood from the Internet towards the portal | ATTACKER-PC › `ping 203.0.113.5` | **Request timed out.** On R-EDGE, the log shows `%IPS-4-SIGNATURE: Sig:2004 ... ICMP Echo Request [45.10.20.66 -> 203.0.113.5]`. PUBLIC-USER › browser `http://203.0.113.5` **still works**. |
| **T7** | Encrypted recruiter VPN | HQ-HR-PC › Email: send a mail to `student1@srm.edu`. STU-PC1 › Email › Receive. Then switch to Simulation mode and repeat with a ping from HQ-INTERVIEWER to INT-ROOM-1. | The mail arrives. Between R-RECRUITER and R-EDGE the packets show as **ESP** (encrypted). `show crypto ipsec sa` on R-EDGE shows `#pkts encaps/decaps` increasing. The ISP never sees 10.x or 192.168.x addresses. |
| **T8** | Core switch failure (high availability) | STU-PC1 › `ping -t 45.10.20.10` (PUBLIC-USER on the Internet), then **power CORE-1 off** (Physical tab › power switch). Don't use the portal 172.16.70.10 as the target: PT's ASA keeps sending replies to CORE-1's MAC after it dies (tested), so that path never recovers in PT. | A few pings time out (5 in testing), then replies **resume** through CORE-2. `show standby brief` on CORE-2 shows **Active**. Power CORE-1 back on afterwards. Its saved config restores it and it takes back the Active role (preempt). |
| **Bonus B1** | Smart interview hall | Drag CARD-1001 to RFID-READER, then CARD-2002. | 1001 › reader **Valid**, door **unlocks**. 2002 › **Invalid**, door stays locked, **siren sounds**. |
| **Bonus B2** | Zero-trust management | STU-PC1 › Command Prompt › `ssh -l netadmin 10.10.10.2`. NETADMIN-PC › `ssh -l netadmin 10.10.99.2` (CORE-1's real address, not the HSRP virtual .1) | The student's attempt **times out** (STUDENT_IN drops it). The admin is prompted for a password, which is checked by **TACACS+** on AAA-SRV (`NetAdmin@2026`). |
| **Bonus B3** | Recruiter privacy (ZBF) | PLC-OFFICER › `ping` HQ-HR-PC's 192.168.50.x address | **Timeout.** The Zone-Based Firewall at HQ blocks campus-initiated traffic, while HQ-initiated traffic (T7) works. |

---

## Troubleshooting
* **A pasted command shows `% Invalid input`.** Some command names differ slightly between Packet Tracer versions. Skip that line, note it, and carry on. Common examples: `logging host` vs `logging`, and `ip arp inspection` (optional).
* **`crypto ...` or `ip ips ...` is rejected.** The security licence is not active. Run `show version` and check that `securityk9` is listed. If not, redo Part A and reload.
* **PCs get 169.254.x.x addresses.** Check `show standby brief` on the cores, the `ip helper-address` lines, and that `CAMPUS_IN` on FW-DC permits UDP 67. Then click DHCP again on the PC.
* **The first VPN ping fails.** This is normal: the first packets build the tunnel. Repeat the ping.
* **The ASA doesn't pass pings.** Make sure the `policy-map global_policy` lines (with `inspect icmp`) were accepted. If `inspect http` or `logging host SERVERS ...` is rejected, skip it; the tests don't need it.
* **`logging host 172.16.50.12` is rejected** on a router or switch. Use `logging 172.16.50.12` instead.
* **EtherChannel shows `(s)` or `(I)` instead of `(P)`.** Check that Fa0/23-24 have identical trunk settings on both cores, then `shutdown` and `no shutdown` the Port-channel.
* **T7 mail works but the HQ › INT-ROOM-1 ping fails.** Packet Tracer's IPS may inspect decrypted VPN traffic and drop ICMP echo. Show the encryption with the SMTP/POP3 packets in Simulation mode instead. That is a correct result: IPS blocks all inbound ICMP echo by design.
* **After `aaa new-model`, logins ask for TACACS+ credentials.** Configure AAA-SRV first. Until then, the local user `localadmin / Local@2026` works as a fallback.
* **The IoT editor has no "≠" operator.** Make two rules instead: `Card ID = 1001` (grant) and `Card ID = 2002` (deny + siren).
* **`ip arp inspection` is rejected** on ACC-STUDENT. Skip it; it's optional.
