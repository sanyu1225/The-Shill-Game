from typing import Literal
import random


background = "The Shill Game is a high-stakes reality show where memecoin founders fight to keep their project alive through persuasion, betrayal, and bold claims. Each round, one is voted out and banished—erasing their coin from existence forever."

l_intro_openings = [
    "[Host] Welcome back to The Shill Game—the only place where rug pulls are part of the charm.",
    "[Host] Six meme coins walk in. One moonshot, five disasters waiting to happen. Let's light this dumpster on fire.",
    "[Host] If you came for serious crypto talk...you're in the wrong hellscape. It's The Shill Game, baby!",
    "[Host] Hope your vaporware is polished, because it's about to get roasty in here.",
    "[Host] The stakes are fake, the drama is real. Welcome to The Shill Game.",
]


l_intro_intros = [
    "[Host] {name}, the mic's yours. Tell us about your coin—and is it just another JPEG-fueled fever dream?",
    "[Host] {name}. Convince us this isn't just another Discord pump-and-dump in disguise.",
    "[Host] {name}, you've got 15 seconds. Make us believe in your bag. Go.",
    "[Host] {name}, step up and pitch your coin like your exit scam depends on it.",
    "[Host] {name}, impress us—or we toss your project into the blockchain abyss. What are you shilling?",
    "[Host] {name}, you're up. Tell us your grand vision—or just admit it's a coin named after your dog.",
    "[Host] {name}, is this innovation… or just desperation with a whitepaper? Let's hear your pitch.",
    "[Host] {name}, go ahead. Tell us why your meme coin won't end up in the same graveyard as Floki 2.0.",
    "[Host] Ok! {name}, it's your turn. What's the story behind your coin—and why should we care?",
    "[Host] {name}, here's your shot. Moon us—or move aside. Tell us what you're building.",
    "[Host] {name}, you're on. Give us something better than AI-generated hype and a Telegram group with 12 bots.",
    "[Host] {name}, tell us—are we looking at a revolution, or just another liquidity trap with better branding?",
    "[Host] Alright {name}, time to introduce your coin—and please tell me the logo wasn't made on Canva at 3AM.",
    "[Host] {name}, let's hear your pitch. Bonus points if you don't say 'decentralized' five times.",
    "[Host] {name}, the floor is yours. Try not to shill us straight into a coma. What's the coin?",
    "[Host] Cool story. Now {name}, introduce your memecoin and prove it's not just fiction.",
    "[Host] Wow. Inspiring. {name}, you're up. Tell us what your coin's about.",
    "[Host] Nice pitch—if this were 2021. {name}, let's hear yours.",
    "[Host] Uh-huh. Anyway. {name}, your turn. Sell us your dream project.",
    "[Host] Incredible delusion. {name}, can you out-shill that? Introduce your coin.",
    "[Host] I think my wallet just unfollowed that one. {name}, time to redeem the moment. What's your coin?",
    "[Host] Ok... that happened. {name}, your turn. What miracle are *you* selling?",
    "[Host] Well, that was a pitch. {name}, let's see what you're bringing to the table.",
    "[Host] That definitely was... words. {name}, save this segment. Tell us about your coin.",
    "[Host] Love the confidence. Not sure about the product. {name}, let's hear what you've got.",
    "[Host] Mmm, bold claims. {name}, can you bring actual facts? Tell us what you're building.",
    "[Host] A roadmap and a prayer. {name}, your turn. What makes your coin real?",
    "[Host] Alright, that was pure hopium. {name}, you're up. Bring us something spicy.",
    "[Host] Sweet. Another whitepaper I'll never read. {name}, impress us with actual substance. What's your pitch?",
    "[Host] Cool. My grandma almost bought it. {name}, your turn to pitch.",
]

l_intro_transition = [
    "[Host] Alright. You've heard them all.",
    "[Host] That's the end of the pitches.",
    "[Host] Time to judge the chaos.",
    "[Host] Hope you were paying attention.",
    "[Host] Let's settle this.",
    "[Host] The stage is clear.",
    "[Host] Memes have been made. Decisions await.",
    "[Host] Let the judgment begin.",
]


l_voting_intro = [
    "[Host] It's time to vote. Choose the founder whose pitch held the least water.",
    "[Host] Place your vote. Which one's getting delisted by popular demand?",
    "[Host] Cast your vote. One of these coins is circling the drain.",
    "[Host] Hit 'em where it hurts. Vote for the weakest shill.",
    "[Host] Decide who takes the express lane to irrelevance.",
    "[Host] Choose the one you trust least with a wallet and a dream.",
    "[Host] Make it count. One founder's about to vanish from the blockchain.",
    "[Host] Tap into your inner cynic. Pick the pitch that insulted your intelligence.",
    "[Host] Rug one. Vote now.",
    "[Host] Who's getting banished? You decide.",
]


class HostLineManager:
    def __init__(self, lines: list[str]):
        self.original_lines = lines
        self.remaining_lines = []

    def next_line(self, restrict_to_first_n: int | None = None) -> str:
        if restrict_to_first_n is not None:
            pool = self.original_lines[:restrict_to_first_n]
            return random.choice(pool)

        if not self.remaining_lines:
            self.remaining_lines = self.original_lines.copy()
            random.shuffle(self.remaining_lines)
        return self.remaining_lines.pop()


intro_intro_manager = HostLineManager(l_intro_intros)


def get_background():
    return background


def get_host_intro_message(
    phase: Literal["opening", "intro", "transition"],
    current_speaker: str = "",
    is_first_intro: bool = False,
) -> str:
    if phase == "opening":
        return random.choice(l_intro_openings)
    elif phase == "intro":
        if not current_speaker:
            raise ValueError("current_speaker_name is required for intro phase")
        if is_first_intro:
            line = intro_intro_manager.next_line(restrict_to_first_n=15)
        else:
            line = intro_intro_manager.next_line()
        return line.format(name=current_speaker)
    elif phase == "transition":
        return random.choice(l_intro_transition)


def get_host_voting_message(
    phase: Literal["intro", "cue", "announce_result", "tie_breaker"],
    current_speaker: str = "",
    most_voted_agents: list[str] = [],
) -> str:
    if phase == "intro":
        return random.choice(l_voting_intro)
    elif phase == "cue":
        return f"[Host] {current_speaker}, please cast your vote."
    elif phase == "announce_result":
        if len(most_voted_agents) == 1:
            return f"[Host] {most_voted_agents[0]} has received the most votes and will now enter the defense phase!"
        else:
            return f"[Host] {', '.join(most_voted_agents)} are tied for the most votes and will now enter the defense phase!"
    elif phase == "tie_breaker":
        return "[Host] It's a tie! Let's do it again."
