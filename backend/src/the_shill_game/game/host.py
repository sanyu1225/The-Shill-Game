from typing import List, Literal
import random

from the_shill_game.agent.character import CharacterVoteResponse
from the_shill_game.agent.memecoin_agent import MemecoinAgent
from the_shill_game.utils.model import invoke_structured_response


_background = "The Shill Game is a high-stakes reality show where memecoin founders fight to keep their project alive through persuasion, betrayal, and bold claims. Each round, one is voted out and banished—erasing their coin from existence forever."

_l_intro_openings = [
    "[Host] Welcome back to The Shill Game—the only place where rug pulls are part of the charm.",
    "[Host] Six meme coins walk in. One moonshot, five disasters waiting to happen. Let's light this dumpster on fire.",
    "[Host] If you came for serious crypto talk...you're in the wrong hellscape. It's The Shill Game, baby!",
    "[Host] Hope your vaporware is polished, because it's about to get roasty in here.",
    "[Host] The stakes are fake, the drama is real. Welcome to The Shill Game.",
]


_l_intro_intros = [
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

_l_intro_transition = [
    "[Host] Alright. You've heard them all.",
    "[Host] That's the end of the pitches.",
    "[Host] Time to judge the chaos.",
    "[Host] Hope you were paying attention.",
    "[Host] Let's settle this.",
    "[Host] The stage is clear.",
    "[Host] Memes have been made. Decisions await.",
    "[Host] Let the judgment begin.",
]


_l_voting_intro = [
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

_l_final_vote_tie = [
    "[Host] We've got a tie—{names} are dead even. Looks like fate's playing games.",
    "[Host] It's a tie! {names} couldn't convince or outlast each other.",
    "[Host] Unbelievable—we have a tie. {names} are locked in a memecoin stalemate.",
    "[Host] And just when we thought one of them would fall… it's a tie. {names} are hanging on by a thread.",
    "[Host] It's official—{names} are equally unconvincing. We've got ourselves a deadlock.",
    "[Host] Wow. Even after all that? It's a tie between {names}. What now?",
    "[Host] Of course it's a tie. {names} couldn't even win *losing* properly.",
    "[Host] A perfect tie. {names} are battling it out for last place glory.",
    "[Host] We've hit a stalemate. {names} will now have to beg the blockchain gods for mercy.",
    "[Host] Looks like we're stuck—{names} are equally doomed. It's a tie.",
]

_l_final_vote_elimination = [
    "[Host] Eliminated. {eliminated_agent} is out.",
    "[Host] And just like that… {eliminated_agent} is gone.",
    "[Host] Game over for {eliminated_agent}.",
    "[Host] That's the end of the line for {eliminated_agent}.",
    "[Host] No more shills. {eliminated_agent} has been dropped.",
    "[Host] The vote is in. {eliminated_agent} didn't make it.",
    "[Host] Delisted. {eliminated_agent} won't be coming back.",
    "[Host] The people have spoken. Bye, {eliminated_agent}.",
    "[Host] Another one bites the dust. Farewell, {eliminated_agent}.",
    "[Host] {eliminated_agent} has been voted off the chain.",
    "[Host] Say goodbye to {eliminated_agent} and their meme coin.",
    "[Host] That's it for {eliminated_agent}. Gone without a moon.",
    "[Host] Sorry, {eliminated_agent}. You've been outshilled.",
    "[Host] {eliminated_agent} just got rugged. Brutally.",
    "[Host] {eliminated_agent} is toast. That's crypto, baby.",
]

_l_end_game_single_winner = [
    "[Host] Congratulations, {name}! You've won The Shill Game!",
    "[Host] And there it is—{name} takes the crown in The Shill Game!",
    "[Host] {name}, against all logic and odds… you've won The Shill Game!",
    "[Host] {name}, you survived the shills, the drama, and the cringe. You win!",
    "[Host] {name}, your fake roadmap actually worked. You win The Shill Game!",
    "[Host] After all the chaos, {name} is the last meme standing.",
    "[Host] The final rug has been dodged. {name} is the winner!",
    "[Host] That's it. {name} outlasted the chaos and takes the win.",
    "[Host] {name}, your coin lives another day. You win.",
    "[Host] All roads led here, and {name} came out on top.",
    "[Host] {name}, this one's for the memecoin history books. You did it.",
    "[Host] {name} wins. Make sure to sell before the chart goes red.",
    "[Host] {name}, you shilled just hard enough to survive. Victory is yours.",
]

_l_end_game_multiple_winners = [
    "[Host] We've got two survivors! {name1} and {name2}, you both win The Shill Game!",
    "[Host] Against all odds, it's a tie at the top. {name1} and {name2}, you shilled your way to victory.",
    "[Host] Turns out, the market couldn't choose just one. {name1} and {name2}, you're both memecoin royalty.",
    "[Host] What a twist—{name1} and {name2} are co-champions of The Shill Game!",
    "[Host] It's official. {name1} and {name2} outlasted them all. Dual winners!",
    "[Host] The final rug was never pulled. {name1} and {name2} walk away with the crown.",
    "[Host] For once, the chain is merciful. {name1} and {name2}, you're both still standing.",
    "[Host] Shill meets shill. {name1} and {name2} survive as the last two standing.",
    "[Host] The game ends not with one, but two. Congrats, {name1} and {name2}.",
    "[Host] {name1} and {name2}, you've both earned your spot in memecoin infamy.",
    "[Host] A perfect split. {name1} and {name2} are both declared winners of this glorious disaster.",
    "[Host] The shill gods smile on you both. {name1}, {name2}—congratulations.",
    "[Host] Somehow, two coins remain. {name1} and {name2}, you are the last shills standing.",
]

_l_end_game_closing = [
    "[Host] And that's how legends—or at least memes—are made. See you next cycle.",
    "[Host] One survived, many were rugged, but only The Shill Game remembers.",
    "[Host] Thanks for watching. Please don't invest based on anything you just saw.",
    "[Host] The markets move on, but the cringe lives forever. Until next time.",
    "[Host] That's it for The Shill Game. May your bags be lighter, and your rugs be softer.",
    "[Host] Join us next time—same scam hour, same scam channel.",
    "[Host] The end. No refunds.",
    "[Host] This episode was proudly powered by copium. Goodnight.",
    "[Host] That's all for this round of chaos. Stay delusional.",
    "[Host] We'll see you next season—unless we get rugged first.",
]


class HostLineManager:
    def __init__(self, lines: List[str]):
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


intro_intro_manager = HostLineManager(_l_intro_intros)


def get_background():
    return _background


def get_host_intro_message(
    phase: Literal["opening", "intro", "transition"],
    current_speaker: str = "",
    is_first_intro: bool = False,
) -> str:
    if phase == "opening":
        return random.choice(_l_intro_openings)
    elif phase == "intro":
        if not current_speaker:
            raise ValueError("current_speaker_name is required for intro phase")
        if is_first_intro:
            line = intro_intro_manager.next_line(restrict_to_first_n=15)
        else:
            line = intro_intro_manager.next_line()
        return line.format(name=current_speaker)
    elif phase == "transition":
        return random.choice(_l_intro_transition)


def get_host_voting_message(
    phase: Literal["intro", "cue", "announce_result", "final_vote", "tie_breaker"],
    current_speaker: str = "",
    most_voted_agents: List[str] = [],
) -> str:
    if phase == "intro":
        return random.choice(_l_voting_intro)
    elif phase == "cue":
        return f"[Host] {current_speaker}, please cast your vote."
    elif phase == "announce_result":
        if len(most_voted_agents) == 1:
            return f"[Host] {most_voted_agents[0]} has received the most votes and will now enter the defense phase!"
        else:
            return f"[Host] {', '.join(most_voted_agents)} are tied for the most votes and will now enter the defense phase!"
    elif phase == "final_vote":
        return "[Host] You've heard the defense. Now it's time—cast your final vote to eliminate one player."
    elif phase == "tie_breaker":
        return "[Host] It's a tie! Let's do it again."


def get_host_defense_message(current_speaker: str) -> str:
    return f"[Host] {current_speaker}, you received the most votes. You now have a chance to defend your memecoin."


def get_host_final_vote_message(
    phase: Literal["tie", "elimination", "farewell"],
    most_voted_agents: List[str] = [],
    eliminated_agent: str = "",
) -> str:
    if phase == "tie":
        return random.choice(_l_final_vote_tie).format(
            names=", ".join(most_voted_agents)
        )
    elif phase == "elimination":
        return random.choice(_l_final_vote_elimination).format(
            eliminated_agent=eliminated_agent
        )
    elif phase == "farewell":
        return f"[Host] {eliminated_agent}, do you have any final words?"


def get_host_end_game_message(
    phase: Literal["announce_winner", "closing"],
    winners: List[str] = [],
) -> str:
    if phase == "announce_winner":
        if len(winners) == 1:
            return random.choice(_l_end_game_single_winner).format(name=winners[0])
        else:
            return random.choice(_l_end_game_multiple_winners).format(
                name1=winners[0], name2=winners[1]
            )
    elif phase == "closing":
        return random.choice(_l_end_game_closing)


def eliminate_agent(agents: List[MemecoinAgent]) -> CharacterVoteResponse:
    """TODO: This is only for demo purpose"""

    input = "\n---\n".join(
        [
            f"{i+1}. {a.character.name} is the founder of a memecoin called {a.character.memecoin.name}({a.character.memecoin.symbol}). The story of the memecoin is: {a.character.memecoin.backstory}"
            for i, a in enumerate(agents)
        ]
    )

    response = invoke_structured_response(
        instruction="You are the host of a game show. You are given a list of agents. You need to eliminate one of them.",
        input=input,
        response_format=CharacterVoteResponse,
    )
    return response
