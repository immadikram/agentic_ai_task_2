"""CLI demo.  Run:  python demo.py"""
from app.agent import TrendPilotAgent

PLATFORMS = ["LinkedIn", "Instagram", "YouTube Shorts", "TikTok", "X/Twitter", "Facebook"]
TONES = ["Professional and exciting", "Motivational", "Funny", "Short and catchy", "Meme style", "Inspirational"]
OUTPUTS = ["Post", "Reel Script", "Post + Reel Script", "Full plan"]


def choose(label, options):
    print(f"\n{label}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        c = input("Choose number: ").strip()
        if c.isdigit() and 1 <= int(c) <= len(options):
            return options[int(c) - 1]


def show(r):
    print("\n" + "=" * 60)
    print(f"Topic: {r['topic']}\nPlatform: {r['platform']}\nTone: {r['tone']}")
    print(f"\nTitle: {r.get('title')}\nThumbnail Text: {r.get('thumbnail')}")
    print(f"\nContent Idea:\n{r['content_idea']}\n\nHook:\n{r['hook']}")
    if r.get("caption"):
        print(f"\nCaption:\n{r['caption']}")
    if r.get("hashtags"):
        print(f"\nHashtags:\n{' '.join(r['hashtags'])}")
    if r.get("reel_script"):
        print(f"\nReel Script:\n{r['reel_script']}")
    print(f"\nReview ({r['review']['score']}/10, {r['review']['verdict']}):\n{r['review']['comments']}")
    print(f"\nSaved File: {r['saved_file']}")
    print("=" * 60)


if __name__ == "__main__":
    print("TrendPilot - Local Agentic AI (Ollama)")
    while True:
        topic = input("\nEnter your topic (or 'q' to quit): ").strip()
        if topic.lower() == "q":
            break
        if not topic:
            continue
        platform = choose("Choose platform:", PLATFORMS)
        tone = choose("Choose tone:", TONES)
        out = choose("Choose output type:", OUTPUTS)
        try:
            show(TrendPilotAgent().run(topic, platform, tone, out))
        except RuntimeError as e:
            print(f"ERROR: {e}")
