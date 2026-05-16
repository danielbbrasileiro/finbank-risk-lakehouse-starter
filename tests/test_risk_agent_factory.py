from src.ai_assistant.app import OfflineGovernedRiskAgent, build_risk_agent


def test_build_risk_agent_uses_offline_agent_in_demo_mode(monkeypatch) -> None:
    monkeypatch.setenv("AI_DEMO_MODE", "1")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    agent = build_risk_agent()

    assert isinstance(agent, OfflineGovernedRiskAgent)
    assert "governed offline mode" in agent.ask("show customer exposure by segment").lower()
