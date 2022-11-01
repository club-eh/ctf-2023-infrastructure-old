# MAC Addresses

"OUI" used for all specified interfaces: `EE:E7:E7`

- `7E7` chosen because it represents 2023 in hexadecimal
- `EEE` chosen because it needs to be a "local, unicast" address and it matches the E from 7E7

4th byte is all-zeros or unique per-deployment (potentially useful in case of multiple test environments on the same network)

5th byte identifies environment and interface:

| Environment | MAC Address Prefix |
| --- | --- |
| Production | `EE:E7:E7:??:0?` |
| Staging    | `EE:E7:E7:??:1?` |
| Local      | `EE:E7:E7:??:2?` |

| Interface | MAC Address Prefix |
| --- | --- |
| Public  | `EE:E7:E7:??:?0` |
| Private | `EE:E7:E7:??:?1` |

6th byte identifies machine:

- Flagship: `:10`
- Challenges: `:20` (, `:21`, ...)
