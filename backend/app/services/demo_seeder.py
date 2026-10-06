import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.database import get_database
from app.parsers.registry import parser_registry
from app.services.normalization import NormalizationService
from app.schemas.parser import ParserDefinition
from app.schemas.source import SourceMetadata

logger = logging.getLogger("ulpf.seeder")

CISCO_LOGS = [
    '%ASA-4-106023: Deny tcp src inside:192.168.1.45/49221 dst outside:198.51.100.14/443 by access-group "acl_out" [0x0, 0x0]',
    '%ASA-2-106001: Inbound TCP connection denied from 203.0.113.195/58231 to 10.0.0.5/22 flags SYN on interface outside',
    '%ASA-6-302013: Built outbound TCP connection 23812 for outside:198.51.100.25/443 (198.51.100.25/443) to inside:192.168.1.105/52110',
    '%ASA-6-302014: Teardown TCP connection 23812 for outside:198.51.100.25/443 to inside:192.168.1.105/52110 duration 0:02:15 bytes 4892 TCP FINs',
    '%ASA-4-106023: Deny udp src inside:192.168.2.80/5353 dst outside:8.8.4.4/53 by access-group "block_dns_tunnel" [0x0, 0x0]',
    '%ASA-3-710003: TCP access denied by ACL from 198.51.100.77/4444 to outside:10.0.0.10/3389',
    '%ASA-5-713119: Group = EmployeeVPN, Username = jsmith, IP = 203.0.113.50, PHASE 1 COMPLETED',
    '%ASA-6-302015: Built outbound UDP connection 59281 for outside:8.8.8.8/53 (8.8.8.8/53) to inside:192.168.1.20/61200',
    '%ASA-4-106023: Deny ip src dmz:172.16.10.50 dst outside:198.51.100.99 by access-group "dmz_egress_restrict"',
    '%ASA-1-106021: Deny protocol 1 src outside:203.0.113.88 dst inside:10.0.0.1 (type 8, code 0) by access-group "drop_icmp_flood"'
]

FORTINET_LOGS = [
    'date=2026-10-06 time=10:14:22 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="notice" vd="root" srcip=192.168.10.15 srcport=54122 srcintf="port1" dstip=198.51.100.4 dstport=443 dstintf="port2" proto=6 action="deny" policyid=102 service="HTTPS" sessionid=109283 crscore=30 craction=131072 crlevel="high"',
    'date=2026-10-06 time=10:15:01 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000020" type="traffic" subtype="forward" level="notice" vd="root" srcip=192.168.10.88 srcport=49811 srcintf="port1" dstip=172.217.16.206 dstport=80 dstintf="port2" proto=6 action="accept" policyid=101 service="HTTP" sessionid=109284',
    'date=2026-10-06 time=10:16:11 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0100020001" type="event" subtype="vpn" level="information" vd="root" user="akash.sharma" srcip=203.0.113.41 dstip=192.168.10.1 action="tunnel-up" tunneltype="ssl-tunnel" msg="SSL tunnel established"',
    'date=2026-10-06 time=10:17:34 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="warning" vd="root" srcip=192.168.20.100 srcport=61244 srcintf="port3" dstip=203.0.113.99 dstport=22 dstintf="port2" proto=6 action="drop" policyid=99 service="SSH" msg="SSH brute force blocked"',
    'date=2026-10-06 time=10:18:05 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="notice" vd="root" srcip=192.168.10.22 srcport=51299 srcintf="port1" dstip=1.1.1.1 dstport=53 dstintf="port2" proto=17 action="accept" policyid=105 service="DNS"',
    'date=2026-10-06 time=10:19:12 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="alert" vd="root" srcip=203.0.113.200 srcport=40123 srcintf="port2" dstip=192.168.1.5 dstport=445 dstintf="port1" proto=6 action="deny" policyid=5 service="SMB" msg="WannaCry scan drop"',
    'date=2026-10-06 time=10:20:00 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="notice" vd="root" srcip=192.168.10.14 srcport=50020 srcintf="port1" dstip=142.250.190.46 dstport=443 dstintf="port2" proto=6 action="accept" policyid=101 service="HTTPS"',
    'date=2026-10-06 time=10:21:40 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="error" vd="root" srcip=192.168.30.55 srcport=48899 srcintf="port4" dstip=198.51.100.80 dstport=8080 dstintf="port2" proto=6 action="close" policyid=110 service="HTTP-Alt"',
    'date=2026-10-06 time=10:22:19 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="critical" vd="root" srcip=192.168.10.200 srcport=38910 srcintf="port1" dstip=198.51.100.200 dstport=3389 dstintf="port2" proto=6 action="deny" policyid=40 service="RDP" msg="C2 beacon detected"',
    'date=2026-10-06 time=10:23:45 devname=FG-HQ-500D devid=FG500D3G15800010 logid="0000000013" type="traffic" subtype="forward" level="notice" vd="root" srcip=192.168.10.12 srcport=59001 srcintf="port1" dstip=93.184.216.34 dstport=443 dstintf="port2" proto=6 action="accept" policyid=101 service="HTTPS"'
]

PALOALTO_LOGS = [
    '1,2026/10/06 10:24:10,001801000000,TRAFFIC,drop,1,2026/10/06 10:24:10,192.168.1.105,198.51.100.55,0.0.0.0,0.0.0.0,Rule-Block-Malicious,,,ssl,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:24:10,1001,1,51200,443,0,0,0x0,tcp,deny,0,0,0,0,2026/10/06 10:24:10,0,any,0,0,0,0,0,,PA-5250,from-policy,,,0',
    '1,2026/10/06 10:25:00,001801000000,TRAFFIC,start,1,2026/10/06 10:25:00,10.0.0.12,198.51.100.12,0.0.0.0,0.0.0.0,Rule-Allow-Web,,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:25:00,1002,1,49152,80,0,0,0x0,tcp,allow,1200,1200,0,1,2026/10/06 10:25:00,0,any,0,0,0,0,0,,PA-5250,from-policy,,,0',
    '1,2026/10/06 10:25:45,001801000000,THREAT,vulnerability,1,2026/10/06 10:25:45,203.0.113.66,10.0.0.5,0.0.0.0,0.0.0.0,Rule-DMZ-Inbound,,,http,vsys1,untrust,dmz,ethernet1/1,ethernet1/3,log-forwarder,2026/10/06 10:25:45,1003,1,43210,80,0,0,0x0,tcp,reset-both,0,0,0,0,2026/10/06 10:25:45,0,any,0,0,0,0,0,,PA-5250,Apache-Struts-Exploit,,,0',
    '1,2026/10/06 10:26:15,001801000000,TRAFFIC,drop,1,2026/10/06 10:26:15,192.168.1.180,198.51.100.99,0.0.0.0,0.0.0.0,Rule-Block-Mining,,,stratum,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:26:15,1004,1,55660,3333,0,0,0x0,tcp,drop,0,0,0,0,2026/10/06 10:26:15,0,any,0,0,0,0,0,,PA-5250,Crypto-Miner-Block,,,0',
    '1,2026/10/06 10:27:00,001801000000,TRAFFIC,end,1,2026/10/06 10:27:00,10.0.0.45,8.8.8.8,0.0.0.0,0.0.0.0,Rule-Allow-DNS,,,dns,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:27:00,1005,1,62345,53,0,0,0x0,udp,allow,180,180,0,1,2026/10/06 10:27:00,0,any,0,0,0,0,0,,PA-5250,from-policy,,,0',
    '1,2026/10/06 10:27:30,001801000000,TRAFFIC,drop,1,2026/10/06 10:27:30,203.0.113.111,10.0.0.2,0.0.0.0,0.0.0.0,Rule-Recon-Block,,,ssh,vsys1,untrust,trust,ethernet1/1,ethernet1/2,log-forwarder,2026/10/06 10:27:30,1006,1,58900,22,0,0,0x0,tcp,deny,0,0,0,0,2026/10/06 10:27:30,0,any,0,0,0,0,0,,PA-5250,Port-Scan-Drop,,,0',
    '1,2026/10/06 10:28:10,001801000000,TRAFFIC,end,1,2026/10/06 10:28:10,192.168.1.20,198.51.100.1,0.0.0.0,0.0.0.0,Rule-Allow-SSL,,,ssl,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:28:10,1007,1,50123,443,0,0,0x0,tcp,allow,5400,5400,0,1,2026/10/06 10:28:10,0,any,0,0,0,0,0,,PA-5250,from-policy,,,0',
    '1,2026/10/06 10:28:45,001801000000,TRAFFIC,drop,1,2026/10/06 10:28:45,192.168.1.99,198.51.100.22,0.0.0.0,0.0.0.0,Rule-Tor-Exit-Block,,,tor,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:28:45,1008,1,49900,9001,0,0,0x0,tcp,drop,0,0,0,0,2026/10/06 10:28:45,0,any,0,0,0,0,0,,PA-5250,Darknet-Block,,,0',
    '1,2026/10/06 10:29:10,001801000000,TRAFFIC,end,1,2026/10/06 10:29:10,10.0.0.100,140.82.112.4,0.0.0.0,0.0.0.0,Rule-Dev-Git,,,git,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:29:10,1009,1,52001,443,0,0,0x0,tcp,allow,89000,89000,0,1,2026/10/06 10:29:10,0,any,0,0,0,0,0,,PA-5250,from-policy,,,0',
    '1,2026/10/06 10:30:00,001801000000,TRAFFIC,drop,1,2026/10/06 10:30:00,203.0.113.15,10.0.0.50,0.0.0.0,0.0.0.0,Rule-GeoIP-Block,,,icmp,vsys1,untrust,dmz,ethernet1/1,ethernet1/3,log-forwarder,2026/10/06 10:30:00,1010,1,0,0,0,0,0x0,icmp,deny,0,0,0,0,2026/10/06 10:30:00,0,any,0,0,0,0,0,,PA-5250,Geo-Fence-Trigger,,,0'
]

SYSLOG_LOGS = [
    'Oct 06 10:31:01 edge-fw-01 kernel: [UFW BLOCK] IN=eth0 OUT= SRC=203.0.113.44 DST=192.168.1.1 LEN=40 TOS=0x00 PREC=0x00 TTL=243 ID=54321 PROTO=TCP SPT=41920 DPT=23 WINDOW=1024 RES=0x00 SYN URGP=0 ACTION=DENY',
    'Oct 06 10:31:15 edge-fw-01 kernel: [UFW ALLOW] IN=eth0 OUT=eth1 SRC=192.168.1.50 DST=8.8.8.8 PROTO=UDP SPT=51234 DPT=53 ACTION=ALLOW',
    'Oct 06 10:31:30 auth-server sshd[28411]: Failed password for invalid user root from 203.0.113.88 port 48920 ssh2 ACTION=DENY',
    'Oct 06 10:31:45 auth-server sshd[28415]: Accepted publickey for rahul from 192.168.1.15 port 54110 ssh2: RSA SHA256:4b227777d ACTION=ALLOW',
    'Oct 06 10:32:00 edge-router iptables: IN=wan0 OUT=lan0 SRC=198.51.100.12 DST=192.168.1.200 PROTO=TCP SPT=49110 DPT=443 ACTION=ALLOW',
    'Oct 06 10:32:15 edge-router iptables: IN=wan0 OUT= SRC=203.0.113.250 DST=192.168.1.1 PROTO=TCP SPT=60000 DPT=445 ACTION=DROP',
    'Oct 06 10:32:30 vpn-gateway openvpn[1050]: rahul.ambhore/198.51.100.33:1194 MULTI: Learn: 10.8.0.5 -> rahul.ambhore/198.51.100.33:1194 ACTION=ALLOW',
    'Oct 06 10:32:45 edge-fw-01 kernel: [UFW BLOCK] IN=eth0 OUT= SRC=203.0.113.77 DST=192.168.1.10 PROTO=TCP SPT=38910 DPT=3389 ACTION=DENY',
    'Oct 06 10:33:00 dns-resolver named[991]: client @0x7f11 192.168.1.10#53210 (malicious-c2.net): query: malicious-c2.net IN A + (127.0.0.1) ACTION=ALERT',
    'Oct 06 10:33:15 edge-fw-01 kernel: [UFW ALLOW] IN=eth1 OUT=eth0 SRC=192.168.1.88 DST=140.82.121.3 PROTO=TCP SPT=49811 DPT=443 ACTION=ALLOW'
]

JSON_LOGS = [
    '{"timestamp": "2026-10-06T10:34:00Z", "vendor": "Suricata", "product": "IDS", "src_ip": "203.0.113.5", "src_port": 50122, "dst_ip": "192.168.1.10", "dst_port": 80, "protocol": "TCP", "action": "DENY", "severity": "high", "alert": "ET SCAN Nmap Scripting Engine"}',
    '{"timestamp": "2026-10-06T10:34:15Z", "vendor": "AWS", "product": "VPC_Flow", "src_ip": "10.0.1.25", "src_port": 49200, "dst_ip": "10.0.2.50", "dst_port": 5432, "protocol": "TCP", "action": "ALLOW", "severity": "low", "bytes": 4820}',
    '{"timestamp": "2026-10-06T10:34:30Z", "vendor": "Cloudflare", "product": "WAF", "src_ip": "198.51.100.88", "src_port": 61200, "dst_ip": "172.67.180.20", "dst_port": 443, "protocol": "TCP", "action": "BLOCK", "severity": "critical", "rule": "SQLi Injection Vector Detected"}',
    '{"timestamp": "2026-10-06T10:34:45Z", "vendor": "Zeek", "product": "Bro", "src_ip": "192.168.1.45", "src_port": 53001, "dst_ip": "8.8.8.8", "dst_port": 53, "protocol": "UDP", "action": "ALLOW", "severity": "low", "query": "api.github.com"}',
    '{"timestamp": "2026-10-06T10:35:00Z", "vendor": "CrowdStrike", "product": "Falcon", "src_ip": "192.168.1.99", "src_port": 49155, "dst_ip": "198.51.100.22", "dst_port": 4444, "protocol": "TCP", "action": "DENY", "severity": "critical", "username": "admin", "tactic": "Command and Control"}',
    '{"timestamp": "2026-10-06T10:35:15Z", "vendor": "NGINX", "product": "Ingress", "src_ip": "203.0.113.14", "src_port": 54100, "dst_ip": "10.244.0.15", "dst_port": 8080, "protocol": "TCP", "action": "ALLOW", "severity": "low", "uri": "/api/v1/auth/login"}',
    '{"timestamp": "2026-10-06T10:35:30Z", "vendor": "Suricata", "product": "IDS", "src_ip": "203.0.113.90", "src_port": 39120, "dst_ip": "192.168.1.2", "dst_port": 22, "protocol": "TCP", "action": "DENY", "severity": "high", "alert": "GPL ATTACK_RESPONSE id check returned root"}',
    '{"timestamp": "2026-10-06T10:35:45Z", "vendor": "ModSecurity", "product": "WAF", "src_ip": "198.51.100.5", "src_port": 58900, "dst_ip": "192.168.1.5", "dst_port": 443, "protocol": "TCP", "action": "BLOCK", "severity": "high", "attack": "XSS vector <script>"}',
    '{"timestamp": "2026-10-06T10:36:00Z", "vendor": "Kubernetes", "product": "Audit", "src_ip": "10.0.0.10", "src_port": 6443, "dst_ip": "10.0.0.1", "dst_port": 443, "protocol": "TCP", "action": "ALLOW", "severity": "low", "username": "system:serviceaccount:default"}',
    '{"timestamp": "2026-10-06T10:36:15Z", "vendor": "Okta", "product": "IdP", "src_ip": "203.0.113.40", "src_port": 0, "dst_ip": "0.0.0.0", "dst_port": 443, "protocol": "TCP", "action": "DENY", "severity": "high", "username": "finance_admin", "reason": "MFA Challenge Failed"}'
]

CEF_LOGS = [
    'CEF:0|CheckPoint|VPN-1|R80.40|drop|Drop|8|src=203.0.113.15 dst=192.168.1.5 spt=51234 dpt=80 proto=TCP act=blocked msg=SYN-Flood mitigation',
    'CEF:0|Symantec|Endpoint|14.3|1|Network Threat Detected|9|src=192.168.1.80 dst=198.51.100.7 spt=49221 dpt=4444 proto=TCP act=blocked suser=bob msg=Trojan.Gen execution blocked',
    'CEF:0|Imperva|Incapsula|2.0|WAF_ALERT|DDoS Attack Mitigated|10|src=203.0.113.100 dst=198.51.100.200 spt=40001 dpt=443 proto=TCP act=blocked msg=Layer 7 HTTP Flood',
    'CEF:0|F5|BIG-IP-ASM|16.1|2000000|Access Granted|3|src=192.168.10.5 dst=10.10.10.20 spt=55400 dpt=443 proto=TCP act=allow suser=operator msg=Authenticated Reverse Proxy Session',
    'CEF:0|SonicWall|NSA|7.0|1|Connection Dropped|6|src=203.0.113.12 dst=192.168.1.1 spt=33890 dpt=3389 proto=TCP act=blocked msg=Unauthorized RDP Probe'
]

CUSTOM_LOGS = [
    '2026-10-06 11:20:31 FW-CUSTOM-01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked level=high user=guest',
    '2026-10-06 11:22:15 FW-CUSTOM-01 source=192.168.50.12 destination=8.8.8.8 protocol=udp port=53 decision=allowed level=low user=system',
    '2026-10-06 11:24:00 PROXY-CUSTOM client=10.20.30.40 server=198.51.100.77 proto=tcp sport=51000 dport=8080 action=blocked severity=critical alert=TorNode',
    '2026-10-06 11:25:40 SEC-GATEWAY-X src_ip=172.16.2.99 dst_ip=192.168.1.1 protocol=icmp decision=denied level=medium rule=ICMP-Ping-Block',
    '2026-10-06 11:27:10 ROUTER-NODE-7 client_ip=203.0.113.55 dest_ip=10.0.0.8 proto=tcp port=22 action=denied level=high user=attacker'
]

class DemoSeeder:
    @classmethod
    def seed_database(cls) -> Dict[str, Any]:
        """
        Clears demo collection and seeds realistic logs across all vendors.
        Calculates and stores actual Universal Events in MongoDB.
        """
        db = get_database()
        
        # 1. Reset collections
        db["events"].delete_many({})
        db["sources"].delete_many({})
        db["parsers"].delete_many({})
        db["audit_logs"].delete_many({})

        # 2. Seed Builtin Parser Records into parsers collection
        builtin_parsers_info = [
            {"parser_id": "parser_cisco_asa", "name": "Cisco ASA / IOS Parser", "vendor": "Cisco", "format": "syslog", "is_builtin": True, "version": "1.0.0"},
            {"parser_id": "parser_fortinet_fortigate", "name": "Fortinet FortiGate Parser", "vendor": "Fortinet", "format": "kv", "is_builtin": True, "version": "1.0.0"},
            {"parser_id": "parser_paloalto_panos", "name": "Palo Alto PAN-OS Parser", "vendor": "Palo Alto", "format": "csv", "is_builtin": True, "version": "1.0.0"},
            {"parser_id": "parser_generic_syslog", "name": "Generic Syslog Parser (RFC 3164/5424)", "vendor": "Generic", "format": "syslog", "is_builtin": True, "version": "1.0.0"},
            {"parser_id": "parser_generic_json", "name": "Generic JSON Parser", "vendor": "Generic", "format": "json", "is_builtin": True, "version": "1.0.0"},
            {"parser_id": "parser_generic_cef", "name": "ArcSight CEF Parser", "vendor": "Generic", "format": "cef", "is_builtin": True, "version": "1.0.0"}
        ]
        for p in builtin_parsers_info:
            p["createdAt"] = datetime.now(timezone.utc).isoformat()
            p["updatedAt"] = datetime.now(timezone.utc).isoformat()
            p["is_active"] = True
            db["parsers"].insert_one(p)

        all_logs = (
            [(log, "cisco") for log in CISCO_LOGS] +
            [(log, "fortinet") for log in FORTINET_LOGS] +
            [(log, "paloalto") for log in PALOALTO_LOGS] +
            [(log, "syslog") for log in SYSLOG_LOGS] +
            [(log, "json") for log in JSON_LOGS] +
            [(log, "cef") for log in CEF_LOGS]
        )

        inserted_events = []
        vendor_counts: Dict[str, int] = {}
        vendor_formats: Dict[str, str] = {}

        # Base timestamp for timeline distribution
        now = datetime.now(timezone.utc)

        for i, (raw_log, category_hint) in enumerate(all_logs):
            parser, parsed_data = parser_registry.detect_and_parse(raw_log, db=db)
            if not parser or not parsed_data:
                continue

            event = NormalizationService.to_universal_event(
                raw_log=raw_log,
                parsed_data=parsed_data,
                parser_name=parser.name,
                parser_version=parser.version,
                confidence=getattr(parser, "confidence", 0.98),
                is_ai_assisted=False
            )

            # Spread event timestamps over the last 24 hours for realistic charts
            time_offset = timedelta(minutes=(len(all_logs) - i) * 25)
            adjusted_time = (now - time_offset).strftime("%Y-%m-%dT%H:%M:%SZ")
            event_dict = event.model_dump()
            event_dict["timestamp"] = adjusted_time
            event_dict["createdAt"] = adjusted_time

            db["events"].insert_one(event_dict)
            inserted_events.append(event_dict["event_id"])

            vendor = event.source.vendor or "Generic"
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
            if event.source.format:
                vendor_formats[vendor] = event.source.format

        # 3. Upsert sources metadata
        for vendor, count in vendor_counts.items():
            db["sources"].insert_one({
                "source_id": f"src_{vendor.lower().replace(' ', '_')}",
                "name": f"{vendor} Gateway",
                "vendor": vendor,
                "format": vendor_formats.get(vendor, "syslog"),
                "status": "active",
                "event_count": count,
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "createdAt": datetime.now(timezone.utc).isoformat()
            })

        # 4. Insert an initial Audit Log
        db["audit_logs"].insert_one({
            "action": "SYSTEM_SEED",
            "user": "admin",
            "resource": "database",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"seeded_events": len(inserted_events), "vendors": list(vendor_counts.keys())}
        })

        return {
            "success": True,
            "message": f"Successfully seeded {len(inserted_events)} realistic events across {len(vendor_counts)} sources.",
            "seeded_count": len(inserted_events),
            "vendors": list(vendor_counts.keys())
        }

    @classmethod
    def get_sample_library(cls) -> Dict[str, List[str]]:
        """Returns sample logs grouped by category for quick UI testing & copy-paste."""
        return {
            "cisco": CISCO_LOGS,
            "fortinet": FORTINET_LOGS,
            "paloalto": PALOALTO_LOGS,
            "syslog": SYSLOG_LOGS,
            "json": JSON_LOGS,
            "cef": CEF_LOGS,
            "custom": CUSTOM_LOGS
        }
