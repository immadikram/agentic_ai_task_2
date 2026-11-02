"""TrendPilot agent: plan -> tool use -> review -> improve -> save."""
from . import tools as T


class TrendPilotAgent:
    def __init__(self, logger=print):
        self.log = logger
        self.tools_used = []

    def _call(self, name, *args, **kwargs):
        self.log(f"[Tool Called]: {name}")
        self.tools_used.append(name)
        return T.TOOLS[name](*args, **kwargs)

    def make_plan(self, topic, platform, tone, output_type) -> list:
        ot = output_type.lower()
        wants_reel = any(w in ot for w in ("reel", "script", "video", "full"))
        wants_post = any(w in ot for w in ("post", "caption", "full")) or not wants_reel
        plan = ["Understand the topic, platform and tone", "Generate content angles",
                "Select the best angle and target audience"]
        if wants_post:
            plan += ["Write the post caption", "Generate hashtags"]
        if wants_reel:
            plan.append("Generate a 30-second reel script")
        plan += ["Generate title and thumbnail text", "Review the output",
                 "Improve the caption using review feedback (if needed)", "Save result and update memory"]
        self.plan_flags = (wants_post, wants_reel)
        return plan

    def run(self, topic, platform="LinkedIn", tone="Professional and exciting", output_type="Post + Reel Script") -> dict:
        self.tools_used = []
        plan = self.make_plan(topic, platform, tone, output_type)
        wants_post, wants_reel = self.plan_flags
        self.log("[Agent Plan]")
        for i, s in enumerate(plan, 1):
            self.log(f"  {i}. {s}")

        angles = self._call("Trend Idea Generator", topic, platform, tone)
        pick = T.select_best_angle(topic, platform, angles)  # reasoning step (LLM decision)
        result = {"topic": topic, "platform": platform, "tone": tone, "output_type": output_type,
                  "all_angles": angles, "content_idea": pick["angle"], "audience": pick["audience"],
                  "plan": plan}

        # Caption is always generated: it provides the hook (the reel script reuses the same hook)
        cw = self._call("Caption Writer", topic, platform, tone, pick["angle"], pick["audience"])
        result["hook"] = cw["hook"]
        if wants_post:
            result["caption"] = cw["caption"]
            result["hashtags"] = self._call("Hashtag Generator", topic, platform, cw["caption"])
        else:
            result["caption"], result["hashtags"] = "", []
        if wants_reel:
            result["reel_script"] = self._call("Reel Script Generator", topic, platform, tone, cw["hook"])
        result.update(self._call("Title & Thumbnail Generator", topic, platform, tone))

        review = self._call("Content Reviewer", platform, tone, cw["hook"], cw["caption"] or cw["hook"], result["hashtags"])
        result["review"] = review
        # Self-improvement loop: one rewrite if reviewer says IMPROVE (or score < 7)
        if wants_post and (review["verdict"] == "IMPROVE" or (review["score"] or 10) < 7):
            self.log("[Agent]: Reviewer asked for improvements -> rewriting caption")
            better = self._call("Caption Writer", topic, platform, tone, pick["angle"], pick["audience"],
                                feedback=review["comments"])
            result["caption_v1"], result["caption"], result["hook"] = result["caption"], better["caption"], better["hook"]
            result["improved"] = True
        else:
            result["improved"] = False

        result["saved_file"] = self._call("File Saver", result, "md")
        self._call("Memory Tool", result)
        result["tools_used"] = list(self.tools_used)
        return result
