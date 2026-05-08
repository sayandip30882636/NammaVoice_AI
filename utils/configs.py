import os

# Helper to load .env manually (zero external dependencies, fully robust)
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip and not line_strip.startswith("#") and "=" in line_strip:
                key, val = line_strip.split("=", 1)
                os.environ[key.strip()] = val.strip()

# API Keys loaded from .env environment variables
DEFAULT_DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")
DEFAULT_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


# Bangalore Localities list for locality extraction & fuzzy matching
BANGALORE_LOCALITIES = [
    "Koramangala", "Indiranagar", "Whitefield", "Electronic City", "Marathahalli",
    "Jayanagar", "Rajajinagar", "Hebbal", "Yelahanka", "Banashankari",
    "HSR Layout", "BTM Layout", "Majestic", "Silk Board", "Bellandur",
    "Sarjapur", "Bommanahalli", "KR Puram", "Peenya", "Yeshwanthpur",
    "Byatarayanapura", "Kadugondanahalli", "Hesaraghatta", "Chikkabanavara",
    "Rajarajeshwarinagar", "Kothanur Dinne", "Thanisandra", "Doddanekundi",
    "Kengeri Upanagara", "Thalaghattapura"
]

# Audio Samples Configuration
# Each sample represents a distinct real-world hiring/telephony scenario
PRELOADED_SAMPLES = {
    "sample_1": {
        "filename": "01_koramangala_quiet.wav",
        "title": "Koramangala - Candidate Intro",
        "condition": "Quiet Room",
        "ground_truth": "I'm looking for a job as a delivery boy near Koramangala, can you help?",
        "expected_localities": ["Koramangala"]
    },
    "sample_2": {
        "filename": "02_indiranagar_quiet.wav",
        "title": "Indiranagar - Previous Work",
        "condition": "Quiet Room",
        "ground_truth": "Mera pichla kaam Indiranagar mein tha, ab naya dhoond raha hoon.",
        "expected_localities": ["Indiranagar"]
    },
    "sample_3": {
        "filename": "03_whitefield_traffic.wav",
        "title": "Whitefield - Traffic Delay",
        "condition": "Traffic Noise",
        "ground_truth": "Sir, I am stuck in traffic near Whitefield, will reach in 10 minutes.",
        "expected_localities": ["Whitefield"]
    },
    "sample_4": {
        "filename": "04_electronic_city_traffic.wav",
        "title": "Electronic City - Heavy Traffic",
        "condition": "Traffic Noise",
        "ground_truth": "Electronic City ke raste mein bahut bheed hai, order late ho jayega.",
        "expected_localities": ["Electronic City"]
    },
    "sample_5": {
        "filename": "05_marathahalli_phone.wav",
        "title": "Marathahalli - Pickup Query",
        "condition": "Phone-call Quality",
        "ground_truth": "Main abhi Marathahalli signal pe hoon, pickup kahan se karna hai?",
        "expected_localities": ["Marathahalli"]
    },
    "sample_6": {
        "filename": "06_jayanagar_phone.wav",
        "title": "Jayanagar - Arrival Info",
        "condition": "Phone-call Quality",
        "ground_truth": "Jayanagar office ke pass pahunch gaya hoon, interview kab start hoga?",
        "expected_localities": ["Jayanagar"]
    },
    "sample_7": {
        "filename": "07_hsr_layout_rushed.wav",
        "title": "HSR Layout - Fast Delivery",
        "condition": "Rushed Speech",
        "ground_truth": "I'm heading to HSR Layout for the delivery, please keep the gate open.",
        "expected_localities": ["HSR Layout"]
    },
    "sample_8": {
        "filename": "08_btm_layout_rushed.wav",
        "title": "BTM Layout - Customer Unreachable",
        "condition": "Rushed Speech",
        "ground_truth": "BTM Layout pahunch gaya hoon, customer ka phone nahi lag raha.",
        "expected_localities": ["BTM Layout"]
    },
    "sample_9": {
        "filename": "09_majestic_whispered.wav",
        "title": "Majestic - Station Update",
        "condition": "Whispered Speech",
        "ground_truth": "Abhi Majestic station pe hoon, train thodi late hai.",
        "expected_localities": ["Majestic"]
    },
    "sample_10": {
        "filename": "10_silk_board_traffic.wav",
        "title": "Silk Board - Infinite Signal",
        "condition": "Traffic Noise",
        "ground_truth": "The Silk Board signal is taking forever today, really sorry for the delay.",
        "expected_localities": ["Silk Board"]
    },
    "sample_11": {
        "filename": "11_bellandur_quiet.wav",
        "title": "Bellandur - Vacancy Query",
        "condition": "Quiet Room",
        "ground_truth": "Bellandur area mein koi vacancy hai kya office assistant ke liye?",
        "expected_localities": ["Bellandur"]
    },
    "sample_12": {
        "filename": "12_sarjapur_phone.wav",
        "title": "Sarjapur - Address Verification",
        "condition": "Phone-call Quality",
        "ground_truth": "Mera address Sarjapur Road ke paas hai, kya wahan delivery possible hai?",
        "expected_localities": ["Sarjapur"]
    },
    "sample_13": {
        "filename": "13_bommanahalli_quiet.wav",
        "title": "Bommanahalli - Experience Info",
        "condition": "Quiet Room",
        "ground_truth": "I have two years of experience working near Bommanahalli in logistics.",
        "expected_localities": ["Bommanahalli"]
    },
    "sample_14": {
        "filename": "14_kr_puram_traffic.wav",
        "title": "KR Puram - Bridge Accident",
        "condition": "Traffic Noise",
        "ground_truth": "KR Puram bridge pe accident hua hai, pura rasta block hai.",
        "expected_localities": ["KR Puram"]
    },
    "sample_15": {
        "filename": "15_peenya_phone.wav",
        "title": "Peenya - Industrial Area Call",
        "condition": "Phone-call Quality",
        "ground_truth": "Calling from Peenya industrial area, regarding the supervisor role.",
        "expected_localities": ["Peenya"]
    },
    "sample_16": {
        "filename": "16_yeshwanthpur_rushed.wav",
        "title": "Yeshwanthpur - Junction Update",
        "condition": "Rushed Speech",
        "ground_truth": "Yeshwanthpur junction cross kar liya hai, bas 5 minute mein aata hoon.",
        "expected_localities": ["Yeshwanthpur"]
    },
    "sample_17": {
        "filename": "17_hebbal_quiet.wav",
        "title": "Hebbal - Travel Update",
        "condition": "Quiet Room",
        "ground_truth": "Hebbal flyover ke paas rehta hoon, wahan se travel karna easy hoga.",
        "expected_localities": ["Hebbal"]
    },
    "sample_18": {
        "filename": "18_yelahanka_phone.wav",
        "title": "Yelahanka - Location Query",
        "condition": "Phone-call Quality",
        "ground_truth": "Is the job location in Yelahanka or somewhere closer to the city?",
        "expected_localities": ["Yelahanka"]
    },
    "sample_19": {
        "filename": "19_banashankari_whispered.wav",
        "title": "Banashankari - Temple Visit",
        "condition": "Whispered Speech",
        "ground_truth": "Banashankari mandir ke pass hoon, yahan network thoda weak hai.",
        "expected_localities": ["Banashankari"]
    },
    "sample_20": {
        "filename": "20_rajajinagar_quiet.wav",
        "title": "Rajajinagar - Sales Role",
        "condition": "Quiet Room",
        "ground_truth": "I'm interested in the sales role for the Rajajinagar branch.",
        "expected_localities": ["Rajajinagar"]
    }
}
