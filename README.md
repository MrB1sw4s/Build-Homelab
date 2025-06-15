# Build-Homelab: Self-Hosted Cloud, Attackbox & Dark Web Stack

A bare-metal homelab project built from scratch using an Intel i5 server and Raspberry Pi-based remote controller. This lab merges **cloud self-hosting**, **web anonymity**, and **offensive security tooling** into one fully modular setup — controlled from anywhere via a custom Flask-based GPIO-powered relay web interface.

---

## 🏗️ Overview

- **Fileserver with Nextcloud**, hosted on RAID-like merged disks (via mergerfs)
- **Dark web server**, hosted via Tor hidden service in a Debian VM
- **Browser-based Attackbox** (ParrotSec + x11vnc), accessible via Cloudflare Tunnel + Zero Trust
- **Remote-controlled server boot** via Raspberry Pi GPIO and Flask web panel

---

## ⚙️ Tech Stack

| Component      | Stack Used                                     |
|----------------|------------------------------------------------|
| Host OS        | Ubuntu Server 22.04 LTS                        |
| Virtualization | QEMU/KVM + Virt-Manager                        |
| Storage        | MergerFS over multiple HDDs                    |
| File Server    | Apache + MariaDB + Nextcloud                   |
| Dark Web Site  | Debian VM + Tor + NGINX                        |
| Attack Box     | ParrotSec (HTB variant) + x11vnc               |
| Public Tunnel  | Cloudflare Tunnel + Zero Trust Access          |
| GPIO Control   | Flask + RPi GPIO + Dual-relay circuit          |

---

## 🛠️ Hardware Used

- **Main Server**: i5-7600, 8 GB RAM, 256 GB NVMe, 1.5 TB HDD
- **Raspberry Pi**: Used for relay-based remote boot control
- **Relay Board**: Dual-channel (PSU & motherboard trigger)

---

## 💡 Use Cases

- Fully private self-hosted cloud (Nextcloud) with public access via domain
- Red/Blue team lab with persistent attack VM
- Onion site hosting inside a VM with Tor service
- Remote browser-based offensive VM via VNC-over-Cloudflare
- Pi-controlled power sequencing for complete headless boot/shutdown

---

## 🛡️ Security Notes

- Fileserver isolated from WAN using Cloudflare tunneling
- Onion services fully segmented within VM sandbox
- Attackbox access protected via Cloudflare Access OTP & domain filter
- No direct port forwarding; hardened via tunnel+auth

---

## 🌐 Architecture Snapshot

Raspberry Pi (Remote Controller)
├── Flask Web App (GPIO-based Relay)
│   ├── PSU Relay (Power ON/OFF)
│   └── Motherboard Boot Trigger

Main Server (Ubuntu 22.04)
├── Virtual Machines (via KVM)
│   ├── ParrotSec (HTB Edition)
│   │   └── x11vnc → Cloudflare Tunnel → Browser (Zero Trust Access)
│   └── Debian VM
│       └── NGINX + Tor → .onion Dark Web Site
├── Fileserver
│   └── Nextcloud (Apache + MariaDB + PHP)
│       └── Mounted on MergerFS (sda1 + sdb1)
└── Cloudflare Tunnels
    ├── HTTPS Access to Fileserver
    └── TCP Forwarding to ParrotSec VNC

---

## 🧠 Challenges Overcome

- Merged storage management via `mergerfs` for live cloud sync
- Full Nextcloud deployment with MariaDB + Apache config
- Secure onion routing via Tor hidden services
- Browser-ready VNC with OTP-auth, TLS, and subdomain routing
- Automated power control with delay-sequenced relays (PSU → MB)

---

## 🔗 Extras

- ⚡ Onion site hosting fully operational inside VM
- 🛠️ Public access to file server via registered domain + Cloudflare
- 💥 ParrotSec VNC rendered inside browser (no Chrome!)

