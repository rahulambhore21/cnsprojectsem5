from app.services.ai_service import AIService
from app.schemas.ai import AIAnalysisResponse

def test_ai_fallback_heuristic_analysis():
    custom_log = "2026-10-06 11:20:31 FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked"
    res = AIService.analyze_log(custom_log)
    assert isinstance(res, AIAnalysisResponse)
    assert res.confidence >= 0.8
    assert len(res.mappings) >= 3

    # Check that source IP and destination IP were identified
    target_fields = [m.target_field for m in res.mappings]
    assert "network.source_ip" in target_fields
    assert "network.destination_ip" in target_fields
