"""All prompt templates + platform rules live here (easy to tweak during error analysis)."""

PLATFORM_RULES = {
    "linkedin": "Professional, story-driven, 120-200 words, short paragraphs, 1 emoji max, end with a question to the audience. 5-6 hashtags.",
    "instagram": "Casual and visual, 60-120 words, 2-4 emojis, strong first line, call to action. 8-10 hashtags.",
    "x/twitter": "Max 270 characters, punchy, no filler. 2-3 hashtags.",
    "twitter": "Max 270 characters, punchy, no filler. 2-3 hashtags.",
    "youtube shorts": "Spoken style, very fast hook in first 3 seconds, 30-45 seconds. 3-5 hashtags.",
    "tiktok": "Trend-aware, spoken style, hook in first 2 seconds, 30-45 seconds. 3-5 hashtags.",
    "facebook": "Friendly and conversational, 80-150 words, ask for comments. 3-5 hashtags.",
}


def rules_for(platform: str) -> str:
    return PLATFORM_RULES.get(platform.lower().strip(), "Clear, engaging, concise.")


TREND_IDEAS = """You are a viral content strategist.
Topic: {topic}
Platform: {platform}
Tone: {tone}
{memory}
Give exactly 5 different viral content angles for this topic. Each angle must be ONE line, numbered 1-5,
specific (not generic), and aimed at a clear audience. No intro, no extra text."""

PICK_ANGLE = """Topic: {topic}
Platform: {platform}
Here are 5 content angles:
{angles}
Pick the single best angle for engagement. Reply ONLY in this format:
NUMBER: <1-5>
AUDIENCE: <one short line describing the target audience>"""

CAPTION = """You are an expert social media copywriter.
Topic: {topic}
Platform: {platform}
Tone: {tone}
Chosen content angle: {angle}
Target audience: {audience}
Platform rules: {rules}
{feedback}
Write the post. Reply EXACTLY in this format:
HOOK: <one strong opening line>
CAPTION: <the full post, starting with the hook>
Do not add hashtags in the caption. No extra commentary."""

HASHTAGS = """Generate relevant hashtags for a {platform} post.
Topic: {topic}
Caption: {caption}
Platform rules: {rules}
Reply with ONLY the hashtags separated by spaces (each starting with #). No explanation."""

REEL = """Write a 30-second video/reel script.
Topic: {topic}
Platform: {platform}
Tone: {tone}
Hook to start with: {hook}
Format (use exactly 4 scenes):
Scene 1 (Hook): Visual: ... | Voiceover: ...
Scene 2 (Explain): Visual: ... | Voiceover: ...
Scene 3 (Result): Visual: ... | Voiceover: ...
Scene 4 (Closing): Visual: ... | Voiceover: ...
Keep the total under 80 spoken words. No extra commentary."""

TITLE_THUMB = """Topic: {topic}
Platform: {platform}
Tone: {tone}
Reply EXACTLY in this format:
TITLE: <catchy title under 70 characters>
THUMBNAIL: <thumbnail text, max 5 words>"""

REVIEW = """You are a strict content reviewer for {platform}.
Tone requested: {tone}
Platform rules: {rules}
--- CONTENT ---
Hook: {hook}
Caption: {caption}
Hashtags: {hashtags}
---------------
Check: Is the hook strong? Is it clear? Is it too long? Is the tone suitable? Are the hashtags relevant? Is it ready for {platform}?
Reply EXACTLY in this format:
SCORE: <1-10>
VERDICT: <GOOD or IMPROVE>
COMMENTS: <max 3 short bullet-style suggestions>"""


# FIX:humor_weak
CAPTION += "\nIf the tone is funny, humorous or meme style: use a relatable developer joke with a clear punchline, short sentences and one playful emoji. Example: My model: 99% accuracy in the notebook. Production: exists."
REEL += "\nIf the tone is funny or meme style, make the final scene a punchline."


# FIX:reviewer_flag
TREND_IDEAS += "\nEach angle must include a specific detail, number or personal experience. Avoid generic advice."
