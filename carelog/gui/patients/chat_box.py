import streamlit as st
from streamlit_chat import message

def chat_box():
   #initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    MAX_MESSAGES = 20  #limits the message to a constant of 20

    # a chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask a health-related question:")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            #appends the user message
            st.session_state.messages.append(("user", user_input))
            
            # Bot response logic
            response_parts = []
            text = user_input.lower()

            # dictionary of categories: key is category name (for reference), value is tuple of (keywords, response_parts)
            categories = {
                "sleep": (
                    ["sleep", "rest", "insomnia", "nap", "tired", "fatigue", "sleep apnea", "circadian", "jet lag"],
                    [
                        "Maintain 7-9 hours of consistent sleep daily to stabilize your circadian rhythm.",
                        "Avoid caffeine and blue light at least 2 hours before bedtime.",
                        "Establish a calming pre-sleep routine such as light stretching or reading.",
                        "If dealing with sleep apnea, consider consulting a specialist for CPAP therapy."
                    ]
                ),
                "diet": (
                    ["diet", "food", "meal", "eat", "nutrition", "snack", "vitamins", "supplements", "calories"],
                    [
                        "Adopt a balanced diet with adequate macronutrients and micronutrients.",
                        "Consume fiber-rich foods like oats, fruits, and legumes to maintain gut health.",
                        "Limit trans fats and processed sugar to reduce metabolic risk factors.",
                        "Incorporate vitamins like B12 or iron if deficient, but consult a doctor first."
                    ]
                ),
                "hydration": (
                    ["drink", "water", "hydration", "thirst", "dehydrated", "electrolytes"],
                    [
                        "Ensure sufficient hydration — about 2 to 3 liters of water daily depending on activity level.",
                        "Dehydration can impair cognitive function and cardiovascular performance.",
                        "Track your urine color; pale yellow usually indicates optimal hydration.",
                        "Replenish electrolytes with drinks like coconut water after intense exercise."
                    ]
                ),
                "exercise": (
                    ["exercise", "workout", "gym", "training", "fitness", "cardio", "strength", "running", "yoga"],
                    [
                        "Engage in at least 150 minutes of moderate-intensity exercise weekly.",
                        "Combine aerobic and resistance training to enhance cardiovascular and muscular health.",
                        "Include flexibility and balance routines such as yoga or Pilates.",
                        "Start slow to avoid injury and gradually increase intensity."
                    ]
                ),
                "stress": (
                    ["stress", "anxiety", "pressure", "tense", "overwhelmed", "burnout", "cortisol"],
                    [
                        "Practice mindfulness or breathing exercises to regulate your parasympathetic nervous system.",
                        "Allocate time for leisure and non-work-related activities.",
                        "Avoid chronic stressors; prolonged cortisol elevation may affect immunity.",
                        "Try progressive muscle relaxation for immediate tension relief."
                    ]
                ),
                "mental": (
                    ["mental", "depression", "mood", "sad", "lonely", "therapy", "psychology", "bipolar", "ptsd"],
                    [
                        "Prioritize mental wellness; consider journaling or therapy for emotional regulation.",
                        "Social interaction and sunlight exposure can elevate serotonin levels.",
                        "Seek professional help if symptoms persist for over two weeks.",
                        "Hotlines like the National Suicide Prevention Lifeline are available 24/7."
                    ]
                ),
                "social": (
                    ["friends", "relationship", "family", "social", "connect", "loneliness", "networking"],
                    [
                        "Healthy social bonds improve emotional resilience and overall well-being.",
                        "Spend quality time with supportive individuals who promote positivity.",
                        "Set boundaries to protect your mental energy.",
                        "Join clubs or online communities to expand your social circle."
                    ]
                ),
                "time": (
                    ["time", "schedule", "productivity", "focus", "plan", "procrastination", "deadlines"],
                    [
                        "Use structured time-blocking to allocate focused work and rest periods.",
                        "Avoid multitasking; deep work enhances cognitive efficiency.",
                        "Review your daily priorities to prevent burnout.",
                        "Tools like Pomodoro timers can help maintain focus."
                    ]
                ),
                "weight": (
                    ["weight", "bmi", "obese", "underweight", "fat", "slim", "metabolism", "calorie deficit"],
                    [
                        "Monitor your BMI, but focus on body composition rather than numbers alone.",
                        "Gradual, sustainable changes yield better metabolic adaptations.",
                        "Consult a dietitian for personalized caloric requirements.",
                        "Incorporate strength training to boost metabolism."
                    ]
                ),
                "digestive": (
                    ["stomach", "digestion", "gut", "bloating", "constipation", "diarrhea", "ibs"],
                    [
                        "Include probiotics like yogurt and prebiotics such as bananas for gut flora balance.",
                        "Eat smaller, more frequent meals to reduce digestive load.",
                        "Stay hydrated and include fiber to aid peristalsis.",
                        "Avoid trigger foods if you suspect IBS; keep a food diary."
                    ]
                ),
                "cardiovascular": (
                    ["heart", "blood pressure", "cholesterol", "pulse", "cardio", "arrhythmia", "stroke"],
                    [
                        "Maintain optimal LDL and HDL levels through regular physical activity.",
                        "Reduce sodium intake to manage hypertension.",
                        "Monitor resting heart rate — a lower RHR often indicates better fitness.",
                        "Know the signs of stroke: FAST (Face, Arms, Speech, Time)."
                    ]
                ),
                "respiratory": (
                    ["lungs", "breath", "asthma", "oxygen", "copd", "shortness of breath"],
                    [
                        "Practice diaphragmatic breathing to improve oxygen exchange efficiency.",
                        "Avoid exposure to pollutants and second-hand smoke.",
                        "Regular aerobic exercise supports pulmonary capacity.",
                        "Use inhalers as prescribed for asthma management."
                    ]
                ),
                "skin": (
                    ["skin", "acne", "eczema", "rash", "face", "dermatitis", "psoriasis"],
                    [
                        "Stay hydrated and maintain a consistent skincare routine.",
                        "Avoid excessive sugar and dairy if prone to acne.",
                        "Use sunscreen daily to prevent UV-induced damage.",
                        "Moisturize regularly for conditions like eczema."
                    ]
                ),
                "posture": (
                    ["posture", "sitting", "ergonomic", "back pain", "neck pain", "sciatica"],
                    [
                        "Maintain neutral spine alignment when sitting or standing.",
                        "Take micro-breaks every 30 minutes to stretch and realign.",
                        "Use ergonomic furniture to reduce musculoskeletal strain.",
                        "Strengthen core muscles to support better posture."
                    ]
                ),
                "immune": (
                    ["immune", "sick", "virus", "infection", "cold", "flu", "autoimmune"],
                    [
                        "Support your immune function with vitamins C, D, and zinc.",
                        "Adequate sleep enhances lymphocyte activity.",
                        "Engage in moderate exercise, but avoid overtraining.",
                        "Manage autoimmune conditions with anti-inflammatory diets."
                    ]
                ),
                "chronic": (
                    ["diabetes", "hypertension", "cholesterol", "arthritis", "osteoporosis", "thyroid"],
                    [
                        "Adhere to prescribed medication and track health metrics regularly.",
                        "Maintain a low-sodium and low-sugar diet to stabilize levels.",
                        "Regular medical check-ups help with early intervention.",
                        "For osteoporosis, ensure adequate calcium and vitamin D intake."
                    ]
                ),
                "hygiene": (
                    ["hygiene", "clean", "wash", "sanitize", "germs", "bacteria"],
                    [
                        "Wash your hands frequently, especially before meals.",
                        "Maintain oral hygiene to prevent bacterial buildup.",
                        "Change clothes and linens regularly to reduce pathogens.",
                        "Use alcohol-based sanitizers when soap isn't available."
                    ]
                ),
                "eye": (
                    ["eye", "vision", "screen", "blur", "glasses", "cataracts", "dry eyes"],
                    [
                        "Follow the 20-20-20 rule: every 20 minutes, look 20 feet away for 20 seconds.",
                        "Adjust screen brightness to match room lighting.",
                        "Eat lutein-rich foods like spinach and eggs for retinal health.",
                        "Use lubricating drops for dry eyes."
                    ]
                ),
                "cognitive": (
                    ["memory", "focus", "brain", "study", "learn", "alzheimer", "dementia"],
                    [
                        "Omega-3 fatty acids and adequate sleep enhance cognitive retention.",
                        "Practice spaced repetition to reinforce long-term memory.",
                        "Stay mentally active through puzzles or reading.",
                        "Reduce risk of dementia with a Mediterranean diet."
                    ]
                ),
                "technology": (
                    ["phone", "social media", "screen time", "computer", "scroll", "blue light"],
                    [
                        "Limit screen exposure before sleep to protect melatonin cycles.",
                        "Take digital detox breaks to reduce eye strain and anxiety.",
                        "Use apps mindfully rather than habitually.",
                        "Enable night mode to filter blue light."
                    ]
                ),
                "environment": (
                    ["environment", "pollution", "air", "noise", "light", "allergens"],
                    [
                        "Maintain clean indoor air with proper ventilation.",
                        "Reduce noise exposure for better concentration.",
                        "Natural light during the day supports circadian rhythm.",
                        "Use air purifiers if allergens are an issue."
                    ]
                ),
                "mindfulness": (
                    ["mindful", "meditate", "breathing", "yoga", "tai chi", "zen"],
                    [
                        "Meditation enhances self-awareness and emotional regulation.",
                        "Slow breathing activates the vagus nerve, reducing heart rate.",
                        "Incorporate yoga or tai chi for both physical and mental balance.",
                        "Start with 5-minute sessions to build a habit."
                    ]
                ),
                "bone": (
                    ["bone", "osteoporosis", "calcium", "fracture", "density"],
                    [
                        "Consume calcium-rich foods like dairy or leafy greens for bone strength.",
                        "Weight-bearing exercises help maintain bone density.",
                        "Get sufficient vitamin D from sunlight or supplements.",
                        "Avoid smoking, as it weakens bones."
                    ]
                ),
                "dental": (
                    ["teeth", "dental", "gums", "cavity", "floss", "braces"],
                    [
                        "Brush twice daily and floss to prevent plaque buildup.",
                        "Limit sugary drinks to reduce cavity risk.",
                        "Regular dental check-ups catch issues early.",
                        "Use fluoride toothpaste for enamel protection."
                    ]
                ),
                "pain": (
                    ["pain", "headache", "migraine", "chronic pain", "ache"],
                    [
                        "For headaches, stay hydrated and manage stress.",
                        "Use heat or cold packs for muscle pain relief.",
                        "Over-the-counter meds like ibuprofen can help, but consult a doctor.",
                        "Chronic pain may benefit from physical therapy."
                    ]
                ),
                "allergy": (
                    ["allergy", "pollen", "sneeze", "hay fever", "anaphylaxis"],
                    [
                        "Identify triggers and avoid them when possible.",
                        "Antihistamines can alleviate symptoms like sneezing.",
                        "Keep windows closed during high pollen seasons.",
                        "Carry an EpiPen if at risk for severe reactions."
                    ]
                ),
                "substance": (
                    ["smoking", "alcohol", "drugs", "addiction", "quit", "nicotine"],
                    [
                        "Quitting smoking improves lung function within weeks.",
                        "Limit alcohol to moderate levels to protect liver health.",
                        "Seek support groups or counseling for addiction.",
                        "Nicotine replacement therapy can aid in quitting."
                    ]
                ),
                "hormonal": (
                    ["hormone", "thyroid", "menopause", "testosterone", "estrogen"],
                    [
                        "Balanced hormones support energy and mood.",
                        "For thyroid issues, monitor TSH levels regularly.",
                        "Lifestyle changes like diet can ease menopause symptoms.",
                        "Consult an endocrinologist for imbalances."
                    ]
                ),
                # Extended with a few more categories for continuation
                "reproductive": (
                    ["reproductive", "fertility", "menstruation", "pregnancy", "contraception"],
                    [
                        "Track menstrual cycles for better reproductive health awareness.",
                        "Maintain a healthy weight to support fertility.",
                        "Consult a gynecologist for contraception options.",
                        "Prenatal vitamins are crucial during pregnancy."
                    ]
                ),
                "neurological": (
                    ["neurological", "headache", "migraine", "seizure", "neuropathy"],
                    [
                        "Manage migraines with trigger avoidance and medication.",
                        "Regular check-ups for neurological symptoms are important.",
                        "Exercise can help reduce neuropathy symptoms.",
                        "Seek immediate care for sudden seizures."
                    ]
                ),
                "cancer": (
                    ["cancer", "tumor", "chemotherapy", "radiation", "screening"],
                    [
                        "Regular screenings like mammograms can detect cancer early.",
                        "Maintain a diet rich in antioxidants to reduce risk.",
                        "Support during chemotherapy includes staying hydrated and resting.",
                        "Consult oncologists for personalized treatment plans."
                    ]
                ),
                "elderly": (
                    ["elderly", "aging", "senior", "geriatric", "osteoarthritis"],
                    [
                        "Stay active to maintain mobility in older age.",
                        "Balance exercises prevent falls in seniors.",
                        "Manage osteoarthritis with low-impact activities.",
                        "Regular health check-ups are vital for elderly care."
                    ]
                )
            }

            matched = False
            for cat, (keywords, responses) in categories.items():
                if any(k in text for k in keywords):
                    response_parts.extend(responses)
                    matched = True
                    break  # only first match to save speed

            if not matched:
                response_parts = ["Stay consistent with healthy habits.", "Consult a doctor for specific issues."]
            
            # perform formatting for the bot reply 
            reply = "\n- " + "\n- ".join(response_parts)
            st.session_state.messages.append(("bot", reply))
            
            # limit message history
            if len(st.session_state.messages) > MAX_MESSAGES:
                st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

    # display chat messages in a scrollable container 
    chat_container = st.container()
    for idx, (role, text) in enumerate(st.session_state.messages):
        if role == "user":
            message(text, is_user=True, avatar_style="thumbs", key=f"user_msg_{idx}")
        else:
            message(text, avatar_style="bottts", key=f"bot_msg_{idx}")
    return None