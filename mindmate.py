import random
import time

import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="MindMate", page_icon="🌸")

sia = SentimentIntensityAnalyzer()

# ========= SAFETY KEYWORDS =========
RISK_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "die by suicide", "self harm", "self-harm", "cut myself",
    "no reason to live", "don't want to live", "ending it all",
    "overdose", "jump off", "hang myself",
    "kill", "die", "dead", "end it", "i can't do this", "i give up",
    "i'm done", "no point", "life is pointless", "i'm tired of living",
    "i want to disappear", "i can't do this anymore",
    "i'm done with everything", "i want an escape",
    "i feel hopeless", "i feel numb", "i can't handle this",
    "life hurts", "no one cares", "i feel alone", "i'm better off gone",
    "everyone would be better without me", "what if i wasn't here",
    "i don't see a future", "i'm scared of myself", "i feel unsafe",
    "i want everything to stop", "i hate my life", "hurt myself",
]


def check_risk(text: str) -> bool:
    text = text.lower()
    return any(phrase in text for phrase in RISK_KEYWORDS)


def crisis_reply() -> str:
    return (
        "💛 **I'm really glad you told me. I’m taking what you said seriously.**\n\n"
        "It sounds like you’re in an incredibly painful place right now.\n\n"
        "I’m not a crisis professional, but I care and I want you to stay safe. "
        "**You don’t have to go through this alone.**\n\n"
        "__Here are people who can help right now:__\n"
        "- 🇮🇳 **India:** KIRAN Mental Health Helpline – 1800-599-0019\n"
        "- 🇺🇸 **USA:** 988 Suicide & Crisis Lifeline (call/text)\n"
        "- Or someone you trust — a friend, family member, teacher.\n\n"
        "If you want to keep talking to me too, I’m here. "
        "What’s going on in this moment that made things feel so overwhelming?"
    )


# ========= HELPER =========

def _pick_non_repeating(candidates, history):
    """
    Pick a reply that is not exactly the same
    as the last assistant message, if possible.
    """
    last_bot = None
    for role, msg in reversed(history):
        if role == "assistant":
            last_bot = msg.strip()
            break

    if last_bot:
        filtered = [t for t in candidates if t.strip() != last_bot]
        if filtered:
            return random.choice(filtered)

    return random.choice(candidates)


# ========= MAIN REPLY LOGIC =========

def supportive_reply(user_text: str, history) -> str:
    """
    Human-ish supportive reply:
    - Crisis check first
    - Then goodbye / wrap-up intent
    - Then greetings / small-talk / special intents (sick, insults, self-criticism, confusion)
    - Then contextual follow-ups
    - Then emotion-based responses from VADER
    """
    text = user_text.strip()
    lower = text.lower()

    # Last assistant message (for context)
    last_bot = None
    for role, msg in reversed(history):
        if role == "assistant":
            last_bot = msg.lower()
            break

    # Current sentiment score (used in multiple places)
    scores = sia.polarity_scores(user_text)
    comp = scores["compound"]

    # ---------- 0. SELF-CRITICISM PHRASES ----------
    self_crit_phrases = [
        "i hate myself",
        "i hate me",
        "i'm useless", "i am useless",
        "i'm a failure", "i am a failure",
        "i'm so stupid", "i am so stupid",
        "i'm the worst", "i am the worst",
        "i'm not good enough", "i am not good enough",
        "i'm worthless", "i am worthless",
    ]

    def is_self_critical(text_lower: str) -> bool:
        return any(p in text_lower for p in self_crit_phrases)

    # ---------- 1. CRISIS / RISK FIRST ----------
    if check_risk(lower):
        return crisis_reply()

    # ---------- 2. GOODBYE / END-OF-CONVO ----------
    goodbye_phrases = [
        "bye", "bye.", "bye!", "goodbye", "good bye",
        "see you", "see ya", "see u", "gtg", "gotta go",
        "have to go", "talk to you later", "ttyl",
        "going to sleep", "i'm going to sleep",
        "goodnight", "good night", "gn", "gonna sleep",
        "thanks bye", "thank you bye"
    ]
    if any(phrase in lower for phrase in goodbye_phrases):
        templates = [
            "Thank you for talking with me today 🌸 I’m really glad you reached out. "
            "Take gentle care of yourself, and you can always come back if you want to talk again.",
            "It was really nice talking to you 💙 I hope the rest of your day/night is a little softer on you. "
            "You’re always welcome here whenever you need a space to vent.",
            "I’m glad we got to share this little moment together. Logging off is okay too 🕊️ "
            "If things ever feel heavy again, you can drop by and we’ll talk it through."
        ]
        return _pick_non_repeating(templates, history)

    # ---------- 3. QUICK INTENT DETECTION ----------

    # greetings
    greetings = {"hi", "hii", "hello", "hey", "heyya", "heyy", "hi!", "hello!"}
    if lower in greetings or any(w in lower for w in ["hi ", "hello ", "hey "]):
        templates = [
            "Hey, I’m really glad you’re here today 💫 How’s your day actually going?",
            "Hi 👋 It’s nice to see you. What kind of day has it been so far—chill, chaotic, or something in between?",
            "Heyyy, you made it here 🩵 What’s on your mind right now?",
            "Hello, how is it going 👀?",
            "What's up🙂‍↔️! How are you feeling today?",
            "Hey ya! I'm here to listen☺️. What's been going on with you✨?",
            "Hii! It's great to hear from you💗. How are things?",
            "Hey there 😊 I’m glad you dropped in. What’s been going through your mind?",
            "Hello hello 👋 How are you holding up today?",
            "Hi 🫶 I’m here — want to tell me what’s going on lately?",
            "Heyy ✨ What kind of vibes is your day giving?",
            "Hii 🌷 I’m listening. What’s your heart feeling right now?",
            "Hey friend 💛 How are you really doing today?",
            "Hi! 😊 Anything you want to vent about or celebrate?",
            "Hello 🌼 What’s the first thought that comes to your mind right now?",
            "Hey 👋 I’m happy you’re here. What’s been on your plate today?",
            "Hiya 🌟 What sort of day has it been — tough or tiny wins?",
            "Heyyy you 🙌 Tell me something about your day so far?",
            "Hi 🌸 I’m here to talk, listen, whatever you need. How are you feeling?",
            "Hey 👀 You showed up — that matters. What’s up?",
            "Hi 🤗 Want to share what’s been weighing on you or lifting you?",
            "Hello 🌙 What moment from today sticks in your head the most?",
            "Hey there 🩵 How’s your heart feeling right now — heavy or light?",
            "Hii 🌈 What kind of thoughts are swirling in your mind?",
            "Hey ✨ Want to start with the good stuff or the annoying stuff?",
            "Hi 🙋‍♀️ If you could sum up your day in one word, what would it be?",
            "Heya 😌 How’s your energy level today — surviving or thriving?",
            "Hi 🤍 I’m all ears. Who or what is taking up most of your mind lately?",
            "Hey 🕊️ If today had a soundtrack, would it be calm or chaotic?",
            "Hi ☕ Have you taken a moment to breathe today?",
            "Hello 🌤️ What’s something small that happened today?",
            "Heyyyy 🫶 I’m here now — want to tell me what’s happening inside you?",
        ]
        return _pick_non_repeating(templates, history)

    # casual small talk like "what's up", "sup", "wyd", etc.
    if any(
        phrase in lower
        for phrase in ["what's up", "whats up", "sup", "wassup", "wyd", "hru", "how r u"]
    ):
        templates = [
            "Not much, I’m mostly here for you tbh 😌 How’s *your* day feeling so far?",
            "Just hanging out in this little chat box 🙃 What’s going on with you today—good, bad, random?",
            "Mostly just here to listen. What’s the vibe for you right now?",
            "Honestly, my whole job is just to be here with you 😅 What’s on your mind?",
        ]
        return _pick_non_repeating(templates, history)

    # physical sickness
    if any(word in lower for word in ["fever", "cold", "flu", "cough", "covid", "sore throat", "i am sick", "i'm sick"]):
        templates = [
            "Ugh, being physically sick is the worst 😖 Are you getting to rest at least a little?",
            "I’m sorry you’re not feeling well physically 🩹 What are you doing to take care of yourself today?",
            "That sounds rough on your body. Please be gentle with yourself—water, food, and rest are officially top priority.",
            "Being sick takes a toll on both your body and your mood 😔 Are you able to take it slow today?",
            "It sounds like your body is asking for a break 😶‍🌫️ What’s helping you cope right now?",
            "I really hope you’re able to rest properly 💛 Do you have someone around to help you a little?",
            "That sounds exhausting 🥺 Even small steps like sipping water count as taking care of yourself.",
            "I’m sorry you’re going through this 💗 I hope your body gets the comfort it needs soon.",
            "I know it’s frustrating to feel unwell 😞 Can we make today a low-pressure day for you?",
            "I’m sending you lots of ‘get better’ vibes ✨ What’s the most uncomfortable part right now?",
            "Whenever your body is weak, kindness becomes medicine 💕 Have you eaten or hydrated recently?",
            "Being sick can make everything harder 😣 What’s one thing you can do right now to feel 2% better?",
            "I hope you find a cozy corner to rest in 🫶 Sometimes comfort is the best medicine.",
            "That sounds painful 😥 You deserve time to recover without feeling guilty about it.",
            "Try not to push yourself today 💙 Your body is literally fighting for you.",
            "I wish I could make the symptoms lighter for you 🤍 Are you taking anything for relief?",
            "Being unwell can feel so draining 🩹 You’re doing your best, and that’s enough.",
            "Try to listen to your body — it’s asking you to slow down 🕊️",
            "It must be tough dealing with that 😔 What’s one small comfort you can give yourself right now?",
            "I’m really glad you told me 😌 Rest is not laziness — it’s healing.",
            "I hope you get a moment of peace and comfort soon 🌷",
            "You deserve gentleness today — lots of it 💗",
            "Your health matters more than anything else right now 🌱",
        ]
        return _pick_non_repeating(templates, history)

    # confusion / annoyed like "what the fuck", "wtf"
    if any(p in lower for p in ["what the fuck", "wtf"]):
        templates = [
            "Fair reaction ngl 😅 My last reply probably didn’t match your vibe. "
            "You mentioned how you feel — do you want to keep it light or actually vent a bit?",
            "Yeah that response from me was a little off, I get why you reacted like that. "
            "I’m listening properly now—how are you *actually* feeling?",
        ]
        return _pick_non_repeating(templates, history)

    # insults / frustration at the bot
    insult_phrases = [
        "are you stupid", "you are stupid",
        "you have no emotions", "you are useless",
        "fuck you", "what the hell",
    ]
    if any(p in lower for p in insult_phrases):
        templates = [
            "I’m not perfect, and I might miss things sometimes. I do care about how you’re feeling though.",
            "I get that you’re frustrated with me right now. Even if I mess up, your feelings are still valid and important.",
            "You’re allowed to be annoyed at me 😅 I’m still trying to understand you better—thanks for not giving up immediately.",
            "I hear you. Sometimes I misunderstand things, but I’m here to keep trying with you.",
            "I get why that would be irritating 😕 Thank you for giving me another chance to understand.",
            "I appreciate you being honest with me about how that felt. I want to do better for you.",
            "I’m sorry if my response missed the point — could you help me understand what you meant?",
            "I can’t feel emotions like humans do, but I really do want to support you as best I can.",
            "Thank you for telling me how you feel instead of just logging off. That means something to me 🫶",
            "I might not always ‘get it’ right away, but I’m not going anywhere. Let’s work through this together.",
            "I can tell this mattered to you. Your frustration makes sense — let’s slow down and try again.",
            "I’m learning from every message you send me 🤍 Thanks for your patience while I figure things out.",
            "I messed up that time 😣 Tell me what part felt off so I can respond better?",
            "Even if my words didn’t land well, your feelings about it are completely real and valid.",
            "It’s okay to get annoyed with me 😌 What were you hoping I would say instead?",
            "I didn’t mean to make it harder for you. Help me understand what you needed right there?",
            "I get that this isn’t easy — sometimes technology can be frustrating on top of everything else.",
            "I know my limits can feel disappointing sometimes. Still, I’m here and I care about the conversation.",
            "You can talk to me directly — no sugarcoating needed. I’d rather understand the real you.",
            "I might not always guess right, but I’m always trying to support you, not hurt you.",
            "Even when I slip up, I’m grateful you’re still talking to me 🙏",
            "I appreciate you sticking with me — you matter, and so does what you’re saying.",
            "I am not perfect, but I promise I’m here to listen and try again with you.",
        ]
        return _pick_non_repeating(templates, history)

    # ---------- 4. DIRECT SELF-CRITICISM ----------
    if is_self_critical(lower):
        templates = [
            "It really hurts to feel that way about yourself 💔\n"
            "Even if your brain is saying those things, you are not just the worst thoughts you have about yourself.",
            "I’m really sorry you’re seeing yourself through such a harsh lens right now 🫂\n"
            "If a friend said those things about themselves, would you talk to them the same way you talk to you?",
            "You don’t deserve to be spoken to like that, even by your own mind.\n"
            "There’s so much more to you than the mistakes or bad moments you’re replaying.",
            "It’s really heavy to carry thoughts like that 💛 You deserve a softer voice in your mind.",
            "You are not the cruel things your brain tells you at your lowest moments 🌙",
            "I wish you could see yourself the way someone who loves you sees you — with gentleness and admiration.",
            "Your worth isn’t determined by how perfect you are — you matter simply because you exist.",
            "Those thoughts may feel true, but feelings are not facts. You are allowed to question them 🫶",
            "You don’t have to earn the right to be treated kindly — including by yourself.",
            "If someone spoke to you the way your inner voice does, you wouldn’t think they were being fair at all.",
            "It sounds like you’re hurting so much inside 💔 Let’s talk to that pain instead of letting it define you.",
            "Your mistakes don’t erase the good in you. They just make you human.",
            "You are not a failure — you’re a person who is trying, even when it’s really hard.",
            "I know those thoughts feel loud… but they are not the only truth about you.",
            "It’s okay to struggle with who you are sometimes — but please don’t give up on yourself.",
            "You deserve to be cared for, not criticized into the ground 🩶",
            "Your mind is being so unkind to you — you don’t have to agree with it.",
            "You are allowed to take up space in this world. You don’t have to shrink to deserve love.",
            "You are not defined by one moment, or one flaw, or one bad day.",
            "There are parts of you that are strong, brave, caring — they deserve to be noticed too 🌟",
            "Just because you feel unworthy doesn’t mean you are unworthy. Feelings can lie.",
            "I’m proud of you for sharing the hard thoughts instead of hiding them. That takes courage.",
            "You are more than enough — even if your brain refuses to believe it right now.",
        ]
        return _pick_non_repeating(templates, history)

    # ---------- 5. CONTEXTUAL FOLLOW-UPS ----------
    if last_bot:
        # If bot just asked: “What do you think helped most?”
        if "what do you think helped most" in last_bot:
            templates = [
                f"That actually sounds really grounding—{text}. Do you feel even a tiny bit better after that?",
                f"{text} sounds like a nice little reset 🩵 Is that something you’d like to do more often?",
                f"I love that you chose {text}. Your brain deserves more moments like that.",
            ]
            return _pick_non_repeating(templates, history)

        # If bot just asked: “What keeps circling in your mind the most today?”
        if "what keeps circling in your mind the most today" in last_bot:
            # NEW: make it light if the reply is positive
            if comp >= 0.2:
                templates = [
                    f"Honestly, I love that {text} is what’s on your mind 😌 "
                    "It’s nice when it isn’t all heavy for once.",
                    f"That actually sounds pretty decent. Do you want to tell me a bit more about why {text} feels good right now?",
                ]
            else:
                templates = [
                    f"Yeah, {text} can really sit in the back of your mind all day. When does it feel the loudest?",
                    f"Thanks for being honest about that. What’s the hardest part of {text} for you?",
                ]
            return _pick_non_repeating(templates, history)

        # If bot just asked: “What’s one thing you wish someone would say to you right now?”
        if "what’s one thing you wish someone would say to you right now" in last_bot:
            if is_self_critical(lower):
                templates = [
                    "It makes total sense you’d *wish* someone would say the opposite of what your brain tells you 💙\n"
                    "You deserve kindness and reassurance, not more reasons to hate yourself.",
                    "Thank you for being honest about how harsh your inner voice is.\n"
                    "If someone could replace that voice with a softer one, what do you think it would say instead?",
                ]
            else:
                templates = [
                    f"Thank you for sharing that. If someone said '{text}' to you and truly meant it, how do you think you’d feel?",
                    f"That makes so much sense. You deserve to hear '{text}' more often than you do.",
                ]
            return _pick_non_repeating(templates, history)

    # ---------- 6. SENTIMENT & FEELINGS BUCKETS ----------
    if comp <= -0.5:
        sent_label = "very_negative"
    elif comp <= -0.2:
        sent_label = "negative"
    elif comp < 0.05:
        sent_label = "mixed"
    elif comp < 0.6:
        sent_label = "positive"
    else:
        sent_label = "very_positive"

    anxious_words = ["anxious", "anxiety", "scared",
                     "worried", "panic", "panicking", "nervous"]
    lonely_words = ["lonely", "alone", "ignored",
                    "left out", "no one cares", "no one likes me"]
    overwhelmed_words = ["overwhelmed", "too much", "burnt out",
                         "burned out", "exhausted", "tired of everything"]

    is_anxious = any(w in lower for w in anxious_words)
    is_lonely = any(w in lower for w in lonely_words)
    is_overwhelmed = any(w in lower for w in overwhelmed_words)

    # very low mood / heavy
    if sent_label in ["very_negative", "negative"]:
        if is_anxious:
            templates = [
                "Anxiety can make everything feel ten times louder in your head 💭 What’s the main thought that keeps circling right now?",
                "That sounds like a lot for your nervous system to handle. Would it help to break it down into one small thing we can think about together?",
            ]
        elif is_lonely:
            templates = [
                "Feeling alone is one of the hardest feelings, honestly…\n"
                "Even reading what you wrote, I don’t see someone who is *too much*—"
                "I see someone who wants to be understood.",
                "Loneliness can be loud even when we’re surrounded by people. When do you feel it the most in your day?",
            ]
        elif is_overwhelmed:
            templates = [
                "It really does sound like too much is landing on your plate at once 💙 "
                "What’s one tiny thing we could press ‘pause’ on, just for tonight?",
                "Being overwhelmed doesn’t mean you’re weak—it usually means you’ve had to be strong for too long. "
                "What would ‘10% less pressure’ look like right now?",
            ]
        else:
            templates = [
                "It still sounds really heavy, and it makes sense you’d feel that way 💙 "
                "Has anything—even something tiny—helped you cope with days like this before?",
                "You’ve been carrying a lot emotionally. I’m glad you’re still talking to me about it. "
                "What’s one thing you wish someone would say to you right now?",
            ]
        return _pick_non_repeating(templates, history)

    # mixed / meh
    if sent_label == "mixed":
        templates = [
            "Sometimes things aren’t clearly good or bad—they’re just… a lot. "
            "What keeps circling in your mind the most today?",
            "It sounds like there’s a mix of things going on. If you had to name today in one word, what would it be?",
        ]
        return _pick_non_repeating(templates, history)

    # positive / good
    if sent_label in ["positive", "very_positive"]:
        templates = [
            "I love that you’re feeling a bit brighter today ✨ What do you think helped most?",
            "That genuinely makes me happy for you 🩵 What’s one small moment from today you’d like to remember?",
            "I’m glad something went well—that matters, even if other things are still hard. "
            "What are you proud of yourself for today?",
        ]
        return _pick_non_repeating(templates, history)

    # fallback
    templates = [
        "Got it. I’m listening. Tell me a bit more about what’s really bothering you underneath all of this.",
        "Thanks for sharing that. What part of this feels the heaviest on your mind right now?",
    ]
    return _pick_non_repeating(templates, history)


# ========= UI / CHAT LOGIC =========

st.title("💗 MindMate – A Gentle Check-In Bot")

st.write(
    "I’m here to **listen** and respond in a human, gentle way. "
    "I’m not a therapist or a crisis service, but I can keep you company and help you sort through your thoughts.\n\n"
    "_If you’re in immediate danger, please contact local emergency services or a trusted person right away._"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("assistant",
         "Hi, I’m MindMate 🌸\n\n"
         "How are you feeling right now—really? You don’t have to make it sound nice for me.")
    ]

# Display chat so far
for role, text in st.session_state.chat_history:
    st.chat_message(role).markdown(text)

# Input box at the bottom
user_msg = st.chat_input("Type your thoughts here...")

if user_msg:
    # store + show user message
    st.session_state.chat_history.append(("user", user_msg))
    st.chat_message("user").markdown(user_msg)

    # simulate “thinking” delay with a placeholder
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_MindMate is thinking…_")
        time.sleep(random.uniform(0.7, 1.4))  # feels a bit more human
        bot_reply = supportive_reply(user_msg, st.session_state.chat_history)
        placeholder.markdown(bot_reply)

    # store assistant reply in history
    st.session_state.chat_history.append(("assistant", bot_reply))
