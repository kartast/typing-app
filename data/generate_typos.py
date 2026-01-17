"""
Generate synthetic MOBILE typo dataset for training.
Simulates realistic iPhone/Android typing errors.

Based on research:
- Aalto University 37k typing study
- Fat finger problem patterns
- Thumb typing error distributions

Mobile typo types:
1. Adjacent key errors (fat finger) - most common
2. Omission (skipped letters) - rushing
3. Insertion (double tap) - bounce errors
4. Transposition (swapped letters) - speed typing
5. Autocorrect failures - wrong word substitution
6. Spacebar errors - missing/extra spaces
7. Capitalization errors - shift key misses

Supports English spelling variants:
- US (American English) - color, organize, center
- UK (British English) - colour, organise, centre
- AU (Australian English) - same as UK
"""

import random
import json
import argparse
import re
from pathlib import Path

# Import English variants support
from english_variants import (
    VARIANT_CONFIG,
    get_sample_sentences,
    convert_sentence_spelling,
    get_protected_words,
    is_protected_word,
    REGIONAL_SENTENCES,
    SHORT_MESSAGES,
    PRESERVED_ABBREVIATIONS,
)


# ============ MOBILE KEYBOARD LAYOUT ============
# Based on standard iPhone/Android QWERTY layout
# Maps each key to its adjacent keys (including diagonal)

MOBILE_ADJACENT_KEYS = {
    # Top row
    'q': ['w', 'a', 's'],
    'w': ['q', 'e', 'a', 's', 'd'],
    'e': ['w', 'r', 's', 'd', 'f'],
    'r': ['e', 't', 'd', 'f', 'g'],
    't': ['r', 'y', 'f', 'g', 'h'],
    'y': ['t', 'u', 'g', 'h', 'j'],
    'u': ['y', 'i', 'h', 'j', 'k'],
    'i': ['u', 'o', 'j', 'k', 'l'],
    'o': ['i', 'p', 'k', 'l'],
    'p': ['o', 'l'],

    # Middle row
    'a': ['q', 'w', 's', 'z', 'x'],
    's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
    'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'],
    'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
    'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'],
    'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
    'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm'],
    'k': ['u', 'i', 'o', 'j', 'l', 'm'],
    'l': ['i', 'o', 'p', 'k'],

    # Bottom row
    'z': ['a', 's', 'x'],
    'x': ['a', 's', 'd', 'z', 'c'],
    'c': ['s', 'd', 'f', 'x', 'v'],
    'v': ['d', 'f', 'g', 'c', 'b'],
    'b': ['f', 'g', 'h', 'v', 'n'],
    'n': ['g', 'h', 'j', 'b', 'm'],
    'm': ['h', 'j', 'k', 'n'],
}

# Probability weights for each error type (based on research)
# Adjacent key errors are most common on mobile
ERROR_WEIGHTS = {
    'adjacent': 0.35,      # Fat finger - hit nearby key
    'omission': 0.20,      # Skip a letter (rushing)
    'insertion': 0.15,     # Double tap / extra letter
    'transposition': 0.15, # Swap two letters (speed)
    'substitution': 0.05,  # Random wrong letter
    'space_error': 0.05,   # Missing/extra space
    'case_error': 0.05,    # Wrong capitalization
}

# Common autocorrect failures (wrong word substituted)
AUTOCORRECT_FAILS = {
    'i': ['u', 'o'],           # "I" often becomes "u" or "o"
    'im': ['in', 'um'],
    'its': ["it's", 'is'],
    "it's": ['its', 'is'],
    'your': ["you're", 'our'],
    "you're": ['your', 'our'],
    'their': ["they're", 'there'],
    'there': ['their', "they're"],
    "they're": ['their', 'there'],
    'to': ['too', 'two', 'yo'],
    'too': ['to', 'two'],
    'were': ['we', 'where', "we're"],
    'where': ['were', 'we'],
    'than': ['then', 'that'],
    'then': ['than', 'the'],
    'know': ['no', 'now'],
    'no': ['know', 'on'],
    'well': ['we', 'will'],
    'will': ['well', 'we'],
    'just': ['dust', 'must'],
    'been': ['be', 'seen'],
    'going': ['doing', 'gong'],
    'doing': ['going', 'soing'],
    'have': ['gave', 'save'],
    'good': ['food', 'god'],
    'like': ['lime', 'live'],
    'make': ['male', 'made'],
    'come': ['cone', 'came'],
    'time': ['tone', 'tire'],
    'take': ['tale', 'tape'],
    'duck': ['fuck'],  # Classic autocorrect fail
    'shot': ['shit'],
    'duck': ['dick'],
    'he': ['be', 'we'],
    'she': ['the', 'be'],
    'are': ['ate', 'ace'],
    'can': ['van', 'cab'],
    'don': ['son', 'con'],
    'for': ['fir', 'got'],
    'got': ['for', 'god'],
    'has': ['had', 'gas'],
    'her': ['het', 'hee'],
    'him': ['his', 'gin'],
    'his': ['him', 'hos'],
    'how': ['hoe', 'row'],
    'man': ['nan', 'mat'],
    'may': ['mat', 'nay'],
    'new': ['few', 'dew'],
    'now': ['not', 'bow'],
    'off': ['of', 'iff'],
    'old': ['ole', 'odd'],
    'one': ['on', 'obe'],
    'our': ['out', 'oir'],
    'out': ['our', 'put'],
    'own': ['pwn', 'oen'],
    'say': ['sat', 'day'],
    'see': ['set', 'bee'],
    'two': ['to', 'teo'],
    'way': ['wat', 'was'],
    'who': ['eho', 'whi'],
    'why': ['ehy', 'whu'],
    'yes': ['yet', 'yea'],
    'get': ['gwt', 'het'],
    'got': ['git', 'hot'],
    'but': ['bit', 'buy'],
    'not': ['nit', 'nor'],
    'all': ['al', 'sll'],
    'use': ['ise', 'sue'],
    'was': ['qas', 'wss'],
    'the': ['thr', 'tue', 'rhe'],
    'and': ['ans', 'abd', 'snd'],
}

# Common thumb-typing word errors (whole word mistakes)
THUMB_TYPING_ERRORS = {
    'the': ['thr', 'tue', 'rhe', 'tge', 'yhe', 'th', 'te'],
    'and': ['ans', 'abd', 'snd', 'amd', 'anf', 'anx', 'nd'],
    'that': ['thar', 'thst', 'rhat', 'yhat', 'tgat', 'thay'],
    'have': ['habe', 'hsve', 'have', 'jave', 'hav', 'havr'],
    'for': ['fir', 'fot', 'gor', 'dor', 'fpr', 'fo'],
    'are': ['ate', 'arr', 'arf', 'sre', 'ae', 'arre'],
    'but': ['bur', 'vut', 'bir', 'nit', 'byt', 'bt'],
    'not': ['nit', 'nor', 'noy', 'mot', 'nof', 'nt'],
    'you': ['yiu', 'tou', 'yoy', 'ypu', 'uou', 'yo'],
    'all': ['sll', 'akk', 'al', 'alll', 'alk'],
    'can': ['csn', 'cab', 'van', 'xan', 'cann', 'cn'],
    'had': ['hsd', 'jad', 'haf', 'hax', 'hadd'],
    'her': ['hee', 'het', 'jer', 'hrr', 'ger'],
    'was': ['wss', 'qas', 'wad', 'eaw', 'wa', 'wass'],
    'one': ['onr', 'obe', 'ine', 'ond', 'on', 'onee'],
    'our': ['oir', 'oyr', 'pur', 'out', 'ou'],
    'out': ['oit', 'put', 'oyt', 'our', 'ot', 'outt'],
    'day': ['dat', 'dau', 'fay', 'dsy', 'dy'],
    'get': ['gwt', 'het', 'ger', 'grt', 'gt', 'gett'],
    'has': ['hss', 'jas', 'hsd', 'gas', 'hs'],
    'him': ['hom', 'hin', 'jim', 'gim', 'hum'],
    'his': ['hos', 'hia', 'jis', 'hiss', 'hs'],
    'how': ['hiw', 'jow', 'hoe', 'gow', 'hw'],
    'its': ['ita', 'irs', 'ots', 'itss', 'ts'],
    'may': ['mat', 'nay', 'msy', 'mau', 'my'],
    'new': ['nee', 'mew', 'nrw', 'bew', 'nw'],
    'now': ['niw', 'mow', 'noe', 'bow', 'nw'],
    'say': ['sat', 'sau', 'ssy', 'aay', 'sy'],
    'two': ['teo', 'twi', 'rwo', 'tw', 'twoo'],
    'way': ['wau', 'wsy', 'eay', 'qay', 'wy'],
    'who': ['whi', 'eho', 'qho', 'wgo', 'wh'],
    'did': ['fid', 'dud', 'didd', 'dd', 'sid'],
    'she': ['shr', 'ahe', 'dhe', 'shee', 'sh'],
    'been': ['bern', 'veen', 'bren', 'ben', 'beenn'],
    'from': ['frim', 'fron', 'feom', 'grom', 'frm'],
    'have': ['habe', 'hsve', 'jave', 'havee', 'hve'],
    'into': ['inti', 'inro', 'intoo', 'unto', 'nto'],
    'just': ['jusr', 'kust', 'jsut', 'jist', 'jst'],
    'like': ['lile', 'likr', 'luke', 'lik', 'loke'],
    'make': ['makr', 'maje', 'nake', 'mke', 'msle'],
    'more': ['mire', 'morr', 'nore', 'mote', 'mre'],
    'only': ['onlt', 'inly', 'omly', 'oly', 'onky'],
    'over': ['iver', 'ovet', 'pver', 'ovee', 'ovr'],
    'such': ['suxh', 'sich', 'suvh', 'sch', 'sucj'],
    'take': ['tske', 'takr', 'rake', 'taje', 'tke'],
    'than': ['tham', 'tjan', 'rhan', 'thn', 'thsn'],
    'them': ['thrm', 'rhem', 'tjem', 'thm', 'tgem'],
    'then': ['tjen', 'rhen', 'thrn', 'thn', 'tgen'],
    'this': ['thia', 'thjs', 'rhis', 'thos', 'ths'],
    'time': ['tine', 'timr', 'rime', 'tume', 'tme'],
    'very': ['vety', 'veru', 'bery', 'vry', 'verg'],
    'want': ['wanr', 'qant', 'wamt', 'wnt', 'wabt'],
    'well': ['wekk', 'qell', 'wrll', 'wll', 'welll'],
    'were': ['wete', 'qere', 'wrer', 'wre', 'weee'],
    'what': ['wjat', 'qhat', 'whst', 'wht', 'whay'],
    'when': ['wjen', 'qhen', 'whrn', 'whn', 'wheb'],
    'will': ['eill', 'wikk', 'qill', 'wil', 'willl'],
    'with': ['woth', 'wirh', 'qith', 'wth', 'wiyh'],
    'word': ['wird', 'worf', 'qord', 'wrd', 'worx'],
    'work': ['wirk', 'wotk', 'qork', 'wrk', 'wprk'],
    'year': ['yeat', 'yesr', 'uear', 'yar', 'yeae'],
    'your': ['yoir', 'ypur', 'uour', 'yor', 'youe'],
    'about': ['aboit', 'sbout', 'abour', 'abt', 'abput'],
    'after': ['aftet', 'sfter', 'afrer', 'aftr', 'aftee'],
    'again': ['agsin', 'sgain', 'agaun', 'agin', 'agaib'],
    'being': ['beinf', 'veing', 'brung', 'bing', 'beibg'],
    'could': ['coild', 'ciuld', 'cpuld', 'cld', 'coudl'],
    'first': ['furst', 'forst', 'dirst', 'frst', 'firat'],
    'great': ['grear', 'gteat', 'grwat', 'grt', 'greay'],
    'never': ['neved', 'mever', 'nevee', 'nvr', 'nevwr'],
    'other': ['othet', 'orher', 'pther', 'othr', 'othee'],
    'right': ['righr', 'roght', 'rugjt', 'rght', 'righy'],
    'still': ['stoll', 'srill', 'atill', 'stll', 'stikl'],
    'thank': ['thabk', 'tjank', 'rhank', 'thnk', 'thsnk'],
    'their': ['theur', 'tjeir', 'rheir', 'thir', 'theie'],
    'there': ['thete', 'tjere', 'rhere', 'thre', 'theee'],
    'these': ['thesw', 'tjese', 'rhese', 'thse', 'thesee'],
    'think': ['thunk', 'tjink', 'rhink', 'thnk', 'thibl'],
    'those': ['thise', 'tjose', 'rhose', 'thse', 'thosee'],
    'three': ['thfee', 'tjree', 'rhree', 'thre', 'threee'],
    'today': ['todat', 'roday', 'todau', 'tday', 'todsy'],
    'under': ['unfer', 'ubder', 'inder', 'undr', 'undee'],
    'water': ['wated', 'qater', 'watee', 'watr', 'watef'],
    'where': ['whete', 'qhere', 'wjere', 'whre', 'wheee'],
    'which': ['whuch', 'qhich', 'wjich', 'whch', 'whicj'],
    'while': ['whike', 'qhile', 'wjile', 'whle', 'whilw'],
    'world': ['wirld', 'qorld', 'wprld', 'wrld', 'worle'],
    'would': ['woukd', 'qould', 'woyld', 'wld', 'woudl'],
    'write': ['wriyr', 'qrite', 'wfite', 'wrte', 'writw'],
    'going': ['goung', 'giing', 'goinf', 'gng', 'goibg'],
    'typing': ['typong', 'tyoing', 'typinf', 'typng', 'typibg'],
    'office': ['offixe', 'iffice', 'offuce', 'offce', 'officw'],
    'because': ['becayse', 'becauae', 'vecause', 'bcause', 'becuase'],
    'people': ['pwople', 'oeople', 'peopke', 'ppl', 'peoplee'],
    'should': ['shoild', 'ahould', 'shpuld', 'shld', 'shoudl'],
    'through': ['thrpugh', 'tjrough', 'throigh', 'thru', 'througj'],
    'hello': ['jello', 'helli', 'hrllo', 'hllo', 'helllo'],
    'message': ['messafe', 'nessage', 'messsgr', 'msg', 'mesaage'],
    'meeting': ['mweting', 'meering', 'neetkng', 'mtng', 'meetibg'],
    'morning': ['mornong', 'norning', 'mornibg', 'mrng', 'mornimg'],
    'thanks': ['tjanks', 'rhanks', 'thsnks', 'thx', 'thankss'],
    'please': ['pleaae', 'olease', 'plesse', 'pls', 'pleasee'],
    'sorry': ['sorrt', 'sirry', 'sorru', 'sry', 'sorrry'],
    'really': ['reall', 'rwally', 'reakky', 'rly', 'reallt'],
    'thing': ['thong', 'thinf', 'rhing', 'thng', 'thibg'],
    'things': ['thongs', 'thinfs', 'rhings', 'thngs', 'thibgs'],
    'something': ['somethong', 'somwthing', 'somerhing', 'smth', 'somethimg'],
    'someone': ['someobe', 'soneone', 'somrone', 'smone', 'someonee'],
    'anything': ['anythong', 'anytjing', 'snything', 'anythng', 'anythimg'],
    'everything': ['everythong', 'everytjing', 'evrrything', 'evrythng', 'everythimg'],
    'nothing': ['nothong', 'notjing', 'borhing', 'nthng', 'nothimg'],
    'i': ['u', 'o', 'k'],  # Very common - I key is small
    'a': ['s', 'q', 'z'],
}

# Spacebar miss patterns (thumb hit nearby keys)
SPACEBAR_ERRORS = {
    'space_to_b': 0.2,   # Hit B instead of space
    'space_to_n': 0.2,   # Hit N instead of space
    'space_to_v': 0.1,   # Hit V instead of space
    'double_space': 0.2, # Double tap spacebar
    'no_space': 0.3,     # Missed spacebar entirely
}


# ============ PROTECTION PATTERNS ============
# Patterns that should NEVER be corrupted

# Regex patterns for protected content
PROTECTED_PATTERNS = [
    # URLs
    re.compile(r'https?://\S+', re.IGNORECASE),
    re.compile(r'www\.\S+', re.IGNORECASE),
    re.compile(r'\S+\.(com|org|net|edu|gov|io|co|app)\b', re.IGNORECASE),

    # Email addresses
    re.compile(r'\S+@\S+\.\S+'),

    # Phone numbers
    re.compile(r'\+?\d[\d\s\-]{7,}\d'),

    # Numbers with units
    re.compile(r'\d+(\.\d+)?\s*(am|pm|kg|lb|km|mi|cm|mm|m|ft|in|oz|ml|l|gb|mb|kb|%|°[cf]?)\b', re.IGNORECASE),

    # Times
    re.compile(r'\d{1,2}:\d{2}(:\d{2})?\s*(am|pm)?', re.IGNORECASE),

    # Dates
    re.compile(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}'),

    # Money
    re.compile(r'[$£€¥₹]\s?\d+(\.\d{2})?'),
    re.compile(r'\d+(\.\d{2})?\s?[$£€¥₹]'),

    # Hashtags and mentions
    re.compile(r'[@#]\w+'),

    # Emojis (basic range)
    re.compile(r'[\U0001F300-\U0001F9FF]'),

    # Code/technical (backticks, common patterns)
    re.compile(r'`[^`]+`'),
]

# Common proper nouns / brand names that should be protected
PROTECTED_PROPER_NOUNS = {
    # Tech companies & products
    'iphone', 'ipad', 'macbook', 'airpods', 'imac', 'ios', 'macos', 'ipados',
    'android', 'samsung', 'galaxy', 'pixel', 'oneplus', 'huawei', 'xiaomi',
    'google', 'gmail', 'youtube', 'chrome', 'chromebook',
    'microsoft', 'windows', 'xbox', 'linkedin', 'github', 'vscode',
    'facebook', 'instagram', 'whatsapp', 'messenger', 'meta',
    'twitter', 'tiktok', 'snapchat', 'discord', 'slack', 'zoom', 'teams',
    'amazon', 'alexa', 'kindle', 'aws', 'netflix', 'spotify', 'uber', 'lyft',
    'airbnb', 'paypal', 'venmo', 'cashapp', 'stripe', 'shopify',
    'tesla', 'spacex', 'openai', 'chatgpt', 'claude', 'anthropic',

    # Apps & Services
    'gmail', 'outlook', 'yahoo', 'hotmail', 'icloud', 'dropbox', 'onedrive',
    'notion', 'figma', 'canva', 'photoshop', 'illustrator', 'premiere',

    # Common names (sample - would be much larger in production)
    'john', 'jane', 'mike', 'david', 'sarah', 'emma', 'james', 'mary',
    'michael', 'jennifer', 'robert', 'linda', 'william', 'elizabeth',

    # Places
    'london', 'paris', 'tokyo', 'singapore', 'sydney', 'melbourne',
    'new york', 'los angeles', 'san francisco', 'seattle', 'chicago',
    'mumbai', 'delhi', 'bangalore', 'manila', 'lagos', 'johannesburg',
    'dublin', 'edinburgh', 'auckland', 'wellington', 'hong kong', 'kuala lumpur',
}


def should_protect_word(word: str, variant: str = None) -> bool:
    """
    Check if a word should be protected from corruption.

    Args:
        word: The word to check
        variant: Regional variant code (for regional particles)

    Returns:
        True if the word should NOT be corrupted
    """
    word_lower = word.lower().strip('.,!?;:\'\"()[]{}')

    # Check if it's a protected abbreviation/slang
    if word_lower in PRESERVED_ABBREVIATIONS:
        return True

    # Check if it's a proper noun
    if word_lower in PROTECTED_PROPER_NOUNS:
        return True

    # Check regional protection
    if is_protected_word(word, variant):
        return True

    # Check if it's a number
    if word_lower.replace('.', '').replace(',', '').isdigit():
        return True

    # Check if it's a single character (likely intentional)
    if len(word_lower) == 1:
        return True

    return False


def find_protected_spans(text: str) -> list:
    """
    Find spans of text that should be protected from corruption.

    Returns:
        List of (start, end) tuples for protected spans
    """
    protected_spans = []

    for pattern in PROTECTED_PATTERNS:
        for match in pattern.finditer(text):
            protected_spans.append((match.start(), match.end()))

    # Merge overlapping spans
    if protected_spans:
        protected_spans.sort()
        merged = [protected_spans[0]]
        for start, end in protected_spans[1:]:
            if start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return merged

    return []


def apply_adjacent_error(char: str) -> str:
    """Replace character with adjacent key (fat finger error)."""
    char_lower = char.lower()
    if char_lower in MOBILE_ADJACENT_KEYS:
        adjacent = random.choice(MOBILE_ADJACENT_KEYS[char_lower])
        return adjacent if char.islower() else adjacent.upper()
    return char


def apply_omission(word: str, pos: int) -> str:
    """Remove a character (skipped while rushing)."""
    if len(word) <= 1:
        return word
    return word[:pos] + word[pos+1:]


def apply_insertion(word: str, pos: int) -> str:
    """Insert an extra character (double tap / bounce)."""
    if pos >= len(word):
        return word
    char = word[pos]
    # Usually doubles the same character or hits adjacent
    if random.random() < 0.6:
        return word[:pos] + char + word[pos:]
    else:
        return word[:pos] + apply_adjacent_error(char) + word[pos:]


def apply_transposition(word: str, pos: int) -> str:
    """Swap two adjacent characters (speed typing)."""
    if pos >= len(word) - 1:
        return word
    chars = list(word)
    chars[pos], chars[pos+1] = chars[pos+1], chars[pos]
    return ''.join(chars)


def corrupt_word_mobile(word: str) -> str:
    """Apply mobile-specific typos to a word."""
    if len(word) <= 1:
        return word

    word_lower = word.lower()

    # Check for known thumb-typing errors first (30% chance)
    if word_lower in THUMB_TYPING_ERRORS and random.random() < 0.3:
        typo = random.choice(THUMB_TYPING_ERRORS[word_lower])
        # Preserve case
        if word[0].isupper() and len(typo) > 0:
            typo = typo[0].upper() + typo[1:]
        if word.isupper():
            typo = typo.upper()
        return typo

    # Otherwise apply random error based on weights
    error_type = random.choices(
        list(ERROR_WEIGHTS.keys()),
        weights=list(ERROR_WEIGHTS.values())
    )[0]

    pos = random.randint(0, len(word) - 1)

    if error_type == 'adjacent':
        chars = list(word)
        chars[pos] = apply_adjacent_error(chars[pos])
        return ''.join(chars)

    elif error_type == 'omission':
        return apply_omission(word, pos)

    elif error_type == 'insertion':
        return apply_insertion(word, pos)

    elif error_type == 'transposition':
        return apply_transposition(word, pos)

    elif error_type == 'substitution':
        chars = list(word)
        # Random letter (rare error)
        chars[pos] = random.choice('abcdefghijklmnopqrstuvwxyz')
        return ''.join(chars)

    elif error_type == 'case_error':
        chars = list(word)
        chars[pos] = chars[pos].swapcase()
        return ''.join(chars)

    return word


def corrupt_text_mobile(text: str, error_rate: float = 0.20, variant: str = None) -> str:
    """
    Corrupt text with realistic mobile typing errors.

    Args:
        text: Clean input text
        error_rate: Probability of error per word (0.15-0.25 is realistic)
        variant: Regional variant code (to protect regional particles)

    Returns:
        Text with mobile typos
    """
    words = text.split()
    result_words = []

    for i, word in enumerate(words):
        # Separate punctuation
        prefix = ''
        suffix = ''
        core = word

        while core and not core[0].isalnum():
            prefix += core[0]
            core = core[1:]
        while core and not core[-1].isalnum():
            suffix = core[-1] + suffix
            core = core[:-1]

        # Check if word should be protected
        if should_protect_word(core, variant):
            result_words.append(prefix + core + suffix)
            continue

        # Apply word-level error
        if core and random.random() < error_rate:
            core = corrupt_word_mobile(core)

        # Spacebar errors (between words)
        if i > 0 and random.random() < 0.03:
            space_error = random.choices(
                list(SPACEBAR_ERRORS.keys()),
                weights=list(SPACEBAR_ERRORS.values())
            )[0]

            if space_error == 'no_space':
                # Join with previous word
                if result_words:
                    result_words[-1] = result_words[-1] + prefix + core + suffix
                    continue
            elif space_error == 'double_space':
                result_words.append('')  # Extra space
            elif space_error in ['space_to_b', 'space_to_n', 'space_to_v']:
                char = space_error[-1]
                result_words.append(char)

        result_words.append(prefix + core + suffix)

    result = ' '.join(result_words)

    # First letter lowercase (forgot shift) - common on mobile
    if result and random.random() < 0.15:
        result = result[0].lower() + result[1:]

    # Random punctuation errors
    if random.random() < 0.1:
        result = result.replace(',', '')
    if random.random() < 0.05:
        result = result.replace('.', '')
    if random.random() < 0.05:
        result = result.replace("'", '')

    return result


# ============ SAMPLE SENTENCES ============
# Expanded set of realistic messages

SAMPLE_SENTENCES = [
    # Greetings and small talk
    "Hello, how are you? I am fine, thank you.",
    "Hey, what's up? How's it going?",
    "Good morning! Hope you have a great day.",
    "Hi there! Nice to hear from you.",
    "How are you doing today?",

    # Work related
    "Today I am going to the office to work on a new project.",
    "I have a meeting at three o'clock this afternoon.",
    "Can you send me the report by end of day?",
    "Let me know when you're free to discuss this.",
    "I'll follow up with you tomorrow morning.",
    "The deadline has been extended to next Friday.",
    "Please review the document and provide feedback.",
    "I'm working from home today.",
    "Can we reschedule our meeting to next week?",
    "I'll be out of office next Monday.",

    # Casual messages
    "I am typing this message hoping the AI can understand me.",
    "Just wanted to check in and see how you're doing.",
    "Are you free for lunch tomorrow?",
    "Let me know if you need anything.",
    "Thanks for your help with this!",
    "Sorry for the late reply, been super busy.",
    "That sounds great, count me in!",
    "No worries, take your time.",
    "I'll get back to you as soon as I can.",
    "Can you please call me when you get a chance?",

    # Common phrases
    "The quick brown fox jumps over the lazy dog.",
    "Can you please help me with this problem?",
    "I would like to schedule a meeting for tomorrow.",
    "Thank you for your help with this issue.",
    "I think we should discuss this further.",
    "Let me know if you have any questions.",
    "I will send you the document later today.",
    "I am looking forward to hearing from you soon.",

    # Questions
    "What time does the meeting start?",
    "Where should we meet for dinner?",
    "Did you get my last message?",
    "When will you be available?",
    "Can you explain this to me?",
    "Why did you change the plan?",
    "How long will this take?",
    "Who is coming to the party?",

    # Statements
    "I forgot my phone at home.",
    "The weather is beautiful today.",
    "I need to finish this by tonight.",
    "Everything is going according to plan.",
    "Something came up and I have to cancel.",
    "I really appreciate your patience.",
    "This is taking longer than expected.",
    "I completely understand your concern.",

    # Mobile-specific contexts
    "Running late, be there in ten minutes.",
    "On my way now, see you soon.",
    "Just got your message, calling you back.",
    "Battery is dying, talk later.",
    "Bad signal here, might cut out.",
    "Can't talk right now, text me.",
    "Send me the address please.",
    "What's the wifi password?",
    "My phone is almost dead.",
    "I'll text you when I arrive.",

    # Longer messages
    "I wanted to follow up on our conversation from yesterday about the project timeline.",
    "Please let me know if there's anything else you need from me before the meeting.",
    "I apologize for any inconvenience this may have caused you.",
    "Looking forward to seeing everyone at the event this weekend.",
    "Just finished the presentation, ready for tomorrow's meeting.",
]


def generate_dataset(num_samples: int = 10000, error_rate: float = 0.20, variant: str = 'US',
                     clean_sample_ratio: float = 0.10, variable_error_rate: bool = True,
                     variants_per_sample: int = 1) -> list:
    """
    Generate dataset of (corrupted, clean) text pairs.

    Args:
        num_samples: Number of samples to generate
        error_rate: Base rate of errors per word
        variant: English spelling variant (US, UK, AU, SG, MY, IN, PH, NG, ZA, HK, IE, SC, NZ)
        clean_sample_ratio: Ratio of samples with NO typos (teaches model not to over-correct)
        variable_error_rate: Whether to vary error rate per sample
        variants_per_sample: Number of different typo variants to generate per clean sample

    Returns:
        List of {"input": corrupted, "output": clean} dicts
    """
    dataset = []

    # Get variant-specific sentences (includes regional + short messages)
    variant_sentences = get_sample_sentences(variant, include_regional=True, include_short=True)

    # Also get base sentences with spelling conversion
    config = VARIANT_CONFIG.get(variant, VARIANT_CONFIG['US'])
    spelling = config.get('spelling', 'US')
    base_sentences = [convert_sentence_spelling(s, spelling) for s in SAMPLE_SENTENCES]

    # Combine all sentences
    all_sentences = list(set(variant_sentences + base_sentences))

    # Error rate distribution for variety (if variable)
    error_rates = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35] if variable_error_rate else [error_rate]
    error_weights = [0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.05] if variable_error_rate else [1.0]

    for i in range(num_samples):
        # Pick a random sentence
        clean = random.choice(all_sentences)

        # Determine if this should be a clean sample (no typos)
        if random.random() < clean_sample_ratio:
            # Clean sample - input equals output (only add once, not multiple variants)
            dataset.append({
                "input": clean,
                "output": clean,
                "variant": variant,
                "typo_type": "none"
            })
        else:
            # Generate multiple typo variants for this clean sample
            generated_variants = set()  # Track to avoid duplicates

            for v in range(variants_per_sample):
                # Select error rate for this variant
                sample_error_rate = random.choices(error_rates, weights=error_weights)[0]

                # Corrupt with mobile typos
                corrupted = corrupt_text_mobile(clean, error_rate=sample_error_rate, variant=variant)

                # Ensure it's actually different (retry if needed)
                attempts = 0
                while (corrupted == clean or corrupted in generated_variants) and attempts < 5:
                    corrupted = corrupt_text_mobile(clean, error_rate=sample_error_rate + 0.10, variant=variant)
                    attempts += 1

                # Only add if unique
                if corrupted not in generated_variants:
                    generated_variants.add(corrupted)
                    dataset.append({
                        "input": corrupted,
                        "output": clean,
                        "variant": variant,
                        "typo_type": "corrupted" if corrupted != clean else "none"
                    })

        if (i + 1) % 1000 == 0:
            total_expected = num_samples * variants_per_sample
            print(f"Processed {i + 1}/{num_samples} samples ({len(dataset)} pairs)...")

    return dataset


def save_dataset(dataset: list, output_path: str):
    """Save dataset to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    print(f"Saved {len(dataset)} samples to {output_path}")


def main():
    # All supported variants
    ALL_VARIANTS = list(VARIANT_CONFIG.keys())

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate mobile typo training data for English spelling variants'
    )
    parser.add_argument(
        '--variant', '-v',
        type=str,
        default='US',
        choices=ALL_VARIANTS + ['ALL'],
        help=f'English variant: {", ".join(ALL_VARIANTS)}, or ALL'
    )
    parser.add_argument(
        '--train-samples', '-t',
        type=int,
        default=10000,
        help='Number of training samples (default: 10000)'
    )
    parser.add_argument(
        '--eval-samples', '-e',
        type=int,
        default=1000,
        help='Number of evaluation samples (default: 1000)'
    )
    parser.add_argument(
        '--error-rate', '-r',
        type=float,
        default=0.22,
        help='Base error rate per word (default: 0.22)'
    )
    parser.add_argument(
        '--clean-ratio', '-c',
        type=float,
        default=0.10,
        help='Ratio of clean (no typo) samples (default: 0.10)'
    )
    parser.add_argument(
        '--variable-error-rate',
        action='store_true',
        default=True,
        help='Use variable error rates per sample (default: True)'
    )
    parser.add_argument(
        '--fixed-error-rate',
        action='store_true',
        help='Use fixed error rate instead of variable'
    )
    parser.add_argument(
        '--variants-per-sample', '-n',
        type=int,
        default=1,
        help='Number of typo variants to generate per clean sample (default: 1). Use 2-3 for better model robustness.'
    )
    args = parser.parse_args()

    # Handle fixed vs variable error rate
    variable_error_rate = not args.fixed_error_rate

    print("=== Generating Mobile Typo Dataset ===\n")
    print("Simulating iPhone/Android typing errors:\n")
    print("  - Fat finger (adjacent key) errors")
    print("  - Omissions (skipped letters)")
    print("  - Insertions (double taps)")
    print("  - Transpositions (swapped letters)")
    print("  - Spacebar misses")
    print("  - Autocorrect-style errors")
    print()
    print("Robustness features:")
    print(f"  - Clean samples ratio: {args.clean_ratio:.0%}")
    print(f"  - Variable error rates: {variable_error_rate}")
    print(f"  - Variants per sample: {args.variants_per_sample}")
    print("  - Protected: numbers, URLs, emails, emojis, slang, regional particles")
    print()

    data_dir = Path(__file__).parent

    # Determine which variants to generate
    if args.variant == 'ALL':
        variants = ALL_VARIANTS
        print(f"Generating data for ALL {len(variants)} variants:")
        for v in variants:
            print(f"  - {v}: {VARIANT_CONFIG[v]['name']}")
    else:
        variants = [args.variant]
        variant_name = VARIANT_CONFIG.get(args.variant, {}).get('name', args.variant)
        print(f"Generating data for: {variant_name}")

    print()

    all_train_data = []
    all_eval_data = []

    for variant in variants:
        variant_name = VARIANT_CONFIG.get(variant, {}).get('name', variant)
        print(f"\n--- {variant_name} ({variant}) ---")

        # Adjust sample count when generating multiple variants
        train_count = args.train_samples if len(variants) == 1 else args.train_samples // len(variants)
        eval_count = args.eval_samples if len(variants) == 1 else args.eval_samples // len(variants)

        # Ensure minimum samples per variant
        train_count = max(train_count, 100)
        eval_count = max(eval_count, 50)

        # Generate training data
        print(f"Generating training data ({train_count} samples × {args.variants_per_sample} variants)...")
        train_data = generate_dataset(
            num_samples=train_count,
            error_rate=args.error_rate,
            variant=variant,
            clean_sample_ratio=args.clean_ratio,
            variable_error_rate=variable_error_rate,
            variants_per_sample=args.variants_per_sample
        )

        # Generate evaluation data (always 1 variant for eval - cleaner metrics)
        print(f"Generating evaluation data ({eval_count} samples)...")
        eval_data = generate_dataset(
            num_samples=eval_count,
            error_rate=args.error_rate,
            variant=variant,
            clean_sample_ratio=args.clean_ratio,
            variable_error_rate=variable_error_rate,
            variants_per_sample=1  # Single variant for eval
        )

        all_train_data.extend(train_data)
        all_eval_data.extend(eval_data)

        # Save individual variant files if generating ALL
        if len(variants) > 1:
            save_dataset(train_data, data_dir / f"train_data_{variant.lower()}.json")
            save_dataset(eval_data, data_dir / f"eval_data_{variant.lower()}.json")

    # Shuffle combined data
    if len(variants) > 1:
        random.shuffle(all_train_data)
        random.shuffle(all_eval_data)

    # Save main datasets
    save_dataset(all_train_data, data_dir / "train_data.json")
    save_dataset(all_eval_data, data_dir / "eval_data.json")

    # Show examples
    print("\n" + "="*60)
    print("SAMPLE TRAINING PAIRS")
    print("="*60 + "\n")

    # Show diverse examples (different variants and typo types)
    examples_shown = 0
    shown_variants = set()
    shown_types = set()

    # First show one clean sample and one corrupted from each variant
    for sample in all_train_data:
        if examples_shown >= 15:
            break

        variant = sample.get('variant', 'US')
        typo_type = sample.get('typo_type', 'corrupted')

        # Try to show diversity
        key = (variant, typo_type)
        if key in shown_types and examples_shown >= len(variants) * 2:
            continue

        shown_types.add(key)
        shown_variants.add(variant)
        examples_shown += 1

        variant_label = f"[{variant}]" if len(variants) > 1 else ""
        type_label = " (clean)" if typo_type == "none" else ""
        print(f"Example {examples_shown} {variant_label}{type_label}:")
        print(f"  Input:  {sample['input']}")
        print(f"  Output: {sample['output']}")
        print()

    # Count statistics
    clean_count = sum(1 for s in all_train_data if s.get('typo_type') == 'none')
    corrupted_count = len(all_train_data) - clean_count

    print("\n=== Summary ===")
    print(f"Total training samples: {len(all_train_data)}")
    print(f"  - Clean (no typo): {clean_count} ({clean_count/len(all_train_data)*100:.1f}%)")
    print(f"  - Corrupted: {corrupted_count} ({corrupted_count/len(all_train_data)*100:.1f}%)")
    print(f"Total evaluation samples: {len(all_eval_data)}")
    print(f"Variants included: {', '.join(variants)}")
    print(f"Files saved to: {data_dir}")


if __name__ == "__main__":
    main()
