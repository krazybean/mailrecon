install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt

test:
	. .venv/bin/activate && pytest

live-test:
	. .venv/bin/activate && MAILRECON_LIVE_TEST=1 pytest tests/test_live.py
