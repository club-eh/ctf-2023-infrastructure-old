#!/bin/bash

set -e

FLAGS=(
	-A /ctf-flagship.localctf/192.168.61.10
	-A /ctf-challenges-1.localctf/192.168.61.11
	#-A /ctf-challenges-2.localctf/192.168.61.12
)

sudo dnsmasq -d -p 53 --dns-loop-detect -z --listen-address 192.168.61.1 "${FLAGS[@]}"
