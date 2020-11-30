import pytest

from tests.conftest import FftMock


def test_empty_config_request_topic(monkeypatch, ML_MOCK_FFT):
    monkeypatch.setenv("CONFIG_MESSAGING_REQUEST_TOPIC", "")
    mock_ = FftMock(outgoing_message_is_temporary=True)
    assert len(mock_._get_topics()) == 1
    assert mock_._get_topics()[0] == "kosmos/analytics/test_url/test_tag"
