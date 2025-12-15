"""
Enrich the normalized concept inventory with English synonyms/meronyms/holonyms
and a few figurative links.

Input: resources/concepts/concepts_v3_2_normalized.jsonl
Output: resources/concepts/concepts_v3_2_enriched.jsonl
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IN_PATH = REPO_ROOT / "resources" / "concepts" / "concepts_v3_2_normalized.jsonl"
OUT_PATH = REPO_ROOT / "resources" / "concepts" / "concepts_v3_2_enriched.jsonl"

# Enrichment payload; keep English-forward and light-touch (no semantic claims).
UPDATES = {
    # Body & Anatomy
    "BODY_01_HEAD": {
        "synonyms_en": ["head", "skull", "crown"],
        "meronyms": ["scalp", "skull", "forehead", "temple", "crown"],
        "holonyms": ["body"],
    },
    "BODY_02_HAIR_(HEAD)": {
        "synonyms_en": ["hair"],
        "meronyms": ["strand", "lock", "root"],
        "holonyms": ["head", "scalp"],
    },
    "BODY_03_EYE": {
        "synonyms_en": ["eye", "eyeball"],
        "meronyms": ["iris", "pupil", "cornea", "sclera", "eyelid", "eyelash", "tear duct"],
        "holonyms": ["face", "head"],
        "figurative_links": [
            {"lang": "ara", "form": "?ayn", "gloss": "spring (of water)", "type": "metonymy"},
            {"lang": "ara", "form": "?ayn", "gloss": "spy/agent", "type": "metonymy"},
        ],
    },
    "BODY_04_EAR": {
        "synonyms_en": ["ear"],
        "meronyms": ["lobe", "ear canal", "eardrum", "pinna"],
        "holonyms": ["head"],
    },
    "BODY_05_NOSE": {
        "synonyms_en": ["nose", "snout"],
        "meronyms": ["bridge", "nostril", "septum", "tip"],
        "holonyms": ["face", "head"],
    },
    "BODY_06_MOUTH": {
        "synonyms_en": ["mouth", "oral cavity"],
        "meronyms": ["lip", "tongue", "teeth", "palate", "gums"],
        "holonyms": ["face", "head"],
    },
    "BODY_07_TOOTH": {
        "synonyms_en": ["tooth"],
        "meronyms": ["crown", "root", "enamel", "dentin"],
        "holonyms": ["mouth", "jaw"],
    },
    "BODY_08_TONGUE": {
        "synonyms_en": ["tongue"],
        "meronyms": ["tip", "blade", "dorsum", "root"],
        "holonyms": ["mouth"],
    },
    "BODY_09_NECK": {
        "synonyms_en": ["neck", "nape"],
        "meronyms": ["throat", "nape"],
        "holonyms": ["body"],
    },
    "BODY_10_SHOULDER": {
        "synonyms_en": ["shoulder"],
        "meronyms": ["blade", "joint", "clavicle"],
        "holonyms": ["arm", "torso"],
    },
    "BODY_11_ARM": {
        "synonyms_en": ["arm"],
        "meronyms": ["upper arm", "forearm", "elbow", "wrist"],
        "holonyms": ["body"],
    },
    "BODY_12_ELBOW": {
        "synonyms_en": ["elbow"],
        "meronyms": ["ulna", "humerus", "joint"],
        "holonyms": ["arm"],
    },
    "BODY_13_HAND": {
        "synonyms_en": ["hand", "palm"],
        "meronyms": ["palm", "thumb", "finger", "knuckle", "wrist"],
        "holonyms": ["arm"],
    },
    "BODY_14_FINGER": {
        "synonyms_en": ["finger", "digit"],
        "meronyms": ["nail", "knuckle", "joint", "tip"],
        "holonyms": ["hand"],
    },
    "BODY_15_NAIL": {
        "synonyms_en": ["nail", "fingernail", "toenail"],
        "meronyms": ["cuticle", "bed", "tip"],
        "holonyms": ["finger", "toe"],
    },
    "BODY_16_CHEST_BREAST": {
        "synonyms_en": ["chest", "breast", "thorax"],
        "meronyms": ["rib", "sternum", "breastbone"],
        "holonyms": ["torso"],
    },
    "BODY_17_BACK": {
        "synonyms_en": ["back"],
        "meronyms": ["spine", "vertebra", "shoulder blade"],
        "holonyms": ["torso"],
    },
    "BODY_18_BELLY_STOMACH": {
        "synonyms_en": ["belly", "stomach", "abdomen"],
        "meronyms": ["navel", "gut"],
        "holonyms": ["torso"],
    },
    "BODY_19_HIP": {
        "synonyms_en": ["hip"],
        "meronyms": ["pelvis", "socket"],
        "holonyms": ["leg", "torso"],
    },
    "BODY_20_LEG": {
        "synonyms_en": ["leg", "limb"],
        "meronyms": ["thigh", "shin", "knee", "ankle"],
        "holonyms": ["body"],
    },
    "BODY_21_KNEE": {
        "synonyms_en": ["knee"],
        "meronyms": ["kneecap", "joint"],
        "holonyms": ["leg"],
    },
    "BODY_22_FOOT": {
        "synonyms_en": ["foot"],
        "meronyms": ["heel", "sole", "arch", "toe", "ankle"],
        "holonyms": ["leg"],
    },
    "BODY_23_BONE": {
        "synonyms_en": ["bone"],
        "meronyms": ["marrow", "shaft", "joint"],
        "holonyms": ["skeleton"],
    },
    "BODY_24_HEART": {
        "synonyms_en": ["heart"],
        "meronyms": ["atrium", "ventricle", "valve"],
        "holonyms": ["chest", "circulatory system"],
    },
    "BODY_25_LUNG": {
        "synonyms_en": ["lung"],
        "meronyms": ["lobe", "bronchus", "alveoli"],
        "holonyms": ["chest", "respiratory system"],
    },
    "BODY_26_LIVER": {
        "synonyms_en": ["liver"],
        "meronyms": ["lobe", "bile duct"],
        "holonyms": ["abdomen"],
    },
    "BODY_27_BLOOD": {
        "synonyms_en": ["blood"],
        "meronyms": ["plasma", "red blood cell", "white blood cell"],
        "holonyms": ["body", "circulatory system"],
    },
    "BODY_28_SKIN_HIDE": {
        "synonyms_en": ["skin", "hide"],
        "meronyms": ["epidermis", "dermis", "pore"],
        "holonyms": ["body"],
    },
    "BODY_29_BRAIN": {
        "synonyms_en": ["brain", "mind"],
        "meronyms": ["cortex", "lobe"],
        "holonyms": ["head"],
    },
    "BODY_30_BREATH": {
        "synonyms_en": ["breath", "respiration"],
        "meronyms": ["inhale", "exhale"],
        "holonyms": ["body"],
    },
    "BODY_31_FAT_GREASE": {
        "synonyms_en": ["fat", "grease"],
        "meronyms": ["tallow", "lard"],
        "holonyms": ["body"],
    },
    "BODY_32_MARROW": {
        "synonyms_en": ["marrow"],
        "meronyms": ["red marrow", "yellow marrow"],
        "holonyms": ["bone"],
    },
    "BODY_33_SWEAT": {
        "synonyms_en": ["sweat", "perspiration"],
        "meronyms": ["drop", "bead"],
        "holonyms": ["body"],
    },
    "BODY_34_TEAR_(EYE)": {
        "synonyms_en": ["tear"],
        "meronyms": ["tear duct", "drop"],
        "holonyms": ["eye"],
    },
    "BODY_35_SALIVA": {
        "synonyms_en": ["saliva", "spit"],
        "meronyms": ["drool", "phlegm"],
        "holonyms": ["mouth"],
    },
    "BODY_36_VOICE": {
        "synonyms_en": ["voice", "speech", "sound"],
        "meronyms": ["tone", "pitch"],
        "holonyms": ["mouth", "throat"],
    },
    # Kinship
    "KIN_01_MOTHER": {"synonyms_en": ["mother", "mom"], "holonyms": ["family"]},
    "KIN_02_FATHER": {"synonyms_en": ["father", "dad"], "holonyms": ["family"]},
    "KIN_03_BROTHER": {"synonyms_en": ["brother", "sib"], "holonyms": ["family"]},
    "KIN_04_SISTER": {"synonyms_en": ["sister", "sib"], "holonyms": ["family"]},
    "KIN_05_SON": {"synonyms_en": ["son"], "holonyms": ["family"]},
    "KIN_06_DAUGHTER": {"synonyms_en": ["daughter"], "holonyms": ["family"]},
    "KIN_07_CHILD_(OFFSPRING)": {"synonyms_en": ["child", "offspring"], "holonyms": ["family"]},
    "KIN_08_PARENT": {"synonyms_en": ["parent"], "holonyms": ["family"]},
    "KIN_09_HUSBAND": {"synonyms_en": ["husband", "spouse"], "holonyms": ["marriage"]},
    "KIN_10_WIFE": {"synonyms_en": ["wife", "spouse"], "holonyms": ["marriage"]},
    "KIN_11_MAN_(MALE_HUMAN)": {"synonyms_en": ["man", "male"], "holonyms": ["people"]},
    "KIN_12_WOMAN_(FEMALE_HUMAN)": {"synonyms_en": ["woman", "female"], "holonyms": ["people"]},
    "KIN_13_PERSON_HUMAN": {"synonyms_en": ["person", "human"], "holonyms": ["people"]},
    "KIN_14_FAMILY": {
        "synonyms_en": ["family", "household"],
        "meronyms": ["parents", "children", "kin"],
        "holonyms": ["clan"],
    },
    "KIN_15_ANCESTOR": {"synonyms_en": ["ancestor", "forefather"], "holonyms": ["lineage"]},
    "KIN_16_TRIBE_CLAN": {"synonyms_en": ["tribe", "clan"], "holonyms": ["people"]},
    # Nature
    "NATURE_01_SUN": {"synonyms_en": ["sun"], "meronyms": ["sunlight", "sunbeam"], "holonyms": ["sky"]},
    "NATURE_02_MOON": {"synonyms_en": ["moon"], "meronyms": ["crescent", "full moon"], "holonyms": ["sky"]},
    "NATURE_03_STAR": {"synonyms_en": ["star"], "holonyms": ["sky"]},
    "NATURE_04_SKY_HEAVEN": {"synonyms_en": ["sky", "heaven"], "holonyms": ["world"]},
    "NATURE_05_EARTH_GROUND_SOIL": {
        "synonyms_en": ["earth", "ground", "soil"],
        "meronyms": ["clod", "dirt"],
        "holonyms": ["world"],
    },
    "NATURE_06_FIRE": {
        "synonyms_en": ["fire", "flame", "blaze"],
        "meronyms": ["flame", "ember", "smoke", "spark"],
        "holonyms": ["hearth"],
    },
    "NATURE_07_WATER": {
        "synonyms_en": ["water"],
        "meronyms": ["drop", "wave", "stream"],
        "holonyms": ["river", "sea", "lake"],
    },
    "NATURE_08_WIND_AIR": {
        "synonyms_en": ["wind", "air", "breeze"],
        "meronyms": ["gust", "breeze"],
        "holonyms": ["weather"],
    },
    "NATURE_09_STONE_ROCK": {
        "synonyms_en": ["stone", "rock"],
        "meronyms": ["pebble", "boulder", "gravel"],
        "holonyms": ["ground"],
    },
    "NATURE_10_MOUNTAIN": {
        "synonyms_en": ["mountain", "mount"],
        "meronyms": ["peak", "ridge", "slope"],
        "holonyms": ["range"],
    },
    "NATURE_11_RIVER_STREAM": {
        "synonyms_en": ["river", "stream"],
        "meronyms": ["source", "mouth", "bank", "current"],
        "holonyms": ["watershed"],
    },
    "NATURE_12_SEA_LAKE": {
        "synonyms_en": ["sea", "lake"],
        "meronyms": ["shore", "wave"],
        "holonyms": ["ocean", "water body"],
    },
    "NATURE_13_TREE": {
        "synonyms_en": ["tree"],
        "meronyms": ["trunk", "branch", "leaf", "root", "bark"],
        "holonyms": ["forest"],
    },
    "NATURE_14_LEAF": {
        "synonyms_en": ["leaf", "foliage"],
        "meronyms": ["blade", "petiole", "vein"],
        "holonyms": ["tree", "plant"],
    },
    "NATURE_15_SEED": {
        "synonyms_en": ["seed", "grain"],
        "meronyms": ["husk", "kernel", "embryo"],
        "holonyms": ["fruit", "plant"],
    },
    "NATURE_16_ROOT_(PLANT)": {
        "synonyms_en": ["root"],
        "meronyms": ["taproot", "fibrous root"],
        "holonyms": ["plant"],
    },
    "NATURE_17_WOOD_(MATERIAL)": {
        "synonyms_en": ["wood", "timber"],
        "meronyms": ["grain", "knot"],
        "holonyms": ["tree"],
    },
    "NATURE_18_GRASS": {
        "synonyms_en": ["grass"],
        "meronyms": ["blade", "turf"],
        "holonyms": ["field", "meadow"],
    },
    "NATURE_19_SAND": {
        "synonyms_en": ["sand"],
        "meronyms": ["grain", "dune"],
        "holonyms": ["desert", "shore"],
    },
    "NATURE_20_CLAY_MUD": {
        "synonyms_en": ["clay", "mud"],
        "meronyms": ["lump", "slurry"],
        "holonyms": ["ground"],
    },
    "NATURE_21_DUST": {"synonyms_en": ["dust"], "meronyms": ["particle", "speck"], "holonyms": ["earth"]},
    "NATURE_22_SMOKE": {"synonyms_en": ["smoke"], "meronyms": ["puff", "cloud"], "holonyms": ["fire"]},
    "NATURE_23_ASH": {"synonyms_en": ["ash"], "meronyms": ["cinder", "soot"], "holonyms": ["fire"]},
    "NATURE_24_RAIN": {
        "synonyms_en": ["rain"],
        "meronyms": ["drop", "shower", "storm"],
        "holonyms": ["weather"],
    },
    "NATURE_25_SNOW_ICE": {
        "synonyms_en": ["snow", "ice"],
        "meronyms": ["flake", "snowdrift", "ice"],
        "holonyms": ["winter"],
    },
    "NATURE_26_THUNDER": {"synonyms_en": ["thunder"], "meronyms": ["peal", "rumble"], "holonyms": ["storm"]},
    "NATURE_27_LIGHTNING": {"synonyms_en": ["lightning", "flash"], "meronyms": ["bolt", "strike"], "holonyms": ["storm"]},
    "NATURE_28_STONE_TOOL_AXE": {"synonyms_en": ["axe", "stone tool"], "meronyms": ["blade", "haft"], "holonyms": ["tool"]},
    # Creatures
    "CREATURE_01_ANIMAL_BEAST_(GENERIC)": {"synonyms_en": ["animal", "beast"], "holonyms": ["fauna"]},
    "CREATURE_02_BIRD": {
        "synonyms_en": ["bird", "fowl"],
        "meronyms": ["wing", "feather", "beak"],
        "holonyms": ["fauna"],
    },
    "CREATURE_03_FISH": {"synonyms_en": ["fish"], "meronyms": ["fin", "scale", "gill"], "holonyms": ["fauna"]},
    "CREATURE_04_SNAKE_SERPENT": {"synonyms_en": ["snake", "serpent"], "meronyms": ["fang", "scale"], "holonyms": ["fauna"]},
    "CREATURE_05_DOG": {"synonyms_en": ["dog", "hound"], "meronyms": ["tail", "paw", "fur"], "holonyms": ["domestic animal"]},
    "CREATURE_06_COW_OX_CATTLE": {"synonyms_en": ["cow", "ox", "cattle"], "meronyms": ["horn", "hoof"], "holonyms": ["livestock"]},
    "CREATURE_07_SHEEP_GOAT": {"synonyms_en": ["sheep", "goat"], "meronyms": ["wool", "horn"], "holonyms": ["livestock"]},
    "CREATURE_08_HORSE": {"synonyms_en": ["horse", "steed"], "meronyms": ["mane", "hoof", "tail"], "holonyms": ["livestock"]},
    "CREATURE_09_DONKEY": {"synonyms_en": ["donkey", "ass"], "meronyms": ["hoof", "mane"], "holonyms": ["livestock"]},
    "CREATURE_10_CAMEL": {"synonyms_en": ["camel"], "meronyms": ["hump", "hoof"], "holonyms": ["livestock"]},
    "CREATURE_11_PIG_BOAR": {"synonyms_en": ["pig", "boar"], "meronyms": ["snout", "tusk"], "holonyms": ["livestock"]},
    "CREATURE_12_CHICKEN_FOWL": {"synonyms_en": ["chicken", "fowl"], "meronyms": ["beak", "wing", "feather"], "holonyms": ["poultry"]},
    "CREATURE_13_BEE": {"synonyms_en": ["bee"], "meronyms": ["sting", "wing"], "holonyms": ["insect"]},
    "CREATURE_14_WOLF": {"synonyms_en": ["wolf"], "meronyms": ["fang", "fur"], "holonyms": ["fauna"]},
    # Time & Space
    "TIME_SPACE_01_DAY": {"synonyms_en": ["day"], "meronyms": ["morning", "noon", "evening"], "holonyms": ["time"]},
    "TIME_SPACE_02_NIGHT": {"synonyms_en": ["night"], "meronyms": ["midnight"], "holonyms": ["time"]},
    "TIME_SPACE_03_YEAR": {"synonyms_en": ["year"], "meronyms": ["season"], "holonyms": ["time"]},
    "TIME_SPACE_04_TIME_(DURATION)": {"synonyms_en": ["time", "duration"], "holonyms": ["timeline"]},
    "TIME_SPACE_05_MORNING": {"synonyms_en": ["morning", "dawn"], "holonyms": ["day"]},
    "TIME_SPACE_06_EVENING": {"synonyms_en": ["evening", "dusk"], "holonyms": ["day"]},
    "TIME_SPACE_07_TODAY_NOW": {"synonyms_en": ["today", "now"], "holonyms": ["time"]},
    "TIME_SPACE_08_YESTERDAY": {"synonyms_en": ["yesterday"], "holonyms": ["time"]},
    "TIME_SPACE_09_TOMORROW": {"synonyms_en": ["tomorrow"], "holonyms": ["time"]},
    "TIME_SPACE_10_BEFORE": {"synonyms_en": ["before", "earlier"], "holonyms": ["sequence"]},
    "TIME_SPACE_11_AFTER": {"synonyms_en": ["after", "later"], "holonyms": ["sequence"]},
    "TIME_SPACE_12_EARLY_SOON": {"synonyms_en": ["early", "soon"], "holonyms": ["time"]},
    "TIME_SPACE_13_LATE": {"synonyms_en": ["late"], "holonyms": ["time"]},
    "TIME_SPACE_14_HERE": {"synonyms_en": ["here"], "holonyms": ["place"]},
    "TIME_SPACE_15_THERE": {"synonyms_en": ["there"], "holonyms": ["place"]},
    "TIME_SPACE_16_NEAR": {"synonyms_en": ["near", "close"], "holonyms": ["distance"]},
    "TIME_SPACE_17_FAR": {"synonyms_en": ["far", "distant"], "holonyms": ["distance"]},
    "TIME_SPACE_18_UP_ABOVE": {"synonyms_en": ["up", "above"], "holonyms": ["direction"]},
    "TIME_SPACE_19_DOWN_BELOW": {"synonyms_en": ["down", "below"], "holonyms": ["direction"]},
    "TIME_SPACE_20_INSIDE": {"synonyms_en": ["inside", "within"], "holonyms": ["location"]},
    "TIME_SPACE_21_OUTSIDE": {"synonyms_en": ["outside", "without"], "holonyms": ["location"]},
    "TIME_SPACE_22_FRONT": {"synonyms_en": ["front", "fore"], "holonyms": ["position"]},
    "TIME_SPACE_23_BACK_(LOCATION)": {"synonyms_en": ["back", "rear"], "holonyms": ["position"]},
    "TIME_SPACE_24_LEFT": {"synonyms_en": ["left"], "holonyms": ["side"]},
    "TIME_SPACE_25_RIGHT": {"synonyms_en": ["right"], "holonyms": ["side"]},
    # Motion & Physical
    "MOTION_01_GO_WALK": {"synonyms_en": ["go", "walk"], "meronyms": ["step", "stride"]},
    "MOTION_02_COME": {"synonyms_en": ["come", "arrive"]},
    "MOTION_03_RUN": {"synonyms_en": ["run", "sprint"]},
    "MOTION_04_ENTER": {"synonyms_en": ["enter", "go in"]},
    "MOTION_05_EXIT_LEAVE": {"synonyms_en": ["exit", "leave", "go out"]},
    "MOTION_06_SIT": {"synonyms_en": ["sit", "sit down"]},
    "MOTION_07_STAND": {"synonyms_en": ["stand", "stand up"]},
    "MOTION_08_LIE_(RECLINE)": {"synonyms_en": ["lie", "recline"]},
    "MOTION_09_FALL": {"synonyms_en": ["fall", "drop"]},
    "MOTION_10_CLIMB": {"synonyms_en": ["climb", "scale"]},
    "MOTION_11_CARRY": {"synonyms_en": ["carry", "bear"]},
    "MOTION_12_BRING": {"synonyms_en": ["bring", "carry to"]},
    "MOTION_13_TAKE": {"synonyms_en": ["take", "grab"]},
    "MOTION_14_GIVE": {"synonyms_en": ["give", "offer"]},
    "MOTION_15_PUT_PLACE": {"synonyms_en": ["put", "place", "set"]},
    "MOTION_16_HOLD": {"synonyms_en": ["hold", "grasp"]},
    "MOTION_17_THROW": {"synonyms_en": ["throw", "cast"]},
    "MOTION_18_HIT_STRIKE": {"synonyms_en": ["hit", "strike"]},
    "MOTION_19_CUT": {"synonyms_en": ["cut", "slice"]},
    "MOTION_20_BREAK": {"synonyms_en": ["break", "shatter"]},
    "MOTION_21_OPEN": {"synonyms_en": ["open", "unlatch"]},
    "MOTION_22_CLOSE": {"synonyms_en": ["close", "shut"]},
    "MOTION_23_FLY": {"synonyms_en": ["fly", "soar"]},
    "MOTION_24_SWIM": {"synonyms_en": ["swim"]},
    # Needs & Actions
    "NEED_01_EAT": {"synonyms_en": ["eat", "consume"]},
    "NEED_02_DRINK": {"synonyms_en": ["drink", "sip"]},
    "NEED_03_BREATHE": {"synonyms_en": ["breathe", "respire"]},
    "NEED_04_SLEEP": {"synonyms_en": ["sleep", "slumber"]},
    "NEED_05_WAKE": {"synonyms_en": ["wake", "awake"]},
    "NEED_06_LIVE_BE_ALIVE": {"synonyms_en": ["live", "be alive"]},
    "NEED_07_DIE": {"synonyms_en": ["die", "perish"]},
    "NEED_08_KILL": {"synonyms_en": ["kill", "slay"]},
    "NEED_09_HUNT": {"synonyms_en": ["hunt", "pursue"]},
    "NEED_10_COOK": {"synonyms_en": ["cook", "prepare food"]},
    "NEED_11_BURN_(TR/INTR)": {"synonyms_en": ["burn", "ignite"]},
    "NEED_12_SPEAK_SAY_TALK": {"synonyms_en": ["speak", "say", "talk"]},
    "NEED_13_HEAR": {"synonyms_en": ["hear", "listen"]},
    "NEED_14_SEE": {"synonyms_en": ["see", "look"]},
    "NEED_15_SMELL": {"synonyms_en": ["smell", "sniff"]},
    "NEED_16_TASTE": {"synonyms_en": ["taste", "savor"]},
    "NEED_17_TOUCH": {"synonyms_en": ["touch", "feel"]},
    "NEED_18_KNOW": {"synonyms_en": ["know", "be aware"]},
    "NEED_19_THINK": {"synonyms_en": ["think", "ponder"]},
    "NEED_20_REMEMBER": {"synonyms_en": ["remember", "recall"]},
    "NEED_21_FORGET": {"synonyms_en": ["forget"]},
    "NEED_22_WANT_DESIRE": {"synonyms_en": ["want", "desire"]},
    "NEED_23_LIKE_LOVE": {"synonyms_en": ["like", "love"]},
    "NEED_24_FEAR": {"synonyms_en": ["fear", "be afraid"]},
    "NEED_25_PAIN_HURT": {"synonyms_en": ["hurt", "pain"]},
    "NEED_26_LAUGH": {"synonyms_en": ["laugh", "giggle"]},
    "NEED_27_CRY_(WEEP)": {"synonyms_en": ["cry", "weep"]},
    "NEED_28_BITE": {"synonyms_en": ["bite", "nip"]},
    "NEED_29_CHEW": {"synonyms_en": ["chew", "masticate"]},
    "NEED_30_SWALLOW": {"synonyms_en": ["swallow", "ingest"]},
    "NEED_31_SPIT": {"synonyms_en": ["spit"], "holonyms": ["mouth"]},
    "NEED_32_URINATE": {"synonyms_en": ["urinate", "pee"]},
    "NEED_33_DEFECATE": {"synonyms_en": ["defecate", "poop"]},
    # Quantity / Quality
    "QUAL_01_ONE": {"synonyms_en": ["one", "single"]},
    "QUAL_02_TWO": {"synonyms_en": ["two"]},
    "QUAL_03_THREE": {"synonyms_en": ["three"]},
    "QUAL_04_FOUR": {"synonyms_en": ["four"]},
    "QUAL_05_FIVE": {"synonyms_en": ["five"]},
    "QUAL_06_SIX": {"synonyms_en": ["six"]},
    "QUAL_07_SEVEN": {"synonyms_en": ["seven"]},
    "QUAL_08_EIGHT": {"synonyms_en": ["eight"]},
    "QUAL_09_NINE": {"synonyms_en": ["nine"]},
    "QUAL_10_TEN": {"synonyms_en": ["ten"]},
    "QUAL_11_ALL": {"synonyms_en": ["all", "every"]},
    "QUAL_12_MANY": {"synonyms_en": ["many", "numerous"]},
    "QUAL_13_FEW": {"synonyms_en": ["few", "some"]},
    "QUAL_14_SOME": {"synonyms_en": ["some", "a few"]},
    "QUAL_15_SAME": {"synonyms_en": ["same", "identical"]},
    "QUAL_16_DIFFERENT": {"synonyms_en": ["different", "other"]},
    "QUAL_17_BIG_LARGE": {"synonyms_en": ["big", "large"]},
    "QUAL_18_SMALL_LITTLE": {"synonyms_en": ["small", "little"]},
    "QUAL_19_LONG": {"synonyms_en": ["long"]},
    "QUAL_20_SHORT": {"synonyms_en": ["short"]},
    "QUAL_21_TALL_HIGH": {"synonyms_en": ["tall", "high"]},
    "QUAL_22_DEEP": {"synonyms_en": ["deep"]},
    "QUAL_23_WIDE_BROAD": {"synonyms_en": ["wide", "broad"]},
    "QUAL_24_NARROW": {"synonyms_en": ["narrow"]},
    "QUAL_25_GOOD": {"synonyms_en": ["good", "fine"]},
    "QUAL_26_BAD_EVIL": {"synonyms_en": ["bad", "evil"]},
    "QUAL_27_HOT": {"synonyms_en": ["hot"]},
    "QUAL_28_COLD": {"synonyms_en": ["cold"]},
    "QUAL_29_WARM": {"synonyms_en": ["warm"]},
    "QUAL_30_COOL": {"synonyms_en": ["cool"]},
    "QUAL_31_NEW": {"synonyms_en": ["new", "fresh"]},
    "QUAL_32_OLD": {"synonyms_en": ["old", "ancient"]},
    "QUAL_33_DRY": {"synonyms_en": ["dry"]},
    "QUAL_34_WET": {"synonyms_en": ["wet", "damp"]},
    "QUAL_35_HEAVY": {"synonyms_en": ["heavy"]},
    "QUAL_36_LIGHT_(WEIGHT)": {"synonyms_en": ["light"]},
    "QUAL_37_HARD": {"synonyms_en": ["hard", "solid"]},
    "QUAL_38_SOFT": {"synonyms_en": ["soft"]},
    "QUAL_39_SHARP": {"synonyms_en": ["sharp"]},
    "QUAL_40_DULL_BLUNT": {"synonyms_en": ["dull", "blunt"]},
    "QUAL_41_FULL": {"synonyms_en": ["full"]},
    "QUAL_42_EMPTY": {"synonyms_en": ["empty"]},
    "QUAL_43_CLEAN": {"synonyms_en": ["clean", "pure"]},
    "QUAL_44_DIRTY": {"synonyms_en": ["dirty", "filthy"]},
    "QUAL_45_WHITE": {"synonyms_en": ["white"]},
    "QUAL_46_BLACK": {"synonyms_en": ["black"]},
    "QUAL_47_RED": {"synonyms_en": ["red"]},
    "QUAL_48_GREEN": {"synonyms_en": ["green"]},
    "QUAL_49_YELLOW": {"synonyms_en": ["yellow"]},
    "QUAL_50_BLUE": {"synonyms_en": ["blue"]},
    "QUAL_51_SWEET": {"synonyms_en": ["sweet"]},
    "QUAL_52_SALTY": {"synonyms_en": ["salty"]},
    "QUAL_53_SOUR": {"synonyms_en": ["sour"]},
    "QUAL_54_BITTER": {"synonyms_en": ["bitter"]},
    # Cultural & Spiritual
    "CULT_01_GOD_DEITY": {"synonyms_en": ["god", "deity"], "holonyms": ["pantheon"]},
    "CULT_02_SPIRIT_SOUL_BREATH": {"synonyms_en": ["spirit", "soul", "breath"], "holonyms": ["body", "afterlife"]},
    "CULT_03_KING_RULER": {"synonyms_en": ["king", "ruler"], "holonyms": ["kingdom"]},
    "CULT_04_SLAVE_SERVANT": {"synonyms_en": ["slave", "servant"], "holonyms": ["household"]},
    "CULT_05_HOUSE_HOME_DWELLING": {
        "synonyms_en": ["house", "home", "dwelling"],
        "meronyms": ["roof", "wall", "door", "window", "floor"],
        "holonyms": ["settlement", "village"],
    },
    "CULT_06_DOOR": {"synonyms_en": ["door", "gate"], "meronyms": ["hinge", "latch"], "holonyms": ["house", "wall"]},
    "CULT_07_WALL": {"synonyms_en": ["wall"], "meronyms": ["brick", "stone"], "holonyms": ["house", "fort"]},
    "CULT_08_PATH_WAY_ROAD": {"synonyms_en": ["path", "road", "track", "way"], "meronyms": ["trail", "lane", "crossing"], "holonyms": ["route network"]},
    "CULT_09_VILLAGE_TOWN": {"synonyms_en": ["village", "town"], "meronyms": ["street", "house", "market"], "holonyms": ["region"]},
    "CULT_10_NAME": {"synonyms_en": ["name", "appellation"], "meronyms": ["letters", "syllables", "sound"], "holonyms": ["identity"]},
    "CULT_11_LAW_RULE_ORDER": {"synonyms_en": ["law", "rule", "order"], "holonyms": ["society"]},
    "CULT_12_TRUTH": {"synonyms_en": ["truth"], "holonyms": ["law", "ethics"]},
    "CULT_13_BREAD_STAPLE_FOOD": {"synonyms_en": ["bread", "loaf"], "meronyms": ["crust", "crumb"], "holonyms": ["meal", "food"]},
    "CULT_14_MEAT": {"synonyms_en": ["meat", "flesh"], "meronyms": ["cut", "piece"], "holonyms": ["food"]},
    "CULT_15_MILK": {"synonyms_en": ["milk"], "holonyms": ["food"]},
    "CULT_16_SALT": {"synonyms_en": ["salt"], "meronyms": ["grain", "crystal"], "holonyms": ["seasoning"]},
    "CULT_17_OIL_FAT": {"synonyms_en": ["oil", "fat"], "holonyms": ["food", "fuel"]},
    "CULT_18_HONEY": {"synonyms_en": ["honey"], "holonyms": ["food"]},
    "CULT_19_BOAT_SHIP": {"synonyms_en": ["boat", "ship"], "meronyms": ["hull", "mast", "oar"], "holonyms": ["fleet"]},
    "CULT_20_FIREPLACE_HEARTH": {"synonyms_en": ["hearth", "fireplace"], "meronyms": ["fire", "ash", "coals"], "holonyms": ["house"]},
    "CULT_21_MARKET_TRADE": {"synonyms_en": ["market", "trade"], "meronyms": ["stall", "vendor"], "holonyms": ["town"]},
    "CULT_22_WAR_BATTLE": {"synonyms_en": ["war", "battle"], "meronyms": ["fight", "campaign"], "holonyms": ["history"]},
    "CULT_23_WEAPON": {"synonyms_en": ["weapon", "arms"], "holonyms": ["war"]},
    "CULT_24_TOOL": {"synonyms_en": ["tool", "implement"], "holonyms": ["work"]},
    "CULT_25_POT_VESSEL": {"synonyms_en": ["pot", "vessel"], "meronyms": ["rim", "handle"], "holonyms": ["kitchen"]},
    # Pronouns & Interrogatives
    "PRONQ_01_I_ME": {"synonyms_en": ["I", "me"]},
    "PRONQ_02_YOU_(SG)": {"synonyms_en": ["you"]},
    "PRONQ_03_HE_SHE_IT": {"synonyms_en": ["he", "she", "it"]},
    "PRONQ_04_WE_(INCLUSIVE/EXCLUSIVE_NOT_MARKED)": {"synonyms_en": ["we", "us"]},
    "PRONQ_05_YOU_(PL)": {"synonyms_en": ["you (pl)"]},
    "PRONQ_06_THEY": {"synonyms_en": ["they"]},
    "PRONQ_07_WHO": {"synonyms_en": ["who"], "holonyms": ["question"]},
    "PRONQ_08_WHAT": {"synonyms_en": ["what"], "holonyms": ["question"]},
    "PRONQ_09_WHERE": {"synonyms_en": ["where"], "holonyms": ["question"]},
    "PRONQ_10_WHEN": {"synonyms_en": ["when"], "holonyms": ["question"]},
    "PRONQ_11_HOW": {"synonyms_en": ["how"], "holonyms": ["question"]},
    "PRONQ_12_WHY": {"synonyms_en": ["why"], "holonyms": ["question"]},
    "PRONQ_13_THIS_(PROXIMAL)": {"synonyms_en": ["this"]},
    "PRONQ_14_THAT_(DISTAL)": {"synonyms_en": ["that"]},
    "PRONQ_15_THESE_(PROX._PL.)": {"synonyms_en": ["these"]},
    "PRONQ_16_THOSE_(DIST._PL.)": {"synonyms_en": ["those"]},
    # Relational & Function Words
    "REL_01_AND": {"synonyms_en": ["and"]},
    "REL_02_OR": {"synonyms_en": ["or"]},
    "REL_03_NOT_NO": {"synonyms_en": ["not", "no"]},
    "REL_04_IF": {"synonyms_en": ["if"]},
    "REL_05_BECAUSE": {"synonyms_en": ["because", "since"]},
    "REL_06_WITH": {"synonyms_en": ["with"]},
    "REL_07_WITHOUT": {"synonyms_en": ["without"]},
    "REL_08_IN_AT_ON": {"synonyms_en": ["in", "at", "on"]},
    "REL_09_FROM": {"synonyms_en": ["from", "out of"]},
    "REL_10_TO_TOWARD": {"synonyms_en": ["to", "toward"]},
    "REL_11_OVER_ABOVE": {"synonyms_en": ["over", "above"]},
    "REL_12_UNDER_BELOW": {"synonyms_en": ["under", "below"]},
    "REL_13_BETWEEN": {"synonyms_en": ["between", "among"]},
    "REL_14_BEFORE_(TIME)": {"synonyms_en": ["before"]},
    "REL_15_AFTER_(TIME)": {"synonyms_en": ["after"]},
    # Possession & Existence
    "POSEX_01_HAVE_POSSESS": {"synonyms_en": ["have", "possess"]},
    "POSEX_02_BE_EXIST": {"synonyms_en": ["be", "exist"]},
    "POSEX_03_OWN_PROPERTY": {"synonyms_en": ["own", "property"], "holonyms": ["possession"]},
    "POSEX_04_BELONG_(TO)": {"synonyms_en": ["belong", "pertain"]},
}


def main() -> None:
    count = 0
    if not IN_PATH.exists():
        raise SystemExit(f"Missing input concepts file: {IN_PATH}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with IN_PATH.open(encoding="utf-8") as f_in, OUT_PATH.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            obj = json.loads(line)
            cid = obj["concept_id"]
            if cid in UPDATES:
                u = UPDATES[cid]
                if "synonyms_en" in u:
                    obj["synonyms_en"] = u["synonyms_en"]
                if "meronyms" in u:
                    obj["meronyms"] = u["meronyms"]
                if "holonyms" in u:
                    obj["holonyms"] = u["holonyms"]
                if "figurative_links" in u:
                    obj["figurative_links"] = u["figurative_links"]
                count += 1
            f_out.write(json.dumps(obj, ensure_ascii=True) + "\n")
    print(f"Concepts updated: {count}")
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
