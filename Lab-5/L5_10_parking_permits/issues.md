\# Issues Identified and Fixed



| Issue | Type | Line(s) | Description | Fix Approach |

|---|---|---|---|---|

| Insecure random number generation | Security — Low | 11 | `random.randint()` is not suitable for security-sensitive permit numbers. | Replaced `random` with `secrets` and used `secrets.randbelow()`. |

| Silent exception handling | Security — Low / Code quality | 22 | A bare `except` with `pass` hides errors when revoking a permit. | Used `permits.pop(vehicle\_plate, None)` to handle missing permits safely. |

| Mutable default argument | Bug / Code quality | 9 | Using `zone\_records=\[]` shares the same list across function calls. | Changed the default to `None` and initialized a list inside the function. |

| Broad exception handling | Code quality | 16, 29, 43 | Bare `except` clauses catch errors without distinguishing their causes. | Replaced broad exception handling with specific exception types where appropriate. |

| Unsafe file handling | Code quality | 42, 47 | Files were opened without context managers or explicit encoding. | Used `with open(...)` and `encoding="utf-8"`. |

| Missing documentation | Code quality | Multiple | The module and functions lacked docstrings. | Added module and function docstrings. |

| Non-standard function name | Style | 51 | `setExpiry` does not follow Python's snake\_case naming convention. | Renamed it to `set\_expiry`. |

| Long lines and spacing issues | Style | Multiple | Several lines exceeded length limits and functions lacked the required blank lines. | Reformatted the code to satisfy Flake8. |

