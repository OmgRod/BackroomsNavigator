class Config:
    CSV_FILES = {
        'fandom-freewriting.csv': 'Fandom Freewriting',
        'fandom.csv': 'Fandom',
        'mghc.csv': 'MGHC',
        'wikidot.csv': 'Wikidot'
    }

    DIFFICULTY_TYPES = {
        '?': 'Undetermined',
        'var': 'Variable',
        'TRANSLATION_ERROR': 'Translation Error',
        '∫': 'Integral',
        '10e': '10e - Environmental',
        'Ω': 'Omega - Livable',
        'N/A': 'N/A',
        'deadzone': 'Deadzone',
        '!': 'Run',
        'ξ': 'Xi',
        'traumatellix': 'Traumatellix',
        '-2': '-2',
    }

    DIFFICULTY_COLORS = {
        '?': 'black',
        'var': 'black',
        'TRANSLATION_ERROR': 'orange',
        '∫': '#bedff0',
        '10e': 'red',
        'Ω': 'purple',
        'N/A': 'green',
        'deadzone': 'black',
        '!': 'red',
        'ξ': 'red,',
        'traumatellix': 'red',
        '-2': '#5bb792',
    }