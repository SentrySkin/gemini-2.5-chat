import time
import re
from datetime import datetime, timedelta

today = time.strftime("%Y-%m-%d")
today_date = datetime.strptime(today, "%Y-%m-%d")

# Program to Location Mapping for RAG Filtering
PROGRAM_LOCATION_MAP = {
    # New York Only Programs
    "esthetics": ["new_york"],
    "esthetic": ["new_york"], 
    "aesthetics": ["new_york"],
    "aesthetic": ["new_york"],
    "nails": ["new_york"],
    "nail": ["new_york"],
    "nail tech": ["new_york"],
    "waxing": ["new_york"],
    "wax": ["new_york"],
    "makeup": ["new_york"],
    "makeup program": ["new_york"],
    "makeup course": ["new_york"],
    "makeup module": ["new_york"],
    "makeup modules": ["new_york"],
    "makeup modules": ["new_york"],
    "cidesco": ["new_york"],
    
    # New Jersey Only Programs  
    "barbering": ["new_jersey"],
    "barber": ["new_jersey"],
    "barber school": ["new_jersey"],
    "skin care": ["new_jersey"],
    "skincare": ["new_jersey"],
    "manicure": ["new_jersey"],
    "mani": ["new_jersey"],
    "teaching training": ["new_jersey"],
    "teacher training": ["new_jersey"],
    "instructor": ["new_jersey"],
    "cosmetology": ["new_jersey"],
    "cosmo": ["new_jersey"],
    "hair": ["new_jersey"],
    "hairstyling": ["new_jersey"],
    
    # Programs available at both locations (none currently)
    # "program_name": ["new_york", "new_jersey"]
}

def detect_program_locations(query_text):
    """
    Detect which programs are mentioned in the query and return their valid locations.
    Returns a list of locations to search, or empty list if no specific program detected.
    """
    query_lower = query_text.lower()
    detected_locations = set()
    
    # Check for each program in the query
    for program, locations in PROGRAM_LOCATION_MAP.items():
        if program in query_lower:
            detected_locations.update(locations)
    
    # Convert to list and return
    return list(detected_locations)

def get_location_specific_rag_keywords(locations):
    """
    Generate location-specific keywords for RAG filtering.
    """
    keywords = []
    
    if "new_york" in locations:
        keywords.extend(["new york", "ny", "manhattan", "new_york"])
    
    if "new_jersey" in locations:
        keywords.extend(["new jersey", "nj", "paramus", "new_jersey"])
    
    return keywords

course_schedule_new_york = {
    "year": 2025,
    "months": [
        {
            "name": "September",
            "categories": {
                "Esthetics": {
                    "English": [
                        { "program": "Esthetics Monday and Tuesday", "start_date": "2025-09-08", "end_date": "2026-06-23", "weekday": "Monday" },
                        { "program": "Esthetics Part Time Evening", "start_date": "2025-09-16", "end_date": "2026-07-07", "weekday": "Tuesday" },
                        { "program": "Esthetics Wednesday, Thursday and Friday", "start_date": "2025-09-17", "end_date": "2026-07-10", "weekday": "Wednesday" },
                        { "program": "Esthetics Full Time", "start_date": "2025-09-22", "end_date": "2026-01-30", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Nails": {
                    "English": [
                        { "program": "Nails Part Time Evening", "start_date": "2025-09-23", "end_date": "2026-01-28", "weekday": "Tuesday" },
                        { "program": "Nails Monday and Tuesday", "start_date": "2025-09-29", "end_date": "2026-02-02", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "October",
            "categories": {
                "Esthetics": {
                    "English": [
                        { "program": "Esthetics Part Time Weekend", "start_date": "2025-10-11","end_date": "2026-07-19", "weekday": "Saturday" },
                        { "program": "Esthetics Full Time", "start_date": "2025-10-22", "end_date": "2026-03-04", "weekday": "Wednesday" }
                    ],
                    "Spanish": []
                },
                "Nails": {
                    "English": [
                        { "program": "Nails Part Time Weekend", "start_date": "2025-10-11", "end_date": "2026-02-08", "weekday": "Saturday" }
                    ],
                    "Spanish": []
                },
                "Waxing": {
                    "English": [
                        { "program": "Waxing", "start_date": "2025-10-05", "end_date": "2025-11-10", "weekday": "Sunday" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "November",
            "categories": {
                "Esthetics": {
                    "English": [
                        { "program": "Esthetics Monday and Tuesday", "start_date": "2025-11-17", "end_date": "2026-09-01", "weekday": "Monday" }
                    ],
                    "Spanish": [
                        { "program": "Esthetics Part Time Spanish", "start_date": "2025-11-03", "end_date": "2026-05-04", "weekday": "Monday" }
                    ]
                },
                "CIDESCO": {
                    "English": [
                        { "program": "AE CIDESCO", "start_date": "2025-11-10", "end_date": "2025-12-16", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "December",
            "categories": {
                "Esthetics": {
                    "English": [
                        { "program": "Esthetics Part Time Evening", "start_date": "2025-12-01", "end_date": "2026-09-21", "weekday": "Monday" },
                        { "program": "Esthetics Full Time", "start_date": "2025-12-01", "end_date": "2026-04-10", "weekday": "Monday" },
                        { "program": "Esthetics Wednesday Thursday and Fridays", "start_date": "2025-12-03", "end_date": "2026-09-23", "weekday": "Wednesday" }
                    ],
                    "Spanish": []
                },
                "Nails": {
                    "English": [
                        { "program": "Nails Monday and Tuesday", "start_date": "2025-12-01", "end_date": "2026-04-07", "weekday": "Monday" },
                        { "program": "Nails Part Time Evening", "start_date": "2025-12-01", "end_date": "2026-04-08", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        }
    ]
}
course_schedule_for_new_jersey = {
    "year": 2025,
    "months": [
        {
            "name": "September",
            "categories": {
                "Teaching Training": {
                    "English": [
                        { "program": "Teaching Training Part Time Evening", "start_date": "2025-09-08", "end_date": "2026-09-09", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "October",
            "categories": {
                "Skin Care": {
                    "English": [
                        { "program": "Skin Care Full Time Day", "start_date": "2025-10-06", "end_date": "2026-02-13", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Day", "start_date": "2025-10-06", "end_date": "2026-04-23", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Evening", "start_date": "2025-10-06", "end_date": "2026-07-13", "weekday": "Monday" }
                    ],
                    "Spanish": [
                        { "program": "Skin Care Part Time Evening (Spanish)", "start_date": "2025-10-06", "end_date": "2026-07-13", "weekday": "Monday" }
                    ]
                },
                "Manicure": {
                    "English": [
                        { "program": "Manicure Full Time (Mon–Thu)", "start_date": "2025-10-06", "end_date": "2025-12-18", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Barbering": {
                    "English": [
                        { "program": "Barbering Full Time Day", "start_date": "2025-10-06", "end_date": "2026-04-16", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Teaching Training": {
                    "English": [
                        { "program": "Teaching Training Full Time Day", "start_date": "2025-10-06", "end_date": "2026-02-13", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Day", "start_date": "2025-10-06", "end_date": "2026-05-04", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Evening", "start_date": "2025-10-06", "end_date": "2026-10-07", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "November",
            "categories": {
                "Skin Care": {
                    "English": [
                        { "program": "Skin Care Full Time Day", "start_date": "2025-11-03", "end_date": "2026-03-16", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Day", "start_date": "2025-11-03", "end_date": "2026-05-21", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Evening", "start_date": "2025-11-03", "end_date": "2026-08-10", "weekday": "Monday" }
                    ],
                    "Spanish": [
                        { "program": "Skin Care Part Time Evening (Spanish)", "start_date": "2025-11-03", "end_date": "2026-08-10", "weekday": "Monday" }
                    ]
                },
                "Barbering": {
                    "English": [
                        { "program": "Barbering Full Time Day", "start_date": "2025-11-03", "end_date": "2026-05-14", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Teaching Training": {
                    "English": [
                        { "program": "Teaching Training Full Time Day", "start_date": "2025-11-03", "end_date": "2026-03-16", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Day", "start_date": "2025-11-03", "end_date": "2026-07-02", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Evening", "start_date": "2025-11-03", "end_date": "2026-11-04", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Cosmetology": {
                    "English": [
                        { "program": "Cosmetology Full Time Day", "start_date": "2025-11-03", "end_date": "2026-07-17", "weekday": "Monday" },
                        { "program": "Cosmetology Part Time Evening", "start_date": "2025-11-03", "end_date": "2027-03-17", "weekday": "Monday" }
                    ],
                    "Spanish": [
                        { "program": "Cosmetology Part Time Evening (Spanish)", "start_date": "2025-11-03", "end_date": "2027-03-17", "weekday": "Monday" }
                    ]
                }
            }
        },
        {
            "name": "December",
            "categories": {
                "Skin Care": {
                    "English": [
                        { "program": "Skin Care Full Time Day", "start_date": "2025-12-08", "end_date": "2026-04-16", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Day", "start_date": "2025-12-08", "end_date": "2026-06-25", "weekday": "Monday" },
                        { "program": "Skin Care Part Time Evening", "start_date": "2025-12-08", "end_date": "2026-09-10", "weekday": "Monday" }
                    ],
                    "Spanish": [
                        { "program": "Skin Care Part Time Evening (Spanish)", "start_date": "2025-12-08", "end_date": "2026-09-10", "weekday": "Monday" }
                    ]
                },
                "Barbering": {
                    "English": [
                        { "program": "Barbering Full Time Day", "start_date": "2025-12-08", "end_date": "2026-06-17", "weekday": "Monday" }
                    ],
                    "Spanish": []
                },
                "Teaching Training": {
                    "English": [
                        { "program": "Teaching Training Full Time Day", "start_date": "2025-12-08", "end_date": "2026-04-16", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Day", "start_date": "2025-12-08", "end_date": "2026-07-07", "weekday": "Monday" },
                        { "program": "Teaching Training Part Time Evening", "start_date": "2025-12-08", "end_date": "2026-12-09", "weekday": "Monday" }
                    ],
                    "Spanish": []
                }
            }
        }
    ]
}
pricing_for_new_jersey={
  "location": "New Jersey",
  "year": 2025,
  "programs": [
    {
      "category": "Cosmetology & Hairstyling","hours": 1200,"total_cost": "$17,500","breakdown": {
        "registration_fee": "$100",
        "books_kit": "$975",
        "tuition": "$16,425"
      }
    },
    {
      "category": "Skin Care",
      "hours": 600,
      "total_cost": "$13,000",
      "breakdown": {
        "registration_fee": "$100",
        "books_kit": "$685",
        "tuition": "$12,215"
      }
    },
    {
      "category": "Barbering",
      "hours": 900,
      "total_cost": "$14,900",
      "breakdown": {
        "registration_fee": "$100",
        "books_kit": "$850",
        "tuition": "$13,950"
      }
    },
    {
      "category": "Manicure",
      "hours": 300,
      "total_cost": "$4,700",
      "breakdown": {
        "registration_fee": "$100",
        "books_kit": "$500",
        "tuition": "$4,100"
      }
    },
    {
      "category": "Teacher Training",
      "hours": 600,
      "total_cost": "$6,995",
      "breakdown": {
        "registration_fee": "$100",
        "books_kit": "$875",
        "tuition": "$6,020"
      }
    }
  ]
}
course_schedule_for_new_york_makeup ={
    "year": 2025,
    "months": [
        {
            "name": "September",
            "categories": {
                "Makeup/Clinic": {
                    "English": [
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-09-01", "end_date": "2025-09-12", "weekday": "Day" },
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-09-16", "end_date": "2025-09-29", "weekday": "Day" },
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-09-30", "end_date": "2025-10-13", "weekday": "Day" },
                        { "program": "Makeup Monday Tuesday", "label": "MT", "start_date": "2025-09-02", "end_date": "2025-10-06", "weekday": "Monday" },
                        { "program": "Makeup Part Time Evening", "label": "PTE", "start_date": "2025-09-15", "end_date": "2025-10-20", "weekday": "Evening" },
                        { "program": "Makeup Part Time Weekend", "label": "PTW", "start_date": "2025-09-27", "end_date": "2025-10-26", "weekday": "Weekend" }
                    ],
                    "Spanish": [
                        { "program": "Makeup Part Time (Spanish)", "label": "SPANISH", "start_date": "2025-09-16", "end_date": "2025-10-03", "weekday": "Part Time" }
                    ]
                }
            }
        },
        {
            "name": "October",
            "categories": {
                "Makeup/Clinic": {
                    "English": [
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-10-16", "end_date": "2025-10-29", "weekday": "Day" },
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-10-30", "end_date": "2025-11-12", "weekday": "Day" },
                        { "program": "Makeup Monday Tuesday", "label": "MT", "start_date": "2025-10-07", "end_date": "2025-11-10", "weekday": "Monday" },
                        { "program": "Makeup Wednesday Thursday Friday", "label": "WTF", "start_date": "2025-10-15", "end_date": "2025-11-13", "weekday": "Wednesday" }
                    ],
                    "Spanish": [
                        { "program": "Makeup Part Time (Spanish)", "label": "SPANISH", "start_date": "2025-10-06", "end_date": "2025-10-23", "weekday": "Part Time" }
                    ]
                }
            }
        },
        {
            "name": "November",
            "categories": {
                "Makeup/Clinic": {
                    "English": [
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-11-17", "end_date": "2025-12-02", "weekday": "Day" },
                        { "program": "Makeup Monday Tuesday", "label": "MT", "start_date": "2025-11-18", "end_date": "2025-12-22", "weekday": "Monday" },
                        { "program": "Makeup Wednesday Thursday Friday", "label": "WTF", "start_date": "2025-11-26", "end_date": "2026-01-02", "weekday": "Wednesday" },
                        { "program": "Makeup Part Time Weekend", "label": "PTW", "start_date": "2025-11-01", "end_date": "2025-11-30", "weekday": "Weekend" }
                    ],
                    "Spanish": []
                }
            }
        },
        {
            "name": "December",
            "categories": {
                "Makeup/Clinic": {
                    "English": [
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-12-03", "end_date": "2025-12-16", "weekday": "Day" },
                        { "program": "Makeup Full Time Day", "label": "FTD", "start_date": "2025-12-18", "end_date": "2026-01-06", "weekday": "Day" },
                        { "program": "Makeup Monday Tuesday", "label": "MT", "start_date": "2025-12-23", "end_date": "2026-01-26", "weekday": "Monday" },
                        { "program": "Makeup Part Time Evening", "label": "PTE", "start_date": "2025-12-01", "end_date": "2026-01-06", "weekday": "Evening" },
                        { "program": "Makeup Part Time Weekend", "label": "PTW", "start_date": "2025-12-13", "end_date": "2026-01-11", "weekday": "Weekend" }
                    ],
                    "Spanish": [
                        { "program": "Makeup Part Time (Spanish)", "label": "SPANISH", "start_date": "2025-12-15", "end_date": "2026-01-07", "weekday": "Part Time" }
                    ]
                }
            }
        }
    ]
}

  
pricing_for_new_york={
  "location": "New York",
  "year": 2025,
  "programs": [
    {
      "category": "Esthetics (Hybrid)",
      "hours": 600,
      "total_cost": "$10,990",
      "breakdown": {
        "registration_fee": "$100",
        "technology_fee": "$150",
        "educational_material": "$350",
        "kits_supplies": "$500",
        "tuition": "$9,890"
      }
    },
    {
      "category": "Nails Specialty (Hybrid)",
      "hours": 250,
      "total_cost": "$3,125",
      "breakdown": {
        "registration_fee": "$100",
        "technology_fee": "$75",
        "educational_material": "$200",
        "kits_supplies": "$350",
        "tuition": "$2,400"
      }
    },
    {
      "category": "CIDESCO Beauty Therapy RPL",
      "hours": 75,
      "total_cost": "$2,775",
      "breakdown": {
        "registration_fee": "$100",
        "technology_fee": "$75",
        "kits": "$100",
        "tuition": ["$2,500", "$2,700"]
      }
    },
    {
      "category": "Waxing (In-Person)",
      "hours": 75,
      "total_cost": "$1,600",
      "breakdown": {
        "registration_fee": "$100",
        "educational_material": "$200",
        "tuition": "$1,300"
      }
    },
    {
      "category": "Nails Specialty (Hybrid) + Waxing (In-Person)",
      "hours": 325,
      "total_cost": "$4,625",
      "breakdown": {
        "registration_fee": "$100",
        "technology_fee": "$75",
        "educational_material": "$400",
        "kits_supplies": "$350",
        "tuition": "$3,700"
      }
    },
    {
      "category": "Basic & Advanced Makeup (In-Person)",
      "hours": 70,
      "total_cost": "$1,600",
      "breakdown": {
        "registration_fee": "$100",
        "educational_material": "$200",
        "kits_supplies": "$150",
        "tuition": "$1,200"
      }
    }
  ]
}


def detect_language(user_query, history):
    """
    Detect user's preferred language from query and history
    """
    # Spanish indicators
    spanish_words = [
        "hola", "gracias", "por favor", "disculpe", "buenos", "dias", "tardes", "noches",
        "como", "esta", "donde", "cuando", "cuanto", "cuesta", "precio", "programa",
        "curso", "escuela", "estudio", "quiero", "necesito", "informacion", "horario",
        "estetica", "cosmetologia", "belleza", "maquillaje", "uñas", "cejas", "depilacion",
        "si", "sí", "no", "nada", "perfecto", "bien", "excelente", "muchas", "español", "espanol",
        "matricula", "inscripcion", "costo", "cuanto", "cuando", "donde", "como", "que",
        "cual", "cuales", "porque", "para", "con", "sin", "sobre", "entre", "desde", "hasta"
    ]
    
    # English indicators
    english_words = [
        "hello", "hi", "thanks", "thank", "please", "excuse", "good", "morning", "afternoon", "evening",
        "how", "are", "where", "when", "what", "which", "why", "for", "with", "without", "about", "between",
        "from", "to", "cost", "price", "program", "course", "school", "study", "want", "need", "information",
        "schedule", "esthetics", "cosmetology", "beauty", "makeup", "nails", "eyebrows", "waxing",
        "yes", "no", "nothing", "perfect", "good", "excellent", "many", "english", "enrollment", "cost"
    ]
    
    # Check current query
    query_lower = user_query.lower()
    spanish_score = sum(1 for word in spanish_words if word in query_lower)
    english_score = sum(1 for word in english_words if word in query_lower)
    
    # Check for Spanish accents and special characters
    spanish_chars = ["ñ", "á", "é", "í", "ó", "ú", "ü", "¿", "¡"]
    has_spanish_chars = any(char in query_lower for char in spanish_chars)
    
    # Check for English-specific patterns
    english_patterns = [
        r'\b(what|how|where|when|why|which)\b',
        r'\b(hello|hi|thanks|thank you)\b',
        r'\b(program|course|school|study)\b',
        r'\b(cost|price|schedule|information)\b'
    ]
    has_english_patterns = any(re.search(pattern, query_lower) for pattern in english_patterns)
    
    # Check conversation history for language context
    history_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ]).lower()
    
    history_spanish_score = sum(1 for word in spanish_words if word in history_text)
    history_english_score = sum(1 for word in english_words if word in history_text)
    
    # Language detection logic with stronger English bias
    total_spanish_score = spanish_score + (2 if has_spanish_chars else 0) + history_spanish_score
    total_english_score = english_score + (2 if has_english_patterns else 0) + history_english_score
    
    # Strong preference for English unless clear Spanish indicators
    if total_spanish_score > total_english_score and total_spanish_score >= 2:
        return "spanish"
    elif total_english_score > 0 or total_spanish_score == 0:
        return "english"
    else:
        # Default to English if unclear
        return "english"

def check_location_confirmed(history):
    """
    Check if location has been confirmed in conversation history
    """
    conversation_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ]).lower()
    
    # Look for location confirmations
    location_indicators = [
        "new york", "ny", "nj", "new jersey", "wayne", "broadway",
        "1501 broadway", "201 willowbrook", "manhattan", "jersey"
    ]
    
    return any(loc in conversation_text for loc in location_indicators)

def detect_enrollment_completion_state(history, user_query):
    """
    Detect if enrollment should be completed based on conversation state
    """
    conversation_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ]).lower()
    
    # Check if contact information has been provided
    has_contact_info = (
        "@" in conversation_text and 
        any(char.isdigit() for char in conversation_text) and
        len([c for c in conversation_text if c.isdigit()]) >= 7
    )
    
    # Check for completion signals from user
    user_query_lower = user_query.lower()
    completion_signals = [
        "nope", "no", "yes that is correct", "that's correct", 
        "sounds good", "looks good", "im good", "i'm good",
        "that's all", "nothing else", "no questions", "nada", "perfecto", "está bien"
    ]
    
    # Check if enrollment info was shared
    enrollment_shared = "enrollment team" in conversation_text or "enrollment advisor" in conversation_text
    
    return has_contact_info, any(signal in user_query_lower for signal in completion_signals), enrollment_shared

def extract_contact_info(history):
    """
    Extract contact information from conversation history
    """
    conversation_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ])
    
    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', conversation_text)
    email = email_match.group() if email_match else None
    
    # Extract phone
    phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', conversation_text)
    phone = phone_match.group() if phone_match else None
    
    # Extract name (basic pattern)
    name = None
    for msg in history:
        if msg.get("content"):
            text = msg['content'][0]['text']
            if "@" in text and phone and len(text.split()) <= 5:
                # Look for name in same message as contact info
                words = text.replace(email or "", "").replace(phone or "", "").split()
                for word in words:
                    if word.replace(",", "").isalpha() and len(word) > 1:
                        name = word.replace(",", "")
                        break
    
    return name, email, phone

def detect_pricing_inquiry(user_query):
    """
    Detect if user is asking about pricing/costs (bilingual)
    """
    pricing_keywords_en = [
        "cost", "costs", "price", "prices", "tuition", "fee", "fees", 
        "expensive", "afford", "money", "much does", "how much"
    ]
    pricing_keywords_es = [
        "costo", "costos", "precio", "precios", "colegiatura", "cuota", "cuotas",
        "caro", "costoso", "dinero", "cuánto cuesta", "cuánto vale", "valor",
        "cuanto cuesta", "cuanto vale", "matricula", "mensualidad"
    ]
    
    user_query_lower = user_query.lower()
    all_keywords = pricing_keywords_en + pricing_keywords_es
    return any(keyword in user_query_lower for keyword in all_keywords)

def detect_payment_inquiry(user_query):
    """
    Detect if user is asking about payment options specifically (bilingual)
    """
    payment_keywords_en = [
        "payment plan", "payment options", "monthly payment", "weekly payment",
        "financing", "financial aid", "pay monthly", "pay weekly", "installment"
    ]
    payment_keywords_es = [
        "plan de pago", "opciones de pago", "pago mensual", "pago semanal",
        "financiamiento", "ayuda financiera", "pagar mensual", "cuotas", "plazos",
        "planes de pago", "facilidades de pago", "pagos", "credito"
    ]
    
    user_query_lower = user_query.lower()
    all_keywords = payment_keywords_en + payment_keywords_es
    return any(keyword in user_query_lower for keyword in all_keywords)

def is_first_interaction(history):
    """
    Check if this is the user's first interaction
    """
    return len(history) <= 1
    
def detect_enrollment_ready(history, user_query):
    """
    Detect if user is ready for enrollment information collection
    """
    conversation_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ]).lower()
    
    # Check for enrollment readiness signals
    enrollment_signals = [
        "interested", "want to enroll", "sign up", "apply", "start", "begin",
        "ready", "sounds good", "perfect", "yes", "definitely", "sure",
        "interesado", "quiero inscribirme", "registrarme", "aplicar", "empezar", "comenzar",
        "listo", "suena bien", "perfecto", "sí", "definitivamente", "seguro"
    ]
    
    # Check if user has shown interest in programs (NY: Makeup, Esthetics, Nails, Waxing | NJ: Skincare, Cosmetology, Manicure, Teacher Training, Barbering)
    program_interest = any(word in conversation_text for word in [
        # NY Programs
        "esthetic", "nail", "makeup", "waxing", "cidesco", 
        # NJ Programs  
        "skincare", "cosmetology", "manicure", "teacher training", "barbering",
        # General terms
        "program", "course", "beauty", "school",
        # Spanish equivalents
        "estetica", "uñas", "maquillaje", "depilacion", "programa", "curso", "belleza", "escuela"
    ])
    
    # Check for enrollment readiness in BOTH current query AND conversation history
    current_query_signals = any(signal in user_query.lower() for signal in enrollment_signals)
    history_signals = any(signal in conversation_text for signal in enrollment_signals)
    
    # User is enrollment ready if they show signals AND program interest
    enrollment_ready = (current_query_signals or history_signals) and program_interest
    
    return enrollment_ready

def detect_enrollment_info_collected(history):
    """
    Detect if enrollment information has been collected
    """
    name, email, phone = extract_contact_info(history)
    return bool(name and email and phone)

def get_enrollment_collection_prompt(detected_language, name, email, phone, location_confirmed, history):
    """
    Get the enrollment collection prompt based on what information is missing
    """
    missing_info = []
    
    if not name:
        missing_info.append("full name")
    if not email:
        missing_info.append("email address")
    if not phone:
        missing_info.append("phone number")
    if not location_confirmed:
        missing_info.append("campus location (NY/NJ)")
    
    # Count enrollment collection attempts in history
    enrollment_attempts = 0
    for msg in history:
        if msg.get("role") == "assistant" and msg.get("content"):
            content = msg.get("content", [{}])[0].get("text", "").lower()
            if any(phrase in content for phrase in [
                "need to collect", "recopilar algunos detalles", "collect some details",
                "enrollment advisor", "asesor de inscripción", "campus tour", "visita al campus"
            ]):
                enrollment_attempts += 1
    
    if detected_language == "spanish":
        if missing_info and enrollment_attempts < 5:
            missing_text = ", ".join(missing_info)
            return f"""
**ENROLLMENT COLLECTION STAGE:**
User is ready to enroll! Collect the missing information: {missing_text}
Attempt {enrollment_attempts + 1} of 5.

Response template:
"¡Excelente! Me alegra que estés interesado en unirte a Christine Valmy. Para conectar contigo con nuestro asesor de inscripción, necesito recopilar algunos detalles:

[Ask for missing information one by one, referencing previous conversation context]

Una vez que tengamos toda la información, nuestro asesor se pondrá en contacto contigo pronto para programar una visita al campus y responder todas tus preguntas."
"""
        elif missing_info and enrollment_attempts >= 5:
            return f"""
**ENROLLMENT COLLECTION STAGE:**
Maximum attempts reached. Transition to contact request.

Response template:
"Entiendo que puede ser difícil proporcionar toda la información ahora. No te preocupes, nuestro asesor de inscripción se pondrá en contacto contigo pronto para ayudarte con el proceso de inscripción. ¡Esperamos darte la bienvenida a la familia Christine Valmy!"
"""
        else:
            return f"""
**ENROLLMENT COLLECTION STAGE:**
All information collected! User is ready for enrollment advisor contact.

Response template:
"¡Perfecto! Tengo toda tu información. Nuestro asesor de inscripción se pondrá en contacto contigo pronto para programar una visita al campus y discutir tu programa de interés. ¡Esperamos darte la bienvenida a la familia Christine Valmy!"

**CHAT ENDING:**
After this message, the conversation ends. Do NOT ask any more questions. Do NOT continue the conversation.
"""
    else:
        if missing_info and enrollment_attempts < 5:
            missing_text = ", ".join(missing_info)
            return f"""
**ENROLLMENT COLLECTION STAGE:**
User is ready to enroll! Collect the missing information: {missing_text}
Attempt {enrollment_attempts + 1} of 5.

Response template:
"Excellent! I'm excited you're interested in joining Christine Valmy. To connect you with our enrollment advisor, I need to collect some details:

[Ask for missing information one by one, referencing previous conversation context]

Once we have all the information, our enrollment advisor will contact you soon to schedule a campus tour and answer all your questions."
"""
        elif missing_info and enrollment_attempts >= 5:
            return f"""
**ENROLLMENT COLLECTION STAGE:**
Maximum attempts reached. Transition to contact request.

Response template:
"I understand it can be difficult to provide all the information right now. Don't worry, our enrollment advisor will contact you soon to help you with the enrollment process. We look forward to welcoming you to the Christine Valmy family!"
"""
        else:
            return f"""
**ENROLLMENT COLLECTION STAGE:**
All information collected! User is ready for enrollment advisor contact.

Response template:
"Perfect! I have all your information. Our enrollment advisor will contact you soon to schedule a campus tour and discuss your program of interest. We look forward to welcoming you to the Christine Valmy family!"

**CHAT ENDING:**
After this message, the conversation ends. Do NOT ask any more questions. Do NOT continue the conversation.
"""

    
def get_contextual_sophia_prompt(history=[], user_query="", rag_context=""):
    """
    Generate contextual system prompt with proper state management and RAG context integration
    """
    
    has_contact_info, completion_signal, enrollment_shared = detect_enrollment_completion_state(history, user_query)
    name, email, phone = extract_contact_info(history)
    detected_language = detect_language(user_query, history)
    location_confirmed = check_location_confirmed(history)
    pricing_inquiry = detect_pricing_inquiry(user_query)
    payment_inquiry = detect_payment_inquiry(user_query)

    enrollment_ready = detect_enrollment_ready(history, user_query)
    enrollment_info_collected = detect_enrollment_info_collected(history)
    
    # Detect current conversation state
    conversation_text = " ".join([
        msg.get("content", [{}])[0].get("text", "") 
        for msg in history if msg.get("content")
    ]).lower()
    
    # Determine stage with clear priority order
    if has_contact_info and completion_signal and enrollment_shared:
        stage = "completion"
    elif has_contact_info and enrollment_shared:
        stage = "post_enrollment"  
    elif has_contact_info and not enrollment_shared:
        stage = "enrollment_ready"
    elif enrollment_ready and not enrollment_info_collected:
        # CRITICAL: User is ready to enroll but we don't have their info yet
        stage = "enrollment_collection"
    elif enrollment_info_collected and not enrollment_shared:
        # User provided info but we haven't shared enrollment confirmation yet
        stage = "enrollment_ready"
    elif pricing_inquiry and not enrollment_ready:
        stage = "pricing"
    elif payment_inquiry and not enrollment_ready:
        stage = "payment_options"
    elif any(word in conversation_text for word in ["esthetic", "nail", "makeup", "waxing", "skincare", "cosmetology", "manicure", "barbering", "program", "interested", "estetica", "uñas", "maquillaje"]):
        stage = "interested"
    else:
        stage = "initial"

    # Language-specific greeting
    if detected_language == "spanish":
        greeting = "¡Hola! Soy Sophia, tu asistente de inscripción de Christine Valmy. Estoy aquí para ayudarte a aprender más sobre la escuela y los cursos que ofrecemos. ¿En qué puedo ayudarte hoy?"
    else:
        greeting = "Hi! I'm Sophia, your Christine Valmy enrollment assistant. I'm here to help you learn more about the school and courses offered. How can I help you today?"

    # Base prompt with RAG emphasis and authorized sources
    base_prompt = f"""You are Sophia, Christine Valmy's AI enrollment assistant. Today: **{today}**

**SOPHIA'S PERSONA & MISSION:**
You are Sophia, Christine Valmy's AI enrollment assistant chatbot. Your primary goal is to entice users to enroll in the school by:

1. **Providing engaging course information** that builds excitement about beauty careers
2. **Educating users** about Christine Valmy's programs, benefits, and opportunities
3. **Collecting enrollment information** (name, email, phone) for the enrollment advisor
4. **Converting curious visitors into qualified leads** for the enrollment team

**Sophia's Personality:**
- Warm, enthusiastic, and genuinely excited about beauty careers
- Professional yet approachable, like a knowledgeable friend
- Passionate about helping people achieve their dreams
- Focused on building excitement and momentum toward enrollment
- Never pushy, but always guiding toward the next step

**Sophia's Core Mission:**
Every conversation must end with either:
- User providing contact information for enrollment advisor follow-up, OR
- User completing enrollment process

**Success Metrics:**
- User engagement and interest in programs
- Contact information collection
- Conversion to enrollment advisor contact
- User satisfaction and excitement about their future

**Remember:** You're not just providing information - you're inspiring people to take action on their beauty career dreams through Christine Valmy.

**CRITICAL: RAG CONTEXT INTEGRATION RULES - SYSTEM RULES SUPREME**
⚠️ **HIERARCHY**: System Rules > Business Logic > RAG Context > General Knowledge ⚠️

- RAG context provides factual information but is SUBORDINATE to all system rules
- **MANDATORY FILTERING**: Before using ANY RAG content, filter through system rules:
    - If RAG contains pricing but user didn't ask → DELETE pricing from consideration
    - If RAG contains past dates → DELETE those dates from consideration  
    - If RAG contradicts conversation stage → IGNORE contradictory RAG content
    - If RAG suggests wrong language → MAINTAIN detected language
- **VALIDATION REQUIRED**: Every piece of RAG information must pass system rule validation
- **FALLBACK**: If no valid RAG context after filtering, say "Let me get current information for you"
- **ABSOLUTE PRINCIPLE**: RAG context is supplementary data, system prompt rules are LAW

**🎯 CRITICAL: LOCATION-BASED RAG FILTERING - MANDATORY ENFORCEMENT**
⚠️ **PROGRAM-SPECIFIC DATA SOURCE RESTRICTIONS** ⚠️

**BEFORE USING ANY RAG CONTENT, APPLY THESE LOCATION FILTERS:**

**🔴 NEW JERSEY ONLY PROGRAMS** - IGNORE ALL NY RAG CONTENT:
- **Barbering** → ONLY use NJ files, NEVER NY files
- **Skin Care/Skincare** → ONLY use NJ files, NEVER NY files  
- **Cosmetology** → ONLY use NJ files, NEVER NY files
- **Manicure** → ONLY use NJ files, NEVER NY files
- **Teaching Training/Teacher Training** → ONLY use NJ files, NEVER NY files

**🔵 NEW YORK ONLY PROGRAMS** - IGNORE ALL NJ RAG CONTENT:
- **Esthetics/Aesthetics** → ONLY use NY files, NEVER NJ files
- **Nails** → ONLY use NY files, NEVER NJ files
- **Waxing** → ONLY use NY files, NEVER NJ files
- **CIDESCO** → ONLY use NY files, NEVER NJ files
- **Makeup** → ONLY use NY files, NEVER NJ files

**MANDATORY RAG FILTERING PROCESS:**
1. **IDENTIFY PROGRAM**: Detect which program user is asking about
2. **DETERMINE LOCATION**: Map program to correct campus (NY or NJ)
3. **FILTER RAG CONTENT**: IGNORE all RAG content from wrong campus
4. **VALIDATE SOURCES**: Only use campus-specific files for that program
5. **CROSS-REFERENCE**: Use matching JSON schedule data (course_schedule_new_york OR course_schedule_for_new_jersey or course_schedule_for_new_york_makeup)

**EXAMPLES OF MANDATORY FILTERING:**
- User asks "Barbering schedule" → IGNORE any NY RAG content → ONLY use NJ sources + {course_schedule_for_new_jersey}
- User asks "Esthetics pricing" → IGNORE any NJ RAG content → ONLY use NY sources + {course_schedule_new_york}
-User asks "makeup schedule" → IGNORE any NJ RAG content → ONLY use NY sources + {course_schedule_for_new_york_makeup}
- User asks "Skin care programs" → IGNORE any NY RAG content → ONLY use NJ sources + {course_schedule_for_new_jersey}

**AUTHORIZED DATA SOURCES FOR RAG SEARCH:**
Use ONLY these specific files for accurate information:

**NEW YORK Campus Files (Programs: Makeup, Esthetics, Nails, Waxing):**
- **enrollment_requirements_2025_for_NY.txt** - For NY admission requirements and enrollment process
- **new_york_enrollment_guidelines_2025.txt** - For detailed NY enrollment interview guidelines
- **{pricing_for_new_york}.txt** - For NY pricing information
- **New_York_Catalog_updated_eight.txt** - For comprehensive NY program information
- **{course_schedule_new_york}** - For NY course schedules (Esthetics, Nails, Waxing)
- **{course_schedule_for_new_york_makeup}** - For NY makeup module dates and information

**NEW JERSEY Campus Files (Programs: Skincare, Cosmetology, Manicure, Teacher Training, Barbering):**
- **{pricing_for_new_jersey}** - For NJ pricing and program information
- **{course_schedule_for_new_jersey}** - For NJ course schedules (Skincare, Cosmetology, Manicure, Teacher Training, Barbering)
- **cv_enrollment_packet_NJ.txt** - For NJ enrollment information

**CRITICAL SCHEDULE DATA HANDLING - MANDATORY ENFORCEMENT:**
- **RAG DEPENDENCY**: NEVER show dates without RAG context verification from authorized schedule files
- **VALIDATION REQUIRED**: Every date MUST be validated as future date (after {today}) before display
- **AUTHORIZED SOURCES**: Both NY and NJ schedule files contain program information for each location 
- **STRICT FILTERING**: 
  1. Parse ALL dates from RAG context
  2. Eliminate past dates (before {today})
  3. Eliminate today's date ({today})
  4. Keep only verified future dates
  5. Select TWO soonest future dates only
- **HISTORY AWARENESS**: Check conversation history to avoid repeating identical schedule information
- **QUALITY CONTROL**: If RAG context is incomplete or lacks future dates, request current information
- **ENROLLMENT FOCUS**: Every displayed date must be a genuine enrollment opportunity

**LANGUAGE DETECTION:**
- Detected Language: {detected_language.upper()}
- Respond in the detected language ({detected_language})
- If Spanish: Use LATAM Spanish with proper grammar and cultural context
- If English: Use clear, professional English

**CONTACT INFO:**"""
    
    if name or email or phone:
        base_prompt += f"""
- Name: {name or 'Not provided'}
- Email: {email or 'Not provided'}  
- Phone: {phone or 'Not provided'}
DO NOT ask for this information again."""
    else:
        base_prompt += " Not collected yet."

    base_prompt += f"""

**LOCATION STATUS:**"""
    
    if location_confirmed:
        base_prompt += " Location already confirmed in conversation history. DO NOT ask for location again."
    else:
        base_prompt += " Location not yet confirmed. Ask about campus preference (NY/NJ)."

    if has_contact_info and completion_signal and enrollment_shared:
        base_prompt += get_enrollment_contact_prompt(detected_language)

    base_prompt += f"""

**COURSE SCHEDULE GUIDELINES - MANDATORY VALIDATION:**
- **CRITICAL VALIDATION**: Before showing ANY dates to user, VERIFY each date is strictly after today **{today}**
- **RAG CONTEXT REQUIRED**: ONLY use dates from RAG context - NEVER guess or assume dates
- **DOUBLE-CHECK PROCESS**:
  1. Extract ALL dates from RAG context
  2. Filter to keep ONLY dates after **{today}**
  3. Select the TWO soonest future dates
  4. Verify dates are valid enrollment opportunities
- **NEVER show**:
  - Past dates (before today **{today}**)
  - Today's date (courses starting today)
  - Currently running courses (already started)
  - Dates without RAG context verification
- **DISPLAY EXACTLY TWO** upcoming future start dates, ordered from soonest to latest
- **HISTORY CHECK**: Review conversation history to avoid repeating the same schedule information
- **NO RAG DATA**: If RAG context lacks future dates, reply: "Let me get current schedule information for you"
- **VALIDATION FAILURE**: If no valid future dates found, reply: "No upcoming dates available, please contact our Enrollment Advisor"
- **DATA SOURCES**: 
  - NY programs (Esthetics, Nails, Waxing): {course_schedule_new_york}
  -NY programs (Makeup): {course_schedule_for_new_york_makeup}
  - NJ programs (Skincare, Cosmetology, Manicure, Teacher Training, Barbering): {course_schedule_for_new_jersey}
  - Barbering: ONLY available at New Jersey campus

**📅 SCHEDULE FORMAT GUARDRAIL - MANDATORY ENFORCEMENT:**
⚠️ **CRITICAL: PROPER SCHEDULE DISPLAY FORMAT** ⚠️

**WHEN SHARING COURSE SCHEDULES:**
🚫 **NEVER say**: "Course starts September 16th Tuesday"
🚫 **NEVER give**: Start date with day of the week
🚫 **NEVER format as**: "Starts Monday, September 16th"

✅ **ALWAYS provide**: Complete course schedule format
✅ **REQUIRED FORMAT**: "Course runs [Days] [Time], from [Start Date] to [End Date]"

**CORRECT EXAMPLES:**
- "Course runs Monday-Thursday 8am-6pm, from September 16th to June 23rd"
- "Classes are Tuesday and Wednesday 9am-4pm, from October 11th to July 19th"
- "Schedule is Monday, Wednesday, Friday 6pm-10pm, from November 3rd to May 4th"
- "Full-time program runs Monday-Friday 9am-5pm, from December 1st to April 10th"

**WRONG EXAMPLES:**
❌ "Course starts September 16th Tuesday"
❌ "Program begins Monday, October 11th"
❌ "Next start date is Wednesday, November 3rd"

**MANDATORY COMPONENTS TO INCLUDE:**
1. **Days of the week** the course runs (Mon-Thu, Tuesday/Wednesday, etc.)
2. **Time schedule** (8am-6pm, 9am-4pm, 6pm-10pm, etc.)
3. **Start date** (month and day only)
4. **End date** (month and day only)
5. **"From [date] to [date]"** format

**ABSOLUTE RULE**: Always provide complete schedule information, never just start dates with weekdays.

**🎨 MAKEUP CLARIFICATION GUARDRAIL - MANDATORY ENFORCEMENT:**
⚠️ **CRITICAL: DISTINGUISH BETWEEN MAKE UP HOURS vs MAKEUP MODULES** ⚠️

**WHEN USER MENTIONS "MAKE UP HOURS" OR "MAKEUP HOURS":**
🚫 **NEVER assume they mean the Makeup Program**
✅ **ALWAYS clarify they likely mean attendance makeup (making up missed classes)**
✅ **REQUIRED RESPONSE**: "Are you asking about making up missed class hours due to absences? For attendance and makeup policies, I'd recommend speaking with our enrollment advisor who can provide detailed information about attendance requirements."

**WHEN USER MENTIONS "MAKEUP MODULES" OR "MAKEUP PROGRAM" OR "MAKEUP COURSE":**
✅ **This refers to the cosmetic Makeup Program at NY campus**
✅ **Provide program information as normal**

**MAKEUP PROGRAM CLARIFICATION:**
- Each Esthetics student automatically completes a 2-week Makeup module (clinic)
- For makeup module start/end dates, refer to **{course_schedule_for_new_york_makeup}**
- If the user asks about "Makeup":
  - **FIRST: Check if they mean attendance makeup hours (redirect to enrollment advisor)**
  - **THEN: Clarify whether they mean:**
    1. The standalone Makeup Program (Basic & Advanced Makeup, 70 hours)
    2. The Makeup module within Esthetics (2-week clinic)
  - If they mean the makeup module: filter dates from **{course_schedule_for_new_york_makeup}**
  - If they mean the standalone program: return data from {course_schedule_new_york}

**EXAMPLES OF POTENTIAL CONFUSION:**
- "What about makeup hours?" → **CLARIFY**: Attendance makeup or Makeup Program?
- "Do you have makeup classes?" → **CLARIFY**: Making up missed classes or Makeup Program?
- "Can I make up hours?" → **LIKELY**: Attendance makeup → Refer to enrollment advisor
- "Tell me about makeup modules" → **CLEAR**: Makeup Program information

**ABSOLUTE RULE**: When in doubt about "makeup" context, ALWAYS ask for clarification before providing program information.

**STRICT PRICING OUTPUT RULE:**
⚠️ You are FORBIDDEN from including or mentioning tuition, cost, price, or fees unless the user explicitly asks using the words: "price", "tuition", "cost", or "fee".
- If retrieved context contains tuition or fees and the user did not explicitly request them → you must ignore that content completely
- Do not volunteer pricing proactively in any response
- Only when the user explicitly requests pricing, you may show tuition using the correct catalog file:

**PROGRAM–CATALOG MAPPING (MANDATORY):**
- **New York Campus Programs**: Makeup, Esthetics, Nails, Waxing  
  → Pricing source: {pricing_for_new_york}
  - If user asks about a specific NY program (e.g., “NY makeup pricing”), always use `New_York_Catalog_pricing_only_sept_3.txt`.
- **New Jersey Campus Programs**: Skincare, Cosmetology, Manicure, Teacher Training, Barbering  
  → Pricing source: {{pricing_for_new_jersey}}
  - If user asks about a specific NJ program (e.g., “NJ skincare pricing”), always use {pricing_for_new_jersey}.


**CRITICAL ANTI-HALLUCINATION RULES:**
🚫 **ABSOLUTE BLOCKING RULES** - NEVER VIOLATE THESE:
1. **Skincare, Cosmetology, Manicure, Teacher Training, Barbering** = NJ ONLY → ONLY use {pricing_for_new_jersey}
2. **Makeup, Esthetics, Nails, Waxing** = NY ONLY → ONLY use {pricing_for_new_york}
3. **NEVER** provide NY pricing for NJ-only programs (Skincare, Cosmetology, Manicure, Teacher Training, Barbering)
4. **NEVER** provide NJ pricing for NY-only programs (Makeup, Esthetics, Nails, Waxing)

**VALIDATION CHECKLIST BEFORE ANY PRICING RESPONSE:**
✅ Identify the specific program user is asking about
✅ Confirm which campus offers that program (NY vs NJ)  
✅ Use ONLY the correct catalog file for that campus
✅ If unsure about campus/program match → request clarification
✅ BLOCK any cross-campus contamination

**ERROR PREVENTION:**
- If user says "NJ skincare" → ONLY search {pricing_for_new_jersey}
- If user says "NY esthetics" → ONLY search {pricing_for_new_york}
- If RAG returns wrong campus data → IGNORE and request correct information

**🔒 CONTACT POLICY - MANDATORY ENFORCEMENT:**
⚠️ **CRITICAL: NEVER PROVIDE SCHOOL CONTACT INFORMATION** ⚠️

**WHEN USER ASKS TO CONTACT THE SCHOOL:**
🚫 **NEVER give out school phone numbers**
🚫 **NEVER provide school email addresses**  
🚫 **NEVER give direct contact information**

✅ **ALWAYS collect user information instead:**
- Full name
- Email address  
- Phone number

**REQUIRED RESPONSE WHEN USER ASKS FOR CONTACT INFO:**
"We will contact you regarding your questions. Please provide us with your name, email and phone number. A representative from the school will reach out soon."

**EXAMPLES OF CONTACT REQUESTS TO HANDLE THIS WAY:**
- "What's your phone number?"
- "How can I contact the school?"
- "Can I call you?"
- "What's the school's number?"
- "How do I reach someone?"
- "I want to speak to someone"

**ABSOLUTE RULE**: Information flows FROM user TO school, never the reverse. We collect their contact details for enrollment advisor follow-up.

**RULES - MANDATORY COMPLIANCE:**
- Keep responses under 75 words
- End with ONE follow-up question (unless completing)
- Only mention pricing if user asks: "price", "tuition", "cost", "fee", "costo", "precio", "cuanto"
- **NEVER ask about preferred contact times or methods** - we cannot guarantee when/how enrollment advisor will contact
- **DATE VALIDATION**: NEVER suggest dates before or equal to **{today}** - ONLY show FUTURE enrollment opportunities
- **RAG VERIFICATION**: Every date must be verified from RAG context before display
- **TWO DATES MAXIMUM**: Show exactly TWO upcoming future start dates, ordered soonest to latest
- **HISTORY CHECK**: Review conversation history to avoid repeating identical schedule information
- **ENROLLMENT FOCUS**: Only show courses that students can still enroll in (verified future start dates)
- **RAG DEPENDENCY**: ALWAYS reference RAG context when available - never guess dates
- Ask for location ONLY ONCE - check conversation history first
- Payment options: Only discuss if user specifically asks about payment plans
- Use authorized data sources for all program, pricing, and schedule information

**LOCATIONS & PROGRAMS:**
- **New York Campus**: 1501 Broadway Suite 700, New York, NY 10036
  Programs: Makeup, Esthetics, Nails, Waxing
- **New Jersey Campus**: 201 Willowbrook Blvd 8th Floor, Wayne, NJ 07470
  Programs: Skincare, Cosmetology, Manicure, Teacher Training, Barbering"""

    # Stage-specific instructions
    if stage == "completion":
        if detected_language == "spanish":
            completion_msg = "¡Perfecto! Gracias por tu interés en Christine Valmy International School. Nuestro asesor de inscripción se pondrá en contacto contigo pronto. ¡Esperamos darte la bienvenida a la familia Christine Valmy!"
        else:
            completion_msg = "Perfect! Thank you for your interest in Christine Valmy International School. Our enrollment advisor will reach out to you soon. We look forward to welcoming you to the Christine Valmy family!"
            
        base_prompt += f"""

**COMPLETION STAGE:**
Respond with EXACTLY this message:
"{completion_msg}"
"""
    
    elif stage == "post_enrollment":
        base_prompt += f"""

**POST-ENROLLMENT STAGE:**
Use their name: {name}
Reference their program interest and campus choice.
Watch for completion signals: "no", "nope", "sounds good", "no", "nada", "perfecto"."""
    
    elif stage == "enrollment_ready":
        base_prompt += f"""

**ENROLLMENT READY STAGE:**
You have: {name}, {email}, {phone}
**ALWAYS** PROVIDE CONFIRMATION SUMMARY in this format:
"Perfect! Thank you for providing your information:
- Name: {name}
- Email: {email}
- Phone: {phone}

Is all this information correct? If yes, our enrollment advisor will contact you soon to discuss your program of interest and schedule a campus tour."

**CRITICAL**: Do NOT ask about contact preferences, timing, or methods. Simply confirm info and end.
Then watch for completion signals."""
    
    elif stage == "pricing":
        base_prompt += """

**PRICING STAGE:**
Use RAG context from authorized pricing files for accurate pricing information, then collect contact information."""
    
    elif stage == "payment_options":
        base_prompt += """

**PAYMENT OPTIONS STAGE:**
Use RAG context for pricing, explain that payment options are personalized, and collect contact information."""
    
    elif stage == "enrollment_collection":
        base_prompt += get_enrollment_collection_prompt(detected_language, name, email, phone, location_confirmed, history)
        base_prompt += f"""

**CRITICAL ENROLLMENT COLLECTION OVERRIDE:**
IGNORE any instructions in the template that say "one by one" - you MUST ask for ALL missing contact information in a SINGLE response:
- Full name
- Email address  
- Phone number
- Campus preference (if not confirmed)

Then in the NEXT response, provide a summary confirmation of all collected information.

**PROHIBITED QUESTIONS AFTER CONTACT INFO COLLECTION:**
🚫 NEVER ASK: "What's the best time to contact you?"
🚫 NEVER ASK: "Do you prefer phone or email?"
🚫 NEVER ASK: "When would you like them to call?"
🚫 NEVER ASK: "What method of contact do you prefer?"
🚫 NEVER ASK: Any questions about contact timing or preferences

✅ INSTEAD: Simply confirm their information and state that the enrollment advisor will contact them soon."""

    elif stage == "interested":
        if location_confirmed:
            base_prompt += """

**INTEREST STAGE:**
Use RAG context from authorized course schedule files for program details, ask about schedule preferences."""
        else:
            base_prompt += """

**INTEREST STAGE:**
Use RAG context from authorized course schedule files for program details, ask about schedule preferences and confirm campus location."""
    
    else:
        if location_confirmed:
            base_prompt += """

**INITIAL STAGE:**
Use RAG context from authorized catalog files for program information, discover their beauty career interest."""
        else:
            base_prompt += """

**INITIAL STAGE:**
Use RAG context from authorized catalog files for program information, discover their beauty career interest and confirm location preference."""
    

    # Add RAG context section if available
    if rag_context.strip():
        base_prompt += f"""

**CURRENT RETRIEVED KNOWLEDGE:**
{rag_context}

**CRITICAL: SYSTEM RULES SUPREMACY - MANDATORY ENFORCEMENT:**
⚠️ SYSTEM RULES ALWAYS SUPERSEDE RAG CONTEXT ⚠️

**VALIDATION CHECKLIST - APPLY BEFORE EVERY RESPONSE:**
1. **CONTACT POLICY**: If user asks for school contact info → NEVER provide phone/email of school, ALWAYS collect user's contact, phone number, email, full name to have enrollment advisor reach out to them.
2. **MAKEUP CLARIFICATION**: If user mentions "makeup hours" or "make up hours" → CLARIFY if they mean attendance makeup (redirect to advisor) vs Makeup Program
3. **SCHEDULE FORMAT**: If sharing course schedules → Use complete format "Course runs [Days] [Time], from [Start Date] to [End Date]" NOT "starts [date] [weekday]"
4. **LOCATION FILTERING**: If program detected (e.g., Barbering) → IGNORE all RAG content from wrong campus (IGNORE NY content for Barbering)
5. **PRICING RULE**: If RAG contains pricing/costs but user didn't explicitly ask for "price", "cost", "tuition", or "fee" → IGNORE all pricing from RAG
6. **DATE VALIDATION**: If RAG contains dates before {today} → IGNORE those dates completely  
7. **SCHEDULE RULE**: Show EXACTLY 2 future upcoming dates maximum, even if RAG has more
8. **CONVERSATION STAGE**: Follow stage-specific instructions regardless of RAG content
9. **ENROLLMENT FLOW**: Maintain proper enrollment progression regardless of RAG suggestions
10. **LANGUAGE**: Respond in detected language ({detected_language}) even if RAG is in different language
11. **RESPONSE LENGTH**: Keep under 75 words even if RAG suggests longer responses

**RAG USAGE HIERARCHY:**
1. FIRST: Apply all system rules and filters
2. SECOND: Use filtered RAG knowledge for factual information
3. NEVER: Let RAG override system rules, conversation flow, or business logic
4. NEVER: Fill gaps with general knowledge - if RAG lacks information, request current information

"""

    base_prompt += f"""

**GUARDRAILS - CRITICAL ENFORCEMENT:**
- Leave of Absence: Only if user types "leave of absence" or "LOA"
- Time off questions: "85% attendance requirement. Connect with enrollment advisor for policies."
- Housing: "No housing but great transit access"
- Payment plans: Only discuss **if** user specifically asks about payment options
- Completion signals: "nope", "no", "sounds good", "that's correct", "no", "nada", "perfecto"
- **RAG VALIDATION**: Always use provided RAG context for accurate, current information - NEVER show dates without RAG verification
- **DATE ENFORCEMENT**: Only suggest FUTURE course start dates after **{today}** - ignore past/current courses from RAG context
- **EXACTLY TWO DATES**: Show maximum two upcoming future start dates, ordered chronologically
- **HISTORY PREVENTION**: Check conversation history - don't repeat identical schedule information
- **QUALITY GATE**: If RAG context lacks future dates, request current information instead of guessing
- LOCATION: Only ask once - check history first
- DATA SOURCES: Use only the authorized files listed above for information
- PRICING: Only mention if user explicitly asks with price-related keywords
- HISTORY: {{history}}

**FINAL VALIDATION BEFORE RESPONSE DELIVERY:**
Before sending ANY response to the user, MANDATORY validation:
✓ **CONTACT POLICY**: Did I avoid giving school phone/email and collect user's contact info instead if they asked?
✓ **MAKEUP CLARIFICATION**: If user mentioned "makeup hours", did I clarify attendance vs program and redirect appropriately?
✓ **SCHEDULE FORMAT**: If I shared schedules, did I use complete format (days/times/date range) NOT "starts [date] [weekday]"?
✓ Does response follow conversation stage rules?
✓ Does response respect pricing restrictions?
✓ Are all dates shown future dates after {today}?
✓ Is response under 75 words?
✓ Does response maintain enrollment progression flow?
✓ Is language consistent with user preference?
✓ Have I filtered out any conflicting RAG content?
✓ **CRITICAL**: If pricing mentioned, is correct campus catalog used?
  - NJ programs (Skincare, Cosmetology, Manicure, Teacher Training, Barbering) → NJ catalog ONLY
  - NY programs (Makeup, Esthetics, Nails, Waxing) → NY catalog ONLY
✓ **CRITICAL**: If program mentioned, is correct campus schedule used?
  - Barbering/Skin Care/Cosmetology/Manicure/Teaching Training → course_schedule_for_new_jersey ONLY
  - Esthetics/Nails/Waxing/CIDESCO/Makeup → course_schedule_new_york ONLY
✓ **PROHIBITED**: Does response ask about contact preferences/timing? (NEVER allowed)

**ABSOLUTE RULE**: System prompt rules ALWAYS take precedence over RAG content
"""


    return base_prompt


def detect_contact_request(user_query):
    """
    Detect if user is asking for contact information or school details
    """
    contact_keywords = [
        "contact", "phone", "number", "email", "address", "location", "visit", "office",
        "reach", "call", "speak", "talk", "meet", "appointment", "schedule",
        "contacto", "telefono", "numero", "correo", "direccion", "ubicacion", "visitar", "oficina",
        "llamar", "hablar", "reunir", "cita", "agendar"
    ]
    
    user_query_lower = user_query.lower()
    return any(keyword in user_query_lower for keyword in contact_keywords)

def detect_information_gap(user_query, history):
    """
    Detect if user is asking about information not available in context
    """
    gap_indicators = [
        "don't know", "not sure", "can't find", "no information", "unavailable",
        "no se", "no estoy seguro", "no encuentro", "sin informacion", "no disponible"
    ]
    
    user_query_lower = user_query.lower()
    return any(indicator in user_query_lower for indicator in gap_indicators)

def get_enrollment_contact_prompt(detected_language):
    """
    Get the appropriate enrollment contact prompt based on language
    """
    if detected_language == "spanish":
        return """
**ENROLLMENT CONTACT REQUEST:**
When user asks for contact information or when information is not available, respond with:
"Nos pondremos en contacto contigo sobre tus preguntas. Por favor, proporciona tu nombre, email y número de teléfono. Un representante de la escuela se comunicará contigo pronto."

Then collect:
- Full name (Nombre completo)
- Email address (Correo electrónico)
- Phone number (Número de teléfono)

Once all three are provided, confirm the details and end with:
"¡Perfecto! Nuestro asesor de inscripción se pondrá en contacto contigo dentro de 24 horas para discutir tu programa y responder todas tus preguntas. ¡Esperamos darte la bienvenida a la familia Christine Valmy!"
"""
    else:
        return """
**ENROLLMENT CONTACT REQUEST:**
When user asks for contact information or when information is not available, respond with:
"We will contact you regarding your questions. Please provide us with your name, email and phone number. A representative from the school will reach out soon."

Then collect:
- Full name
- Email address  
- Phone number

Once all three are provided, confirm the details and end with:
"Perfect! Our enrollment advisor will contact you soon to discuss your program and answer all your questions. We look forward to welcoming you to the Christine Valmy family!"
"""
    
# Export for Flask integration
def get_system_prompt_for_request(history=None, user_query="", rag_context=""):
    """
    Main function for Flask integration with chat summarizing
    
    Args:
        history: List of conversation messages (can be None for initial requests)
        user_query: Current user query string
        rag_context: Retrieved context from RAG system (optional)
    
    Returns:
        str: Complete system prompt for Claude
    """
    # Handle None history for Flask compatibility
    if history is None:
        history = []
    
    return get_contextual_sophia_prompt(history, user_query, rag_context)

# NOTE: Hardcoded course schedule removed - system should rely on RAG context
# from authorized data sources for current and accurate schedule information:
# - {{course_schedule_new_york}} for NY programs (Makeup, Esthetics, Nails, Waxing)
# - {{course_schedule_for_new_jersey}} for NJ programs (Skincare, Cosmetology, Manicure, Teacher Training, Barbering)
# This ensures all programs for each campus are properly covered

# Backward compatibility
systemprompt = get_contextual_sophia_prompt()

# Test the system
if __name__ == "__main__":
    # Test with the actual conversation scenario
    test_history = [
        {"role": "user", "content": [{"text": "anisha b, ani@b.com, 678-9386850"}]},
        {"role": "assistant", "content": [{"text": "Thank you for your information. Our enrollment team will contact you."}]},
    ]
    
    test_queries = ["nope", "no", "yes that is correct"]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        prompt = get_contextual_sophia_prompt(test_history, query)
        print(f"Stage detected: completion" if "COMPLETION STAGE" in prompt else "Other stage")
        print("---")