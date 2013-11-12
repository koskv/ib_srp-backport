all: srp-initiator-state-diagram.svg srp-initiator-state-diagram.png

srp-initiator-state-diagram.svg: srp-initiator-state-diagram.dot
	dot -Tsvg -o $@ $<

srp-initiator-state-diagram.png: srp-initiator-state-diagram.dot
	dot -Tpng -o $@ $<
