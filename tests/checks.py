"""Automatic quality checks on a generated result (used for 'Useful?' column + error analysis)."""
import re

HASHTAG_LIMIT = {"x/twitter": 3, "twitter": 3, "linkedin": 6, "instagram": 10}


def wants(output_type):
    ot = output_type.lower()
    reel = any(w in ot for w in ("reel", "script", "video", "full"))
    post = any(w in ot for w in ("post", "caption", "full")) or not reel
    return post, reel


def spoken_words(script):
    vo = re.findall(r"Voiceover:\s*(.*)", script, re.I)
    text = " ".join(vo) if vo else script
    return len(text.split())


def check(r):
    """Return a list of (issue_type, human-readable detail)."""
    issues = []
    if r.get("error"):
        return [("error", f"Run failed: {r['error']}")]
    post, reel = wants(r["output_type"])
    plat = r["platform"].lower()
    score = (r.get("review") or {}).get("score")
    if not r.get("hook") or (post and not r.get("caption")) or (reel and not r.get("reel_script")):
        issues.append(("missing", "A required section (hook / caption / reel script) came out empty"))
    if plat in ("x/twitter", "twitter") and post and len(r.get("caption", "")) > 270:
        issues.append(("x_length", f"Caption is {len(r['caption'])} characters; X/Twitter limit is 270"))
    if reel and r.get("reel_script") and spoken_words(r["reel_script"]) > 80:
        issues.append(("reel_long", f"Reel voiceover is {spoken_words(r['reel_script'])} words (too long for ~30 seconds)"))
    if post:
        n, lim = len(r.get("hashtags", [])), HASHTAG_LIMIT.get(plat, 5)
        if n == 0 or n > lim:
            issues.append(("hashtags", f"{n} hashtags generated; recommended maximum for {r['platform']} is {lim}"))
    if any(w in r["tone"].lower() for w in ("funny", "humor", "meme")) and (r.get("improved") or (score or 10) < 7):
        issues.append(("humor_weak", f"Humorous tone requested but reviewer scored it {score}/10 / asked for rewrite"))
    if r.get("improved") or (score is not None and score < 7):
        issues.append(("reviewer_flag", f"Reviewer flagged the first draft (score {score}/10): "
                                         f"{(r.get('review') or {}).get('comments', '')[:140]}"))
    return issues
