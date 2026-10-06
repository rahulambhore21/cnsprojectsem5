# Parser Architecture & Registry

**ULPF Parser Engine & Dynamic Onboarding Subsystem**

---

## 1. Object-Oriented Parser Hierarchy

All parsers in ULPF inherit from the abstract `BaseParser` class:

```python
class BaseParser(ABC):
    name: str
    vendor: str
    supported_formats: List[str]
    version: str = "1.0.0"
    is_builtin: bool = True

    @abstractmethod
    def can_parse(self, raw_log: str) -> bool:
        """Signature and structural detection."""
        pass

    @abstractmethod
    def parse(self, raw_log: str) -> Dict[str, Any]:
        """Extraction of raw key-values."""
        pass
```

---

## 2. Deterministic Built-in Adapters

| Parser | Format | Detection Signature | Key Field Extractions |
|---|---|---|---|
| `CiscoParser` | Cisco ASA/IOS Syslog | `%ASA-`, `%IOS-`, `ciscoasa` | Event Code, Source/Dest IP & Port, Protocol, Action, Interface |
| `FortinetParser` | Key-Value (FortiOS) | `devname=`, `type="traffic"`, `srcip=` | `srcip`, `dstip`, `proto` (num->proto), `action`, `level` |
| `PaloAltoParser` | PAN-OS CSV & Syslog | `TRAFFIC,`, `THREAT,`, `pa-fw` | Future_use, Source/Dest IP & Port, Protocol, Rule, Action |
| `CEFParser` | ArcSight CEF | `CEF:Version\|Vendor\|...` | Header fields (7 parts) + Extensions (`src=`, `dst=`, `act=`) |
| `JsonParser` | Structured JSON | JSON `{...}` detection | Automatic extraction of standard cloud and microservice keys |
| `SyslogParser` | RFC 3164 / 5424 | PRI headers, Month/Day, `SRC=`, `DST=` | Priority, Facility, Timestamp, Hostname, Netfilter/UFW fields |

---

## 3. Dynamic Custom Parsers (`CustomDynamicParser`)

When an unsupported format is analyzed via the AI Parser Studio and approved by the analyst:
1. A parser record is written to the MongoDB `parsers` collection.
2. It encapsulates:
   - `parser_id`
   - `mapping`: dictionary mapping raw token names to Universal Schema paths
   - `signature_pattern`: regex pattern or matching keywords
3. The `ParserRegistry` loads dynamic parsers alongside built-ins.
4. If a future log matches the signature, it is parsed deterministically by `CustomDynamicParser` with zero latency and zero OpenAI tokens consumed.
