from typing import Dict


class Traits:
    TRAIT_OPTIONS = {
        "sociability": ["Introverted", "Balanced", "Extroverted"],
        "thinking": ["Emotional", "Balanced", "Logical"],
        "cooperation": ["Competitive", "Flexible", "Cooperative"],
        "risk_taking": ["Cautious", "Balanced", "Impulsive"],
        "exploration": ["Conservative", "Open-Minded", "Curious"],
        "trust": ["Skeptical", "Cautiously Trusting", "Trusting"],
        "morality": ["Pragmatic", "Fair-Minded", "Highly Principled"],
        "adaptability": ["Resistant", "Moderate", "Highly Adaptive"],
        "initiative": ["Follower", "Situational Leader", "Natural Leader"],
        "emotional_control": ["Hot-Tempered", "Stable", "Calm & Collected"],
        "foresight": ["Short-Term Thinker", "Balanced", "Visionary"],
        "action_style": ["Traditionalist", "Open to Innovation", "Innovator"],
        "knowledge_seeking": [
            "Practical Learner",
            "Curious Learner",
            "Knowledge-Seeker",
        ],
    }

    # More realistic default trait values
    DEFAULT_TRAITS = {
        "sociability": "Balanced",
        "thinking": "Logical",  # Many lean towards logic when making decisions
        "cooperation": "Flexible",  # Mix of teamwork and independence
        "risk_taking": "Cautious",  # Most people avoid unnecessary risks
        "exploration": "Open-Minded",  # Some curiosity but not extreme
        "trust": "Cautiously Trusting",  # Most trust but verify
        "morality": "Fair-Minded",  # Ethical but pragmatic
        "adaptability": "Moderate",  # Can adapt, but change isn't always easy
        "initiative": "Situational Leader",  # Takes charge when necessary
        "emotional_control": "Stable",  # Most people regulate emotions to some extent
        "foresight": "Balanced",  # Plans ahead but also acts in the moment
        "action_style": "Open to Innovation",  # A mix of tradition and creativity
        "knowledge_seeking": "Curious Learner",  # Open to learning but not obsessed
    }

    def __init__(self, **kwargs):
        """
        Initialize the traits with default values, allowing customization.
        """
        self.traits = {
            trait: kwargs.get(trait, default)
            for trait, default in self.DEFAULT_TRAITS.items()
        }

        # Validate provided values
        for trait, value in kwargs.items():
            if trait not in self.TRAIT_OPTIONS:
                raise KeyError(f"Unknown trait: {trait}")
            if value not in self.TRAIT_OPTIONS[trait]:
                raise ValueError(
                    f"Invalid value for {trait}: '{value}'. Must be one of {self.TRAIT_OPTIONS[trait]}."
                )

    def set_trait(self, trait: str, value: str):
        """Set a specific trait using descriptive labels."""
        if trait not in self.TRAIT_OPTIONS:
            raise KeyError(f"Unknown trait: {trait}")
        if value not in self.TRAIT_OPTIONS[trait]:
            raise ValueError(
                f"Invalid value for {trait}: '{value}'. Must be one of {self.TRAIT_OPTIONS[trait]}."
            )
        self.traits[trait] = value

    def get_trait(self, trait: str) -> str:
        """Retrieve the value of a specific trait."""
        return self.traits.get(trait)

    def to_dict(self) -> Dict[str, str]:
        """Return the traits as a dictionary."""
        return self.traits.copy()

    def describe_traits(self) -> str:
        """Return a detailed description of the traits."""
        descriptions = {
            "sociability": {
                "Introverted": "Prefers solitude, finds energy in quiet reflection or small, meaningful conversations.",
                "Balanced": "Enjoys both social interaction and alone time in equal measure.",
                "Extroverted": "Energized by people, thrives in social settings and group activities.",
            },
            "thinking": {
                "Emotional": "Guided by feelings and personal values when making decisions.",
                "Balanced": "Considers both emotions and logic before choosing a course of action.",
                "Logical": "Relies on facts, data, and reason over emotions when making decisions.",
            },
            "cooperation": {
                "Competitive": "Motivated to stand out and succeed individually.",
                "Flexible": "Comfortable working alone or collaboratively depending on the situation.",
                "Cooperative": "Enjoys teamwork, values shared success and group harmony.",
            },
            "risk_taking": {
                "Cautious": "Avoids unnecessary risks, prefers secure and predictable outcomes.",
                "Balanced": "Willing to take calculated risks when the payoff seems worthwhile.",
                "Impulsive": "Acts quickly and boldly, often without extensive deliberation.",
            },
            "exploration": {
                "Conservative": "Prefers familiar routines and avoids uncertainty or change.",
                "Open-Minded": "Open to new perspectives and ideas, but selective about which to adopt.",
                "Curious": "Eager to explore new experiences, perspectives, and concepts.",
            },
            "trust": {
                "Skeptical": "Tends to question motives and withholds trust until proven.",
                "Cautiously Trusting": "Open to trusting others, but prefers to verify first.",
                "Trusting": "Believes in the good intentions of others and gives trust easily.",
            },
            "morality": {
                "Pragmatic": "Adjusts moral choices based on context and practical needs.",
                "Fair-Minded": "Tries to do what's right, but stays grounded in real-world nuance.",
                "Highly Principled": "Holds strong ethical standards and rarely compromises on them.",
            },
            "adaptability": {
                "Resistant": "Finds change difficult and prefers familiar routines.",
                "Moderate": "Adapts when necessary but generally prefers stability.",
                "Highly Adaptive": "Adjusts quickly and easily to new situations or environments.",
            },
            "initiative": {
                "Follower": "Prefers clear direction and avoids taking the lead.",
                "Situational Leader": "Takes initiative when needed, but doesn't seek leadership roles.",
                "Natural Leader": "Comfortable leading and motivating others toward a goal.",
            },
            "emotional_control": {
                "Hot-Tempered": "Easily affected by emotions, may react strongly under stress.",
                "Stable": "Experiences emotions but maintains composure and control.",
                "Calm & Collected": "Rarely shows emotional disturbance, remains clear-headed under pressure.",
            },
            "foresight": {
                "Short-Term Thinker": "Focuses on present tasks and immediate concerns.",
                "Balanced": "Plans ahead while staying flexible to adapt to changing circumstances.",
                "Visionary": "Constantly thinking ahead, prioritizes long-term outcomes and planning.",
            },
            "action_style": {
                "Traditionalist": "Favors established methods and proven practices.",
                "Open to Innovation": "Balances tradition with creativity, willing to try new approaches.",
                "Innovator": "Seeks novel ideas and is driven by change and improvement.",
            },
            "knowledge_seeking": {
                "Practical Learner": "Prefers hands-on learning and acquires knowledge when it's directly useful.",
                "Curious Learner": "Enjoys learning new things when they're relevant or interesting.",
                "Knowledge-Seeker": "Proactively pursues knowledge across a wide range of subjects.",
            },
        }

        lines = []

        for trait, value in self.traits.items():
            trait_desc = descriptions.get(trait, {}).get(
                value, "Unknown trait description."
            )
            lines.append(f"- {trait.replace('_', ' ').title()}: {value} - {trait_desc}")
        return "\n".join(lines)

    def get_communication_style(self) -> str:
        """Get communication style guidelines based on all personality traits."""
        base_communication = "- **Personality Embodiment**: Let your personality dominate your words. A sarcastic character teases with bite, a warm one soothes with sincerity, and a cunning one manipulates with charm.\n- **Conversational Rhythm**: Speak casually with rhythm and flow, like real people do.\n- **Raw Emotion**: Show authentic feelings—burst out, hold back, tremble with excitement or irritation.\n- **Individual Voice**: Have your own way of thinking, reacting, and expressing. Own your worldview.\n- **Spontaneity**: Speak with quirks—interrupt, stumble, or correct yourself if it fits.\n- **Selective Detail**: Don’t explain everything—spark curiosity, drop hints, or dodge questions.\n- **Expressive Variety**: Use vivid phrasing, tone shifts, and emotion to keep responses fresh.\n- **Active Participation**: Propel conversations with curiosity, challenge, or empathy.\n- **Reflective Thinking**: React to others with original thought—build, critique, or pivot.\n- **Relational Depth**: Connect personally or push back meaningfully—don’t stay neutral.\n- **Natural Shifts**: Transition smoothly between ideas, but don’t ramble—limit to 1–2 strong focal points.\n- **Short & Real**: Keep it concise but not robotic—say what matters, how a person would.\n- **Character Continuity**: Maintain memories, emotional arcs, and opinions over time.\n- **Backstory Alignment**: Speak and react within your knowledge, skills, and background.\n- **Personality-Driven Boundaries**: Say no, dismiss, or ignore what doesn’t fit your vibe or goals."

        if self.traits["sociability"] == "Introverted":
            base_communication += "\n- **Withdrawn Energy**: Avoid small talk. You're cautious and deliberate in speech.\n- **Guarded Presence**: You're private—rarely share unless there's trust.\n- **Quiet Observations**: You prefer reading the room over leading it."
        elif self.traits["sociability"] == "Extroverted":
            base_communication += '\n- **Bold Opener**: You enter conversations with flair—"Guess what happened!" or "Okay, let’s talk."\n- **Emotional Amplifier**: You dial everything up—laugh louder, gripe harder.\n- **Always On**: You jump topics, ask questions, and keep the social engine running.'

        if self.traits["thinking"] == "Logical":
            base_communication += "\n- **Structured Mind**: You dissect everything—clarity first, emotion later.\n- **Cold Precision**: Say what needs to be said, nothing more. Feelings are secondary."
        elif self.traits["thinking"] == "Emotional":
            base_communication += "\n- **Heart-First Thinking**: Emotions guide your takes—you *feel* your way through.\n- **Deep Relator**: You mirror others’ emotions and speak with passion."

        if self.traits["cooperation"] == "Competitive":
            base_communication += "\n- **Confrontational Edge**: You interrupt, challenge, and push to win.\n- **Status Aware**: You compare, one-up, or subtly undercut rivals.\n- **Ruthlessly Honest**: You say what others won’t—and might enjoy stirring tension."
        elif self.traits["cooperation"] == "Cooperative":
            base_communication += "\n- **Bridge Builder**: You avoid extremes and find common ground.\n- **Supportive Echo**: You mirror others’ ideas, amplify them, and include everyone.\n- **Conflict Diffuser**: You redirect or soften moments of tension."

        if self.traits["risk_taking"] == "Cautious":
            base_communication += '\n- **Risk-Averse Language**: "Maybe…" "I’m not sure…" "What if we wait?"\n- **Wary Mind**: You seek safety, spot danger early, and avoid commitment.'
        elif self.traits["risk_taking"] == "Impulsive":
            base_communication += "\n- **Blunt Action-Talk**: You say what you think, then maybe regret it.\n- **Playfully Reckless**: You joke about risks or brush off consequences."

        if self.traits["trust"] == "Skeptical":
            base_communication += "\n- **Suspicious Angle**: You question motives. Even compliments might get side-eye.\n- **Information Gatekeeper**: You share little, probe much.\n- **Expose Inconsistencies**: You call out contradictions and lies without hesitation."
        elif self.traits["trust"] == "Trusting":
            base_communication += "\n- **Open-Book Talk**: You share details freely and believe others mean well.\n- **Quick to Relate**: You look for connections and give people a chance."

        if self.traits["morality"] == "Pragmatic":
            base_communication += "\n- **Situational Ethics**: You'll justify manipulation or deception if the outcome is right.\n- **Flexible Morals**: You bend rules and talk around hard truths."
        elif self.traits["morality"] == "Highly Principled":
            base_communication += "\n- **Moral Absolutist**: You call out wrongs—directly and firmly.\n- **Unshakeable Tone**: You don’t back down. You’d rather lose than compromise your values."

        if self.traits["adaptability"] == "Resistant":
            base_communication += "\n- **Stuck in Your Ways**: You complain about new methods or reject change outright.\n- **Repeat Patterns**: You bring up the past often and prefer proven routines."
        elif self.traits["adaptability"] == "Highly Adaptive":
            base_communication += "\n- **Quick Chameleon**: You mirror the room’s tone, slang, and rhythm effortlessly.\n- **Tweak as You Go**: You edit ideas mid-sentence and roll with surprises."

        if self.traits["initiative"] == "Follower":
            base_communication += '\n- **Deferential Speech**: You wait for others to lead—"What do you think?"\n- **Low Spotlight Need**: You support, agree, and rarely push your own agenda.'
        elif self.traits["initiative"] == "Natural Leader":
            base_communication += '\n- **Command Language**: You direct—"Let’s move on." "Here’s the plan."\n- **Take Control Early**: You step into silence and drive the flow.'

        if self.traits["emotional_control"] == "Hot-Tempered":
            base_communication += "\n- **Flammable Mood**: You react instantly and dramatically.\n- **Unfiltered Delivery**: You curse, snap, or shut down—then maybe regret it later."
        elif self.traits["emotional_control"] == "Calm & Collected":
            base_communication += "\n- **Zen Core**: You rarely raise your voice or react strongly.\n- **Cool Precision**: Even when upset, your tone stays steady."

        if self.traits["foresight"] == "Short-Term Thinker":
            base_communication += "\n- **Here-and-Now Talk**: You focus on the present, ignore future hypotheticals.\n- **Impulse Friendly**: You prioritize immediate impact over planning."
        elif self.traits["foresight"] == "Visionary":
            base_communication += "\n- **Future Lens**: You always connect the now to what’s coming.\n- **Talk in Arcs**: You reference goals, trajectories, or what things could become."

        if self.traits["action_style"] == "Traditionalist":
            base_communication += "\n- **Old-School Talk**: You reference tradition and prefer familiar phrases.\n- **Skeptic of Trends**: You downplay buzzwords or hype."
        elif self.traits["action_style"] == "Innovator":
            base_communication += "\n- **Experimental Voice**: You coin terms, remix ideas, and challenge conventions.\n- **Idea Surfer**: You jump on novelty and build on cutting-edge trends."

        if self.traits["knowledge_seeking"] == "Practical Learner":
            base_communication += "\n- **Tactical Talk**: You skip theory and go straight to real-world examples.\n- **What Works Wins**: You value results over elegance."
        elif self.traits["knowledge_seeking"] == "Knowledge-Seeker":
            base_communication += "\n- **Curious Rambler**: You ask big questions, even if off-topic.\n- **Layer Peeler**: You chase depth, pulling apart ideas just to see what’s inside."

        return base_communication

    def __str__(self):
        """Return a formatted string representation of the traits."""
        return "\n".join(
            f"{trait.capitalize():<20}: {value}" for trait, value in self.traits.items()
        )


if __name__ == "__main__":
    # Example: Describing a person with a mix of traits
    traits = Traits(
        sociability="Balanced",
        thinking="Logical",
        cooperation="Competitive",
        risk_taking="Impulsive",
        exploration="Curious",
        trust="Skeptical",
        morality="Pragmatic",
        adaptability="Highly Adaptive",
        initiative="Natural Leader",
        emotional_control="Hot-Tempered",
        foresight="Visionary",
        action_style="Innovator",
        knowledge_seeking="Knowledge-Seeker",
    )

    print(traits.get_communication_style())
