# Per-bit linearity report — which state bits are linear vs non-linear

Over 40 random input-pair superposition trials on the 92-bit state (`F(X1)⊕F(X2)⊕F(X1⊕X2)⊕F(0)`). A bit is **non-linear** if it ever failed superposition.

- **51 of 92 bits NON-LINEAR**, 41 linear.

## Correlation with role

| group | flops | non-linear | linear |
|---|---|---|---|
| in success cone (hash core) | 57 | 51 | 6 |
| output-generator only | 35 | 0 | 35 |

| flop type | count | non-linear |
|---|---|---|
| dfrtp_2 | 84 | 51 |
| dfstp_2 | 4 | 0 |
| dfxtp_2 | 4 | 0 |

## Full per-flop table

| # | flop | type | cone | absorbs I | class | fails/40 |
|---|---|---|---|---|---|---|
| 0 | g__10 | dfxtp_2 |  |  | lin | 0 |
| 1 | g__11 | dfxtp_2 |  |  | lin | 0 |
| 2 | g__12 | dfstp_2 |  | ✓ | lin | 0 |
| 3 | g__13 | dfstp_2 |  |  | lin | 0 |
| 4 | g__14 | dfstp_2 |  |  | lin | 0 |
| 5 | g__178 | dfrtp_2 |  |  | lin | 0 |
| 6 | g__179 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 7 | g__180 | dfrtp_2 | ✓ |  | lin | 0 |
| 8 | g__181 | dfrtp_2 |  |  | lin | 0 |
| 9 | g__182 | dfrtp_2 | ✓ | ✓ | **NL** | 36 |
| 10 | g__183 | dfrtp_2 | ✓ | ✓ | lin | 0 |
| 11 | g__184 | dfrtp_2 | ✓ | ✓ | **NL** | 37 |
| 12 | g__185 | dfrtp_2 |  |  | lin | 0 |
| 13 | g__186 | dfrtp_2 |  | ✓ | lin | 0 |
| 14 | g__187 | dfrtp_2 |  |  | lin | 0 |
| 15 | g__188 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 16 | g__189 | dfrtp_2 | ✓ | ✓ | **NL** | 34 |
| 17 | g__190 | dfrtp_2 | ✓ | ✓ | **NL** | 17 |
| 18 | g__192 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 19 | g__193 | dfrtp_2 | ✓ | ✓ | **NL** | 34 |
| 20 | g__194 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 21 | g__195 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 22 | g__196 | dfrtp_2 |  |  | lin | 0 |
| 23 | g__197 | dfrtp_2 | ✓ |  | lin | 0 |
| 24 | g__198 | dfrtp_2 | ✓ | ✓ | **NL** | 34 |
| 25 | g__199 | dfrtp_2 |  |  | lin | 0 |
| 26 | g__200 | dfrtp_2 | ✓ | ✓ | **NL** | 5 |
| 27 | g__201 | dfrtp_2 | ✓ | ✓ | **NL** | 17 |
| 28 | g__202 | dfrtp_2 | ✓ | ✓ | **NL** | 36 |
| 29 | g__203 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 30 | g__204 | dfrtp_2 | ✓ | ✓ | **NL** | 29 |
| 31 | g__205 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 32 | g__206 | dfrtp_2 |  |  | lin | 0 |
| 33 | g__207 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 34 | g__208 | dfrtp_2 |  |  | lin | 0 |
| 35 | g__209 | dfrtp_2 |  |  | lin | 0 |
| 36 | g__210 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 37 | g__211 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 38 | g__212 | dfrtp_2 |  |  | lin | 0 |
| 39 | g__213 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 40 | g__214 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 41 | g__215 | dfrtp_2 | ✓ | ✓ | lin | 0 |
| 42 | g__216 | dfrtp_2 | ✓ | ✓ | **NL** | 26 |
| 43 | g__217 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 44 | g__218 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 45 | g__219 | dfrtp_2 | ✓ | ✓ | **NL** | 10 |
| 46 | g__220 | dfrtp_2 |  |  | lin | 0 |
| 47 | g__221 | dfrtp_2 |  |  | lin | 0 |
| 48 | g__222 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 49 | g__223 | dfrtp_2 |  |  | lin | 0 |
| 50 | g__224 | dfrtp_2 | ✓ | ✓ | **NL** | 23 |
| 51 | g__225 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 52 | g__226 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 53 | g__227 | dfrtp_2 |  |  | lin | 0 |
| 54 | g__228 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 55 | g__229 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 56 | g__230 | dfrtp_2 | ✓ | ✓ | **NL** | 37 |
| 57 | g__231 | dfrtp_2 |  |  | lin | 0 |
| 58 | g__232 | dfrtp_2 | ✓ | ✓ | **NL** | 35 |
| 59 | g__233 | dfrtp_2 | ✓ | ✓ | **NL** | 19 |
| 60 | g__234 | dfrtp_2 | ✓ | ✓ | **NL** | 37 |
| 61 | g__235 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 62 | g__236 | dfrtp_2 | ✓ | ✓ | **NL** | 20 |
| 63 | g__237 | dfrtp_2 |  |  | lin | 0 |
| 64 | g__238 | dfrtp_2 | ✓ | ✓ | **NL** | 27 |
| 65 | g__240 | dfrtp_2 |  |  | lin | 0 |
| 66 | g__241 | dfrtp_2 | ✓ | ✓ | **NL** | 40 |
| 67 | g__242 | dfrtp_2 | ✓ | ✓ | **NL** | 21 |
| 68 | g__243 | dfrtp_2 | ✓ |  | lin | 0 |
| 69 | g__244 | dfrtp_2 | ✓ | ✓ | **NL** | 37 |
| 70 | g__245 | dfrtp_2 |  |  | lin | 0 |
| 71 | g__247 | dfrtp_2 |  |  | lin | 0 |
| 72 | g__248 | dfrtp_2 |  |  | lin | 0 |
| 73 | g__249 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 74 | g__250 | dfrtp_2 |  |  | lin | 0 |
| 75 | g__251 | dfrtp_2 |  |  | lin | 0 |
| 76 | g__252 | dfrtp_2 | ✓ | ✓ | **NL** | 39 |
| 77 | g__253 | dfrtp_2 | ✓ | ✓ | **NL** | 33 |
| 78 | g__254 | dfrtp_2 | ✓ | ✓ | lin | 0 |
| 79 | g__255 | dfrtp_2 |  |  | lin | 0 |
| 80 | g__256 | dfrtp_2 |  |  | lin | 0 |
| 81 | g__257 | dfrtp_2 | ✓ | ✓ | **NL** | 35 |
| 82 | g__258 | dfrtp_2 |  | ✓ | lin | 0 |
| 83 | g__259 | dfrtp_2 |  | ✓ | lin | 0 |
| 84 | g__260 | dfrtp_2 | ✓ | ✓ | **NL** | 38 |
| 85 | g__261 | dfrtp_2 | ✓ | ✓ | **NL** | 20 |
| 86 | g__262 | dfrtp_2 | ✓ | ✓ | **NL** | 22 |
| 87 | g__263 | dfrtp_2 | ✓ | ✓ | **NL** | 22 |
| 88 | g__393 | dfrtp_2 | ✓ | ✓ | **NL** | 23 |
| 89 | g__405 | dfstp_2 |  |  | lin | 0 |
| 90 | g__539 | dfxtp_2 |  |  | lin | 0 |
| 91 | g__9 | dfxtp_2 |  |  | lin | 0 |
