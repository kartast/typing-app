"""
English Spelling Variants & Regional Expressions
=================================================

Supports English spelling systems and regional expressions from:
- American English (US) - USA, Canada (mostly)
- British English (UK) - UK, EU, Malta
- Australian English (AU) - Australia
- New Zealand English (NZ) - New Zealand
- Singapore English (SG) - Singapore (Singlish)
- Malaysian English (MY) - Malaysia (Manglish)
- Indian English (IN) - India
- Philippine English (PH) - Philippines
- Nigerian English (NG) - Nigeria
- South African English (ZA) - South Africa
- Hong Kong English (HK) - Hong Kong
- Irish English (IE) - Ireland
- Scottish English (SC) - Scotland

Focus:
1. SPELLING DIFFERENCES - color vs colour, organize vs organise
2. PROTECTED EXPRESSIONS - Regional particles that should NOT be "corrected"
3. The model fixes TYPOS only, not grammar or dialect features
"""

# ============ SPELLING VARIANTS ============

SPELLING_US_TO_UK = {
    # -or vs -our
    'color': 'colour',
    'colors': 'colours',
    'colored': 'coloured',
    'coloring': 'colouring',
    'favor': 'favour',
    'favors': 'favours',
    'favored': 'favoured',
    'favorite': 'favourite',
    'favorites': 'favourites',
    'flavor': 'flavour',
    'flavors': 'flavours',
    'flavored': 'flavoured',
    'harbor': 'harbour',
    'harbors': 'harbours',
    'honor': 'honour',
    'honors': 'honours',
    'honored': 'honoured',
    'honoring': 'honouring',
    'humor': 'humour',
    'humors': 'humours',
    'labor': 'labour',
    'labors': 'labours',
    'labored': 'laboured',
    'laboring': 'labouring',
    'neighbor': 'neighbour',
    'neighbors': 'neighbours',
    'neighboring': 'neighbouring',
    'neighborhood': 'neighbourhood',
    'rumor': 'rumour',
    'rumors': 'rumours',
    'savior': 'saviour',
    'saviors': 'saviours',
    'behavior': 'behaviour',
    'behaviors': 'behaviours',
    'endeavor': 'endeavour',
    'endeavors': 'endeavours',

    # -er vs -re
    'center': 'centre',
    'centers': 'centres',
    'centered': 'centred',
    'centering': 'centring',
    'theater': 'theatre',
    'theaters': 'theatres',
    'meter': 'metre',
    'meters': 'metres',
    'liter': 'litre',
    'liters': 'litres',
    'fiber': 'fibre',
    'fibers': 'fibres',
    'caliber': 'calibre',
    'somber': 'sombre',
    'specter': 'spectre',
    'scepter': 'sceptre',
    'luster': 'lustre',
    'meager': 'meagre',

    # -ize vs -ise (US prefers -ize, UK accepts both but -ise common)
    'organize': 'organise',
    'organizes': 'organises',
    'organized': 'organised',
    'organizing': 'organising',
    'organization': 'organisation',
    'organizations': 'organisations',
    'recognize': 'recognise',
    'recognizes': 'recognises',
    'recognized': 'recognised',
    'recognizing': 'recognising',
    'realize': 'realise',
    'realizes': 'realises',
    'realized': 'realised',
    'realizing': 'realising',
    'apologize': 'apologise',
    'apologizes': 'apologises',
    'apologized': 'apologised',
    'analyze': 'analyse',
    'analyzes': 'analyses',
    'analyzed': 'analysed',
    'analyzing': 'analysing',
    'paralyze': 'paralyse',
    'paralyzed': 'paralysed',
    'criticize': 'criticise',
    'criticizes': 'criticises',
    'criticized': 'criticised',
    'customize': 'customise',
    'customizes': 'customises',
    'customized': 'customised',
    'minimize': 'minimise',
    'minimizes': 'minimises',
    'minimized': 'minimised',
    'maximize': 'maximise',
    'maximizes': 'maximises',
    'maximized': 'maximised',
    'optimize': 'optimise',
    'optimizes': 'optimises',
    'optimized': 'optimised',
    'prioritize': 'prioritise',
    'prioritizes': 'prioritises',
    'prioritized': 'prioritised',
    'authorize': 'authorise',
    'authorizes': 'authorises',
    'authorized': 'authorised',
    'summarize': 'summarise',
    'summarizes': 'summarises',
    'summarized': 'summarised',
    'memorize': 'memorise',
    'memorizes': 'memorises',
    'memorized': 'memorised',
    'categorize': 'categorise',
    'categorizes': 'categorises',
    'categorized': 'categorised',
    'standardize': 'standardise',
    'standardized': 'standardised',
    'specialize': 'specialise',
    'specializes': 'specialises',
    'specialized': 'specialised',
    'visualize': 'visualise',
    'visualized': 'visualised',
    'finalize': 'finalise',
    'finalized': 'finalised',
    'utilize': 'utilise',
    'utilized': 'utilised',

    # -se vs -ce (noun/verb differences)
    'defense': 'defence',
    'offense': 'offence',
    'license': 'licence',  # UK: licence (noun), license (verb)
    'practice': 'practise',  # UK: practice (noun), practise (verb)
    'pretense': 'pretence',

    # -og vs -ogue
    'catalog': 'catalogue',
    'catalogs': 'catalogues',
    'dialog': 'dialogue',
    'dialogs': 'dialogues',
    'analog': 'analogue',
    'monolog': 'monologue',
    'prolog': 'prologue',
    'epilog': 'epilogue',

    # -ment
    'judgment': 'judgement',
    'judgments': 'judgements',
    'acknowledgment': 'acknowledgement',
    'acknowledgments': 'acknowledgements',

    # -led vs -lled (US single L, UK double L)
    'traveled': 'travelled',
    'traveling': 'travelling',
    'traveler': 'traveller',
    'travelers': 'travellers',
    'canceled': 'cancelled',
    'canceling': 'cancelling',
    'labeled': 'labelled',
    'labeling': 'labelling',
    'modeled': 'modelled',
    'modeling': 'modelling',
    'counselor': 'counsellor',
    'counselors': 'counsellors',
    'jeweler': 'jeweller',
    'jewelers': 'jewellers',
    'fueled': 'fuelled',
    'fueling': 'fuelling',
    'leveled': 'levelled',
    'leveling': 'levelling',
    'signaled': 'signalled',
    'signaling': 'signalling',
    'dialed': 'dialled',
    'dialing': 'dialling',
    'marveled': 'marvelled',
    'marveling': 'marvelling',
    'marvelous': 'marvellous',

    # Other common differences
    'gray': 'grey',
    'grays': 'greys',
    'program': 'programme',  # UK: programme (TV/event), program (computer)
    'programs': 'programmes',
    'check': 'cheque',  # UK: cheque (bank), check (verify)
    'checks': 'cheques',
    'tire': 'tyre',
    'tires': 'tyres',
    'airplane': 'aeroplane',
    'airplanes': 'aeroplanes',
    'pajamas': 'pyjamas',
    'mom': 'mum',
    'moms': 'mums',
    'draft': 'draught',  # UK: draught (beer/air), draft (document)
    'drafts': 'draughts',
    'plow': 'plough',
    'plows': 'ploughs',
    'plowed': 'ploughed',
    'skeptic': 'sceptic',
    'skeptics': 'sceptics',
    'skeptical': 'sceptical',
    'donut': 'doughnut',
    'donuts': 'doughnuts',
    'curb': 'kerb',
    'curbs': 'kerbs',
    'fulfill': 'fulfil',
    'fulfills': 'fulfils',
    'fulfilled': 'fulfilled',
    'skillful': 'skilful',
    'willful': 'wilful',
    'enrollment': 'enrolment',
    'enrollments': 'enrolments',
    'installment': 'instalment',
    'installments': 'instalments',
    'fulfill': 'fulfil',
    'aging': 'ageing',
    'routing': 'routeing',
    'artifact': 'artefact',
    'artifacts': 'artefacts',
    'medieval': 'mediaeval',
    'maneuver': 'manoeuvre',
    'maneuvers': 'manoeuvres',
    'maneuvered': 'manoeuvred',
    'pediatric': 'paediatric',
    'pediatrics': 'paediatrics',
    'orthopedic': 'orthopaedic',
    'anesthetic': 'anaesthetic',
    'anesthesia': 'anaesthesia',
    'estrogen': 'oestrogen',
    'fetus': 'foetus',
    'diarrhea': 'diarrhoea',
    'leukemia': 'leukaemia',
    'edema': 'oedema',
    'encyclopedia': 'encyclopaedia',
    'archeology': 'archaeology',
    'ax': 'axe',
    'cozy': 'cosy',
    'licorice': 'liquorice',
    'molt': 'moult',
    'mustache': 'moustache',
    'omelet': 'omelette',
    'smolder': 'smoulder',
    'story': 'storey',  # UK: storey (building floor), story (narrative)
    'stories': 'storeys',
}

# Build reverse mapping (UK to US)
SPELLING_UK_TO_US = {v: k for k, v in SPELLING_US_TO_UK.items()}


# ============ VARIANT CONFIGURATION ============

VARIANT_CONFIG = {
    'US': {
        'name': 'American English',
        'markets': ['USA', 'Canada'],
        'spelling': 'US',
        'protected': [],  # No special particles
    },
    'UK': {
        'name': 'British English',
        'markets': ['UK', 'EU', 'Malta'],
        'spelling': 'UK',
        'protected': ['innit', 'bloody', 'blimey', 'cheers', 'mate', 'rubbish', 'dodgy', 'gobsmacked', 'chuffed'],
    },
    'AU': {
        'name': 'Australian English',
        'markets': ['Australia'],
        'spelling': 'UK',
        'protected': ['arvo', 'servo', 'bottle-o', 'smoko', 'brekkie', 'barbie', 'sunnies', 'thongs',
                      'mate', 'reckon', 'heaps', 'keen', 'no worries', 'strewth', 'crikey', 'fair dinkum',
                      'bogan', 'drongo', 'sheila', 'bloke', 'ripper', 'stoked', 'sicko', 'maccas'],
    },
    'NZ': {
        'name': 'New Zealand English',
        'markets': ['New Zealand'],
        'spelling': 'UK',
        'protected': ['bro', 'cuz', 'sweet as', 'choice', 'chur', 'yeah nah', 'nah yeah', 'mint',
                      'mean', 'hard out', 'all good', 'ka pai', 'kia ora', 'whanau', 'tamariki',
                      'tiki tour', 'tramping', 'jandals', 'dairy', 'bach'],
    },
    'SG': {
        'name': 'Singapore English (Singlish)',
        'markets': ['Singapore'],
        'spelling': 'UK',
        'protected': ['lah', 'leh', 'lor', 'meh', 'hor', 'sia', 'liao', 'ah', 'one', 'already',
                      'can', 'cannot', 'got', 'never', 'still got', 'how come', 'is it', 'steady',
                      'shiok', 'sian', 'blur', 'kiasu', 'kiasi', 'paiseh', 'bojio', 'jialat',
                      'alamak', 'wah', 'walao', 'aiyo', 'aiyah', 'oi', 'eh', 'hah', 'makan',
                      'chope', 'lepak', 'kopi', 'teh', 'tabao', 'dabao', 'hawker', 'kopitiam',
                      'ang moh', 'gahmen', 'atas', 'sua ku', 'act blur', 'kena', 'arrow',
                      'sabo', 'wayang', 'on', 'off', 'ownself', 'liddat', 'likdat', 'machiam'],
    },
    'MY': {
        'name': 'Malaysian English (Manglish)',
        'markets': ['Malaysia'],
        'spelling': 'UK',
        'protected': ['lah', 'mah', 'lor', 'leh', 'meh', 'one', 'got', 'already', 'can', 'cannot',
                      'wei', 'woi', 'eh', 'aiyo', 'aiyoh', 'walao', 'yalor', 'haiya', 'aiya',
                      'boss', 'macha', 'dei', 'macam', 'cincai', 'gostan', 'jalan', 'makan',
                      'mamak', 'tapau', 'yum cha', 'kaw kaw', 'terror', 'geng', 'syok',
                      'action', 'outstation', 'lepak', 'yamcha', 'potong', 'cabut', 'kantoi'],
    },
    'IN': {
        'name': 'Indian English',
        'markets': ['India', 'Nepal', 'Bangladesh'],
        'spelling': 'UK',
        'protected': ['yaar', 'yar', 'na', 'no', 'hai', 'haan', 'ji', 'arey', 'arre', 'arrey',
                      'accha', 'achha', 'theek', 'thik', 'bas', 'chalo', 'kya', 'bhai', 'didi',
                      'uncle', 'aunty', 'auntie', 'beta', 'beti', 'babu', 'sahib', 'ji',
                      'prepone', 'revert', 'do the needful', 'kindly', 'intimate', 'passed out',
                      'mugging', 'timepass', 'eve teasing', 'godown', 'lakh', 'crore',
                      'dabba', 'dabbawala', 'pukka', 'jugaad', 'bindaas', 'fundoo', 'bakwas',
                      'timepass', 'tension', 'funda', 'gyaan', 'desi', 'firangi', 'gora'],
    },
    'PH': {
        'name': 'Philippine English',
        'markets': ['Philippines'],
        'spelling': 'US',  # Philippines uses American spelling
        'protected': ['po', 'opo', 'ho', 'naman', 'ba', 'daw', 'raw', 'pala', 'kasi', 'talaga',
                      'ano', 'di ba', 'diba', 'ganun', 'ganon', 'edi', 'sige', 'ge', 'hala',
                      'ay', 'nako', 'sus', 'hay', 'aba', 'aray', 'lodi', 'petmalu', 'werpa',
                      'for a while', 'open the light', 'close the light', 'CR', 'comfort room',
                      'ref', 'aircon', 'brownout', 'blow out', 'despedida', 'merienda',
                      'balikbayan', 'pasalubong', 'utang na loob', 'kilig', 'gigil', 'basta'],
    },
    'NG': {
        'name': 'Nigerian English',
        'markets': ['Nigeria', 'Ghana', 'West Africa'],
        'spelling': 'UK',
        'protected': ['abi', 'sha', 'shaa', 'sef', 'o', 'oh', 'na', 'dey', 'wey', 'wetin',
                      'wahala', 'gist', 'gisting', 'yawa', 'chop', 'dash', 'kolo', 'craze',
                      'japa', 'sabi', 'no wahala', 'e go be', 'how far', 'how body', 'bros',
                      'oga', 'madam', 'abeg', 'biko', 'jare', 'ehen', 'ehn', 'shey', 'oya',
                      'ginger', 'pepper', 'strong thing', 'enter', 'drop', 'pick', 'flash',
                      'okada', 'danfo', 'keke', 'mama put', 'buka', 'suya', 'small chops',
                      'ashewo', 'packaging', 'shakara', 'flex', 'slay', 'on point', 'gbas gbos'],
    },
    'ZA': {
        'name': 'South African English',
        'markets': ['South Africa', 'Namibia', 'Zimbabwe'],
        'spelling': 'UK',
        'protected': ['lekker', 'kiff', 'kif', 'sharp', 'shap', 'eish', 'eina', 'ag', 'shame',
                      'ja', 'nee', 'dankie', 'baie', 'braai', 'bru', 'boet', 'china', 'oke',
                      'dof', 'dwaal', 'gatvol', 'now now', 'just now', 'robot', 'circle',
                      'bakkie', 'tackies', 'takkies', 'slops', 'howzit', 'yebo', 'aikona',
                      'ubuntu', 'sangoma', 'toyi-toyi', 'vuvuzela', 'braai', 'potjie',
                      'bunny chow', 'boerewors', 'biltong', 'rooibos', 'moerse', 'lank'],
    },
    'HK': {
        'name': 'Hong Kong English',
        'markets': ['Hong Kong', 'Macau'],
        'spelling': 'UK',
        'protected': ['lah', 'ah', 'la', 'lor', 'leh', 'geh', 'meh', 'wor', 'ga', 'ge',
                      'add oil', 'fighting', 'aiya', 'aiyo', 'wah', 'haiya',
                      'siu mai', 'char siu', 'dim sum', 'yum cha', 'dai pai dong',
                      'wet market', 'MTR', 'octopus', 'minibus', 'ding ding',
                      'helper', 'domestic helper', 'expat', 'gweilo', 'ABC', 'BBC',
                      'can', 'cannot', 'got', 'have', 'play', 'do', 'make'],
    },
    'IE': {
        'name': 'Irish English (Hiberno)',
        'markets': ['Ireland'],
        'spelling': 'UK',
        'protected': ['grand', 'craic', 'crack', 'fierce', 'deadly', 'gas', 'sound', 'class',
                      'yer man', 'yer one', 'yer wan', 'himself', 'herself', 'bold', 'press',
                      'messages', 'runners', 'jumper', 'minerals', 'banjaxed', 'knackered',
                      'eejit', 'gobshite', 'feck', 'acting the maggot', 'giving out',
                      'what way', 'amnt', 'tis', 'twas', 'yoke', 'yera', 'ara', 'sure look',
                      'slainte', 'cead mile failte', 'go raibh maith agat', 'ta', 'nil'],
    },
    'SC': {
        'name': 'Scottish English',
        'markets': ['Scotland'],
        'spelling': 'UK',
        'protected': ['aye', 'nae', 'wee', 'braw', 'bonnie', 'ken', 'kent', 'dinna', 'didnae',
                      'cannae', 'willnae', 'wouldnae', 'shouldnae', 'havnae', 'isnae', 'wasnae',
                      'och', 'hoots', 'wheesht', 'blether', 'haver', 'scunner', 'crabbit',
                      'dreich', 'glaikit', 'numpty', 'bampot', 'radge', 'bairn', 'lad', 'lass',
                      'loch', 'ben', 'brae', 'kirk', 'croft', 'burn', 'glen', 'strath',
                      'tattie', 'neep', 'haggis', 'hogmanay', 'ceilidh', 'slàinte'],
    },
}

# All protected words across all variants (for quick lookup)
ALL_PROTECTED_WORDS = set()
for config in VARIANT_CONFIG.values():
    ALL_PROTECTED_WORDS.update(word.lower() for word in config.get('protected', []))


# ============ SAMPLE SENTENCES ============
# Generic sentences that work for any variant (spelling will be converted)

SAMPLE_SENTENCES = [
    # Daily communication
    "I'll meet you at the center of town.",
    "What's your favorite color?",
    "The theater is just around the corner.",
    "Can you organize the meeting for tomorrow?",
    "I realized I left my phone at home.",
    "Let me check my schedule and get back to you.",
    "The neighbor's dog has been barking all night.",
    "I need to apologize for being late.",
    "She has a great sense of humor.",
    "The program starts at eight o'clock.",

    # Work/professional
    "We need to finalize the report by Friday.",
    "Can you summarize the main points?",
    "The team analyzed the data carefully.",
    "I'll authorize the payment today.",
    "Let's prioritize the urgent tasks.",
    "The organization is planning a restructure.",
    "We should optimize the workflow.",
    "I recognize that this is challenging.",
    "The defense team prepared their case.",
    "Please catalog all the items.",

    # Travel/daily life
    "I traveled to London last summer.",
    "The airplane landed on time.",
    "Check the tire pressure before driving.",
    "The draft is coming through the window.",
    "She wore her favorite pajamas.",
    "The jewelry store is closed today.",
    "I need to refuel the car.",
    "The counselor gave good advice.",
    "It was a gray and cloudy day.",
    "Mom is coming to visit next week.",

    # Casual conversation
    "That donut looks delicious.",
    "I'm skeptical about the results.",
    "The movie was marvelous.",
    "He has a thick mustache.",
    "I made an omelet for breakfast.",
    "The building has ten stories.",
    "Let me fulfill your request.",
    "She's very skillful at her job.",
    "The artifact was found in Egypt.",
    "They maneuvered through traffic.",
]

# ============ REGIONAL SAMPLE SENTENCES ============
# Sentences with regional expressions (these won't be spell-converted)

REGIONAL_SENTENCES = {
    'SG': [
        # Singlish expressions
        "This one very shiok lah!",
        "Wah, the queue so long sia.",
        "Can help me chope this seat ah?",
        "Later go makan, you want?",
        "Aiyo, I so blur today.",
        "Don't be so kiasu lah.",
        "Why you never tell me earlier leh?",
        "This place damn atas one.",
        "Aiyah, kena arrow again.",
        "Wa lao eh, so jialat.",
        "You eat already or not?",
        "The kopitiam downstairs got good kopi.",
        "I paiseh to ask him leh.",
        "This one macam not right lor.",
        "Ok lah, I do it myself.",
        "Today very sian, nothing to do.",
        "You bojio me go!",
        "Steady lah bro!",
        "How come liddat one?",
        "Is it? I didn't know sia.",
    ],
    'MY': [
        # Manglish expressions
        "Wah, this food damn terror lah!",
        "Boss, one teh tarik please.",
        "Let's go mamak later lah.",
        "Aiyo, so mahal one this.",
        "Can or not? I need answer now.",
        "Wei, you going where ah?",
        "Haiya, traffic jam again.",
        "This one cincai do can already lah.",
        "Let's lepak at my place.",
        "Don't action so much lah.",
        "I outstation next week.",
        "Gostan a bit, you blocking me.",
        "Syok sendiri only you.",
        "Why you so geng one?",
        "Yalor, I also think so.",
        "Jom yamcha tonight!",
        "Faster lah, we late already.",
        "This curry kaw kaw one.",
        "He kantoi already, everyone knows.",
        "Potong stim lah you.",
    ],
    'IN': [
        # Indian English expressions
        "Please do the needful and revert back.",
        "I will intimate you once done.",
        "The meeting got preponed to 2 PM.",
        "Arey yaar, what happened?",
        "Accha, I understand now.",
        "One second, I am coming only.",
        "What is your good name?",
        "Kindly adjust a little bit.",
        "I passed out from IIT in 2015.",
        "He's doing timepass only.",
        "This is very tension giving.",
        "Let me give you some gyaan on this.",
        "Chalo, let's go now.",
        "Bas, that's enough.",
        "Theek hai, no problem.",
        "Uncle, can you help me?",
        "This is very fundoo idea yaar.",
        "He's a total bakwas person.",
        "I am having some doubts.",
        "My cousin brother is coming today.",
    ],
    'PH': [
        # Filipino English expressions
        "Wait lang po, for a while.",
        "Sige, I'll do it na.",
        "Can you open the light please?",
        "The CR is over there.",
        "Ay nako, I forgot again!",
        "It's so traffic outside.",
        "I'll get my ref and bring some food.",
        "There's a brownout in our area.",
        "We had a blow out for her birthday.",
        "Did you bring pasalubong?",
        "I'm so kilig right now!",
        "This makes me gigil!",
        "Basta, just do it.",
        "That's so petmalu, lodi!",
        "Talaga? I didn't know that.",
        "Kasi, I was busy eh.",
        "Edi wow, good for you.",
        "Hala, we're late!",
        "Close the aircon, it's cold.",
        "I have a despedida party next week.",
    ],
    'NG': [
        # Nigerian English expressions
        "How far, my guy?",
        "No wahala, we go sort am.",
        "Abeg, help me with this.",
        "The thing dey pepper me sha.",
        "Oya, make we go!",
        "Wetin you dey do?",
        "E go be, no worry.",
        "This gist is too much!",
        "Bros, I dey come.",
        "That one na wahala o.",
        "Shey you understand?",
        "Na so the thing be.",
        "I wan chop something.",
        "Make we go mama put.",
        "This suya is on point!",
        "Ehen, I remember now.",
        "Oga, please help me.",
        "You sabi this thing well well.",
        "Dem dey ginger me.",
        "I don japa already.",
    ],
    'ZA': [
        # South African English expressions
        "Howzit my china!",
        "That braai was lekker!",
        "Eish, what a mission.",
        "I'll do it now now.",
        "Just now I was there.",
        "Sharp sharp, see you later.",
        "This place is moerse nice.",
        "Stop at the robot please.",
        "I'm gatvol with this traffic.",
        "Shame, that's so sad.",
        "Ja nee, it's complicated.",
        "The biltong here is kiff.",
        "Let me get my takkies.",
        "I came with my bakkie.",
        "This boerewors is baie lekker!",
        "Ag man, don't stress.",
        "That oke is a bit dof.",
        "I'm in a dwaal today.",
        "Yebo, I agree with you.",
        "We need more ubuntu here.",
    ],
    'HK': [
        # Hong Kong English expressions
        "Add oil! You can do it!",
        "Let's go yum cha tomorrow.",
        "Take the MTR, it's faster.",
        "The wet market closes early.",
        "Aiya, I forgot my octopus card!",
        "The ding ding is very slow.",
        "My helper is on leave today.",
        "This char siu is amazing lah!",
        "Wah, so expensive ah!",
        "Can can, no problem.",
        "Fighting! Good luck!",
        "Let's eat at the dai pai dong.",
        "The dim sum here is good ge.",
        "I'm an ABC, born in America.",
        "That gweilo speaks Cantonese!",
        "The minibus is faster lor.",
        "Got time or not?",
        "This one very nice wor.",
        "Haiya, so troublesome.",
        "The siu mai here is the best!",
    ],
    'IE': [
        # Irish English expressions
        "Ah sure, it'll be grand.",
        "The craic was mighty last night!",
        "That's pure gas altogether.",
        "Yer man over there said so.",
        "I'm absolutely knackered.",
        "Stop acting the maggot!",
        "She's always giving out about something.",
        "What way are you going?",
        "That's a deadly idea!",
        "The young fella is being bold.",
        "I need to get the messages.",
        "Put on your runners, we're late.",
        "Get us some minerals from the shop.",
        "The car is totally banjaxed.",
        "That yoke over there is broken.",
        "Yera, don't worry about it.",
        "Sure look, it is what it is.",
        "Your one from down the road.",
        "Tis a fierce cold day.",
        "Sláinte! Good health to you!",
    ],
    'SC': [
        # Scottish English expressions
        "Aye, I ken what you mean.",
        "That's a braw wee idea!",
        "Och, dinnae worry about it.",
        "The bairn is sleeping upstairs.",
        "She's a bonnie lass.",
        "I cannae do that right now.",
        "Wheesht! Be quiet!",
        "Stop your blethering!",
        "That's pure brilliant, pal!",
        "The weather's awfy dreich today.",
        "He's a right numpty.",
        "Are you coming to the ceilidh?",
        "Let's go up the ben.",
        "The burn is running high today.",
        "I'm fair scunnered with this.",
        "She's in a crabbit mood.",
        "That's a glaikit thing to say.",
        "Happy Hogmanay everyone!",
        "The kirk is just up the brae.",
        "I'll have some tatties and neeps.",
    ],
    'AU': [
        # Australian English expressions
        "G'day mate, how's it going?",
        "No worries, she'll be right!",
        "That's fair dinkum, mate.",
        "Let's have a barbie this arvo.",
        "I'm heading to the servo.",
        "Grab some snags for the barbie.",
        "Strewth, that was close!",
        "He's a bit of a drongo.",
        "That sheila is really nice.",
        "This is heaps good!",
        "I reckon we should go.",
        "I'm absolutely stoked!",
        "Let's go to Maccas.",
        "Crikey, look at that!",
        "Put on your sunnies, it's bright.",
        "I left my thongs at the beach.",
        "That bloke is a ripper!",
        "Time for smoko.",
        "Let's grab a bottle-o run.",
        "I'm keen as mustard!",
    ],
    'NZ': [
        # New Zealand English expressions
        "Sweet as, bro!",
        "Chur, thanks for that.",
        "That's pretty choice, aye.",
        "Yeah nah, I'm not sure.",
        "Nah yeah, let's do it!",
        "That feed was mean as!",
        "All good, no drama.",
        "Hard out, that was intense!",
        "Ka pai! Well done!",
        "Kia ora, welcome everyone!",
        "We're going tramping this weekend.",
        "Grab your jandals, we're going to the beach.",
        "Let's go to the dairy for some milk.",
        "We're staying at the bach.",
        "That's a mint car, bro!",
        "Whanau is coming over for dinner.",
        "The tamariki are playing outside.",
        "Let's do a tiki tour around town.",
        "Choice bro, see you later.",
        "That's pretty mean, cuz!",
    ],
    'UK': [
        # British English expressions
        "Cheers mate, appreciate it!",
        "That's absolutely brilliant!",
        "Blimey, that was unexpected!",
        "Don't talk rubbish.",
        "That seems a bit dodgy to me.",
        "I'm gobsmacked by the news!",
        "I'm well chuffed with the result.",
        "Fancy a cuppa?",
        "That's proper good, innit?",
        "I'm knackered, need some sleep.",
        "Let's pop to the shops.",
        "I'll ring you later.",
        "Queueing is a way of life here.",
        "The telly is on too loud.",
        "I'm going to the loo.",
        "That's a load of codswallop!",
        "I'm feeling a bit poorly today.",
        "Mind the gap please.",
        "Lovely weather for ducks!",
        "Sorted, we're all good now.",
    ],
    'US': [
        # American English expressions (standard)
        "What's up, how's it going?",
        "That's awesome, dude!",
        "I'm gonna grab some coffee.",
        "Let's hang out this weekend.",
        "That's totally cool with me.",
        "I'm good, thanks for asking.",
        "We should totally do that.",
        "No worries, it's all good.",
        "I'm super excited about this!",
        "Let me check my schedule real quick.",
        "I gotta run, catch you later!",
        "That's so sick, bro!",
        "We're grabbing some takeout.",
        "I'll shoot you a text later.",
        "That's lit, for real!",
        "I'm down for whatever.",
        "Let's bounce, it's getting late.",
        "I'm so done with this.",
        "That slaps, honestly.",
        "No cap, that was amazing.",
    ],
}

# ============ SHORT MESSAGES & SLANG ============
# Universal short messages that work across all variants

SHORT_MESSAGES = [
    # Ultra short (1-3 words)
    "ok", "okay", "k", "kk", "yep", "yup", "nope", "nah", "ya", "yeah", "yes", "no",
    "sure", "cool", "nice", "great", "thanks", "thx", "ty", "np", "yw", "please", "pls",
    "sorry", "sry", "hi", "hey", "hello", "bye", "later", "soon", "now", "wait",
    "omw", "otw", "brb", "brt", "ttyl", "gtg", "g2g", "lol", "lmao", "haha", "hehe",
    "idk", "idc", "imo", "imho", "tbh", "nvm", "jk", "ikr", "smh", "fyi", "btw", "asap",
    "omg", "wtf", "wth", "rn", "atm", "fr", "ngl", "ong", "bet", "facts", "true", "same",
    "mood", "vibes", "slay", "fire", "goat", "goated", "bussin", "cap", "no cap", "lowkey",
    "highkey", "sus", "based", "mid", "lit", "valid", "bet", "word", "say less", "less",

    # Short phrases (4-8 words)
    "sounds good", "sounds great", "all good", "no problem", "no worries", "got it",
    "on my way", "be right there", "be there soon", "running late", "almost there",
    "see you soon", "see you later", "talk later", "call you later", "text me",
    "let me know", "keep me posted", "what's up", "how are you", "you good",
    "wanna hang", "wanna come", "you down", "i'm down", "count me in", "i'm in",
    "can't make it", "maybe later", "rain check", "next time", "my bad", "all good",
    "no rush", "take your time", "whenever you can", "when you're free",
    "good morning", "good night", "sleep well", "have fun", "good luck", "congrats",
    "happy birthday", "thank you so much", "appreciate it", "means a lot",
    "miss you", "love you", "thinking of you", "checking in", "just checking",
    "quick question", "one sec", "hold on", "coming", "leaving now", "here",
    "where are you", "you there", "anyone home", "hello?", "you up",
]

# Common abbreviations that should be preserved (not "corrected")
PRESERVED_ABBREVIATIONS = {
    # Text speak
    'u': 'u', 'r': 'r', 'ur': 'ur', 'y': 'y', 'n': 'n', 'k': 'k', 'b': 'b',
    'pls': 'pls', 'plz': 'plz', 'thx': 'thx', 'thnx': 'thnx', 'ty': 'ty', 'yw': 'yw',
    'np': 'np', 'sry': 'sry', 'bc': 'bc', 'cuz': 'cuz', 'tho': 'tho', 'rn': 'rn',
    'tmr': 'tmr', 'tmrw': 'tmrw', 'tn': 'tn', 'ytd': 'ytd', 'msg': 'msg',
    'mins': 'mins', 'secs': 'secs', 'hrs': 'hrs', 'wks': 'wks',

    # Common acronyms
    'omw': 'omw', 'otw': 'otw', 'brb': 'brb', 'brt': 'brt', 'ttyl': 'ttyl',
    'gtg': 'gtg', 'g2g': 'g2g', 'lol': 'lol', 'lmao': 'lmao', 'rofl': 'rofl',
    'idk': 'idk', 'idc': 'idc', 'imo': 'imo', 'imho': 'imho', 'tbh': 'tbh',
    'nvm': 'nvm', 'jk': 'jk', 'ikr': 'ikr', 'smh': 'smh', 'fyi': 'fyi',
    'btw': 'btw', 'asap': 'asap', 'omg': 'omg', 'wtf': 'wtf', 'wth': 'wth',
    'afk': 'afk', 'irl': 'irl', 'fomo': 'fomo', 'yolo': 'yolo', 'tmi': 'tmi',
    'dm': 'dm', 'pm': 'pm', 'hmu': 'hmu', 'lmk': 'lmk', 'wyd': 'wyd', 'hbu': 'hbu',
    'ily': 'ily', 'ilysm': 'ilysm', 'bff': 'bff', 'bf': 'bf', 'gf': 'gf',

    # Casual contractions
    'gonna': 'gonna', 'wanna': 'wanna', 'gotta': 'gotta', 'kinda': 'kinda',
    'sorta': 'sorta', 'dunno': 'dunno', 'lemme': 'lemme', 'gimme': 'gimme',
    'gotcha': 'gotcha', 'whatcha': 'whatcha', 'coulda': 'coulda', 'shoulda': 'shoulda',
    'woulda': 'woulda', 'oughta': 'oughta', 'hafta': 'hafta', 'outta': 'outta',
    'tryna': 'tryna', 'finna': 'finna', 'boutta': 'boutta', 'imma': 'imma',

    # Gen-Z slang
    'fr': 'fr', 'ngl': 'ngl', 'ong': 'ong', 'lowkey': 'lowkey', 'highkey': 'highkey',
    'sus': 'sus', 'bussin': 'bussin', 'slay': 'slay', 'goated': 'goated',
    'mid': 'mid', 'based': 'based', 'valid': 'valid', 'bet': 'bet', 'cap': 'cap',
    'nocap': 'nocap', 'rizz': 'rizz', 'simp': 'simp', 'stan': 'stan', 'vibe': 'vibe',
    'yeet': 'yeet', 'sheesh': 'sheesh', 'bruh': 'bruh', 'fam': 'fam', 'lit': 'lit',
}


def get_spelling_for_variant(word: str, variant: str = 'US') -> str:
    """
    Convert a word to the specified English variant spelling.

    Args:
        word: The word to convert
        variant: 'US', 'UK', or 'AU'

    Returns:
        Word with appropriate spelling for the variant
    """
    word_lower = word.lower()
    is_capitalized = word[0].isupper() if word else False
    is_upper = word.isupper() if word else False

    if variant == 'US':
        # Convert UK spelling to US if found
        if word_lower in SPELLING_UK_TO_US:
            result = SPELLING_UK_TO_US[word_lower]
        else:
            result = word_lower
    elif variant in ['UK', 'AU']:
        # Convert US spelling to UK if found
        if word_lower in SPELLING_US_TO_UK:
            result = SPELLING_US_TO_UK[word_lower]
        else:
            result = word_lower
    else:
        result = word_lower

    # Preserve original capitalization
    if is_upper:
        return result.upper()
    elif is_capitalized:
        return result.capitalize()
    return result


def convert_sentence_spelling(sentence: str, variant: str = 'US') -> str:
    """
    Convert all words in a sentence to the specified variant spelling.

    Args:
        sentence: The sentence to convert
        variant: 'US', 'UK', or 'AU'

    Returns:
        Sentence with appropriate spelling for the variant
    """
    words = sentence.split()
    converted = []

    for word in words:
        # Handle punctuation
        prefix = ''
        suffix = ''
        core = word

        # Extract leading punctuation
        while core and not core[0].isalnum():
            prefix += core[0]
            core = core[1:]

        # Extract trailing punctuation
        while core and not core[-1].isalnum():
            suffix = core[-1] + suffix
            core = core[:-1]

        # Convert the core word
        if core:
            core = get_spelling_for_variant(core, variant)

        converted.append(prefix + core + suffix)

    return ' '.join(converted)


def get_sample_sentences(variant: str = 'US', include_regional: bool = True, include_short: bool = True) -> list:
    """
    Get sample sentences for the specified variant.

    Args:
        variant: Regional variant code (US, UK, AU, SG, MY, IN, PH, NG, ZA, HK, IE, SC, NZ)
        include_regional: Whether to include regional expressions
        include_short: Whether to include short messages/slang

    Returns:
        List of sentences appropriate for the variant
    """
    sentences = []

    # Add base sentences with spelling conversion
    config = VARIANT_CONFIG.get(variant, VARIANT_CONFIG['US'])
    spelling = config.get('spelling', 'US')
    sentences.extend([convert_sentence_spelling(s, spelling) for s in SAMPLE_SENTENCES])

    # Add regional sentences (no spelling conversion - they're already correct)
    if include_regional and variant in REGIONAL_SENTENCES:
        sentences.extend(REGIONAL_SENTENCES[variant])

    # Add short messages (universal)
    if include_short:
        sentences.extend(SHORT_MESSAGES)

    return sentences


def get_protected_words(variant: str = None) -> set:
    """
    Get protected words that should not be spell-corrected.

    Args:
        variant: Regional variant code, or None for all protected words

    Returns:
        Set of protected words (lowercase)
    """
    if variant is None:
        return ALL_PROTECTED_WORDS | set(PRESERVED_ABBREVIATIONS.keys())

    protected = set(PRESERVED_ABBREVIATIONS.keys())
    config = VARIANT_CONFIG.get(variant)
    if config:
        protected.update(word.lower() for word in config.get('protected', []))

    return protected


def is_protected_word(word: str, variant: str = None) -> bool:
    """
    Check if a word should be protected from spell-correction.

    Args:
        word: The word to check
        variant: Regional variant code, or None to check all variants

    Returns:
        True if the word should be preserved as-is
    """
    word_lower = word.lower().strip('.,!?;:\'\"')
    protected = get_protected_words(variant)
    return word_lower in protected


# ============ DEMO ============

if __name__ == "__main__":
    print("=== English Spelling Variants ===\n")
    print("Supported variants:")
    for code, config in VARIANT_CONFIG.items():
        markets = ', '.join(config['markets'])
        print(f"  {code}: {config['name']} ({markets})")

    print("\n\n=== Spelling Conversions ===")
    test_words = ['color', 'organize', 'center', 'favorite', 'traveled', 'gray']
    print(f"\n{'Word':<15} {'US':<15} {'UK':<15}")
    print("-" * 45)
    for word in test_words:
        us = get_spelling_for_variant(word, 'US')
        uk = get_spelling_for_variant(word, 'UK')
        print(f"{word:<15} {us:<15} {uk:<15}")

    print("\n\n=== Sample Sentences ===")
    test_sentence = "I realized my favorite color is gray."
    print(f"\nOriginal: {test_sentence}")
    print(f"US:       {convert_sentence_spelling(test_sentence, 'US')}")
    print(f"UK:       {convert_sentence_spelling(test_sentence, 'UK')}")

    print(f"\nTotal spelling pairs: {len(SPELLING_US_TO_UK)}")
