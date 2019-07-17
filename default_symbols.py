""" 
This file contains the default symbol list as well as a list of special symbols
which should behave like colon-delimited symbols.
"""
SPECIAL_KEYS = [
    '->',
    '<-'
]

DEFAULT_MATCHES = [
    # Arrows
    ('->',          u'\u2192'),
    ('=>',          u'\u21D2'),
    ('<-',          u'\u2190'),
    ('<=',          u'\u21D0'),
    (':N:',         u'\u2191'),
    (':N2:',        u'\u21D1'),
    (':S:',         u'\u2193'),
    (':S2:',        u'\u21D3'),
    (':E:',         u'\u2192'),
    (':E2:',        u'\u21D2'),
    (':W:',         u'\u2190'),
    (':W2:',        u'\u21D0'),

    # Math symbols
    (':geq:',       u'\u2265'),
    (':leq:',       u'\u2264'),
    (':>>:',        u'\u226B'),
    (':<<:',        u'\u226A'),
    (':pm:',        u'\u00B1'),
    (':infty:',     u'\u221E'),
    (':approx:',    u'\u2248'),
    (':neq:',       u'\u2260'),
    (':deg:',       u'\u00B0'),

    # Fractions
    (':1/2:',       u'\u00BD'),
    (':1/3:',       u'\u2153'),
    (':2/3:',       u'\u2154'),
    (':1/4:',       u'\u00BC'),
    (':3/4:',       u'\u00BE'),

    # Greek letters (lowercase)
    (':alpha:',     u'\u03B1'),
    (':beta:',      u'\u03B2'),
    (':gamma:',     u'\u03B3'),
    (':delta:',     u'\u03B4'),
    (':episilon:',  u'\u03B5'),
    (':zeta:',      u'\u03B6'),
    (':eta:',       u'\u03B7'),
    (':theta:',     u'\u03B8'),
    (':iota:',      u'\u03B9'),
    (':kappa:',     u'\u03BA'),
    (':lambda:',    u'\u03BB'),
    (':mu:',        u'\u03BC'),
    (':nu:',        u'\u03BD'),
    (':xi:',        u'\u03BE'),
    (':omicron:',   u'\u03BF'),
    (':pi:',        u'\u03C0'),
    (':rho:',       u'\u03C1'),
    (':sigma:',     u'\u03C3'),
    (':tau:',       u'\u03C4'),
    (':upsilon:',   u'\u03C5'),
    (':phi:',       u'\u03C6'),
    (':chi:',       u'\u03C7'),
    (':psi:',       u'\u03C8'),
    (':omega:',     u'\u03C9'),

    # Greek letters (uppercase)
    (':Alpha:',     u'\u0391'),
    (':Beta:',      u'\u0392'),
    (':Gamma:',     u'\u0393'),
    (':Delta:',     u'\u0394'),
    (':Episilon:',  u'\u0395'),
    (':Zeta:',      u'\u0396'),
    (':Eta:',       u'\u0397'),
    (':Theta:',     u'\u0398'),
    (':Iota:',      u'\u0399'),
    (':Kappa:',     u'\u039A'),
    (':Lambda:',    u'\u039B'),
    (':Mu:',        u'\u039C'),
    (':Nu:',        u'\u039D'),
    (':Xi:',        u'\u039E'),
    (':Omicron:',   u'\u039F'),
    (':Pi:',        u'\u03A0'),
    (':Rho:',       u'\u03A1'),
    (':Sigma:',     u'\u03A3'),
    (':Tau:',       u'\u03A4'),
    (':Upsilon:',   u'\u03A5'),
    (':Phi:',       u'\u03A6'),
    (':Chi:',       u'\u03A7'),
    (':Psi:',       u'\u03A8'),
    (':Omega:',     u'\u03A9')
]
