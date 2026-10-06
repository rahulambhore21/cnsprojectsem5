import pytest
from app.parsers.cisco import CiscoParser
from app.parsers.fortinet import FortinetParser
from app.parsers.paloalto import PaloAltoParser
from app.parsers.cef import CEFParser
from app.parsers.json_parser import JsonParser
from app.parsers.syslog import SyslogParser
from app.parsers.dynamic import CustomDynamicParser
from app.parsers.registry import parser_registry

def test_cisco_parser():
    raw_log = '%ASA-4-106023: Deny tcp src inside:192.168.1.10/49221 dst outside:8.8.8.8/443 by access-group "acl_out"'
    parser = CiscoParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["vendor"] == "Cisco"
    assert data["source_ip"] == "192.168.1.10"
    assert data["source_port"] == 49221
    assert data["destination_ip"] == "8.8.8.8"
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_fortinet_parser():
    raw_log = 'date=2026-10-06 time=10:31:22 devname=FG100D srcip=192.168.1.10 srcport=49221 dstip=8.8.8.8 dstport=443 proto=6 action=deny level=warning'
    parser = FortinetParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["vendor"] == "Fortinet"
    assert data["source_ip"] == "192.168.1.10"
    assert data["destination_ip"] == "8.8.8.8"
    assert data["source_port"] == 49221
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"
    assert data["severity"] == "medium"

def test_paloalto_parser():
    raw_log = '1,2026/10/06 10:31:22,001801000000,TRAFFIC,drop,1,2026/10/06 10:31:22,192.168.1.10,8.8.8.8,0.0.0.0,0.0.0.0,Rule-Block,,,ssl,vsys1,trust,untrust,ethernet1/2,ethernet1/1,log-forwarder,2026/10/06 10:31:22,1001,1,49221,443,0,0,0x0,tcp,deny,0,0,0,0,2026/10/06 10:31:22,0,any,0,0,0,0,0,,PA-3020,from-policy,,,0'
    parser = PaloAltoParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["vendor"] == "Palo Alto"
    assert data["source_ip"] == "192.168.1.10"
    assert data["destination_ip"] == "8.8.8.8"
    assert data["source_port"] == 49221
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_cef_parser():
    raw_log = 'CEF:0|Vendor|Firewall|1.0|100|Connection|5|src=192.168.1.10 dst=8.8.8.8 spt=49221 dpt=443 proto=TCP act=blocked'
    parser = CEFParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["format"] == "cef"
    assert data["source_ip"] == "192.168.1.10"
    assert data["destination_ip"] == "8.8.8.8"
    assert data["source_port"] == 49221
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_json_parser():
    raw_log = '{"timestamp": "2026-10-06T10:31:22Z", "src_ip": "192.168.1.10", "dst_ip": "8.8.8.8", "src_port": 49221, "dst_port": 443, "protocol": "TCP", "action": "DENY"}'
    parser = JsonParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["format"] == "json"
    assert data["source_ip"] == "192.168.1.10"
    assert data["destination_ip"] == "8.8.8.8"
    assert data["source_port"] == 49221
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_syslog_parser():
    raw_log = 'Oct 06 10:31:22 firewall01 SRC=192.168.1.10 DST=8.8.8.8 PROTO=TCP DPT=443 ACTION=DENY'
    parser = SyslogParser()
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["format"] == "syslog"
    assert data["source_ip"] == "192.168.1.10"
    assert data["destination_ip"] == "8.8.8.8"
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_custom_dynamic_parser():
    mapping = {
        "source": "network.source_ip",
        "destination": "network.destination_ip",
        "protocol": "network.protocol",
        "port": "network.destination_port",
        "decision": "event.action"
    }
    raw_log = '2026-10-06 11:20:31 FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked'
    parser = CustomDynamicParser(
        parser_id="custom_test",
        name="Test Parser",
        vendor="TestVendor",
        format_type="custom",
        mapping=mapping
    )
    assert parser.can_parse(raw_log) is True
    data = parser.parse(raw_log)
    assert data["source_ip"] == "10.10.1.20"
    assert data["destination_ip"] == "172.16.0.10"
    assert data["destination_port"] == 443
    assert data["protocol"] == "TCP"
    assert data["action"] == "DENY"

def test_parser_registry_precedence():
    cisco_log = '%ASA-4-106023: Deny tcp src inside:192.168.1.10/49221 dst outside:8.8.8.8/443'
    parser, data = parser_registry.detect_and_parse(cisco_log)
    assert parser is not None
    assert parser.name == "CiscoParser"
