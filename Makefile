.PHONY: install data check test robustness
install:     ; pip install -e ".[dev]"
data:        ; meldq generate
check:       ; meldq check
all:         ; meldq all
test:        ; pytest -q
robustness:  ; meldq robustness --n 20
