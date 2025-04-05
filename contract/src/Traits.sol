// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

library Traits {
    struct TraitSet {
        bytes32 sociability;
        bytes32 thinking;
        bytes32 cooperation;
        bytes32 riskTaking;
        bytes32 exploration;
        bytes32 trust;
        bytes32 morality;
        bytes32 adaptability;
        bytes32 initiative;
        bytes32 emotionalControl;
        bytes32 foresight;
        bytes32 actionStyle;
        bytes32 knowledgeSeeking;
    }

    // Store all options in a single array to reduce memory usage
    function getAllOptions() internal pure returns (bytes32[39] memory) {
        return [
            // Sociability
            bytes32("Introverted"),
            bytes32("Balanced"),
            bytes32("Extroverted"),
            // Thinking
            bytes32("Emotional"),
            bytes32("Balanced"),
            bytes32("Logical"),
            // Cooperation
            bytes32("Competitive"),
            bytes32("Flexible"),
            bytes32("Cooperative"),
            // Risk Taking
            bytes32("Cautious"),
            bytes32("Balanced"),
            bytes32("Impulsive"),
            // Exploration
            bytes32("Conservative"),
            bytes32("Open-Minded"),
            bytes32("Curious"),
            // Trust
            bytes32("Skeptical"),
            bytes32("Cautiously Trusting"),
            bytes32("Trusting"),
            // Morality
            bytes32("Pragmatic"),
            bytes32("Fair-Minded"),
            bytes32("Highly Principled"),
            // Adaptability
            bytes32("Resistant"),
            bytes32("Moderate"),
            bytes32("Highly Adaptive"),
            // Initiative
            bytes32("Follower"),
            bytes32("Situational Leader"),
            bytes32("Natural Leader"),
            // Emotional Control
            bytes32("Hot-Tempered"),
            bytes32("Stable"),
            bytes32("Calm & Collected"),
            // Foresight
            bytes32("Short-Term Thinker"),
            bytes32("Balanced"),
            bytes32("Visionary"),
            // Action Style
            bytes32("Traditionalist"),
            bytes32("Open to Innovation"),
            bytes32("Innovator"),
            // Knowledge Seeking
            bytes32("Practical Learner"),
            bytes32("Curious Learner"),
            bytes32("Knowledge-Seeker")
        ];
    }

    function generateRandomTraits(uint256 seed) internal pure returns (TraitSet memory traits) {
        bytes32[39] memory options = getAllOptions();
        uint256 offset = 0;

        traits.sociability = options[(seed + 1) % 3 + offset];
        offset += 3;
        traits.thinking = options[(seed + 2) % 3 + offset];
        offset += 3;
        traits.cooperation = options[(seed + 3) % 3 + offset];
        offset += 3;
        traits.riskTaking = options[(seed + 4) % 3 + offset];
        offset += 3;
        traits.exploration = options[(seed + 5) % 3 + offset];
        offset += 3;
        traits.trust = options[(seed + 6) % 3 + offset];
        offset += 3;
        traits.morality = options[(seed + 7) % 3 + offset];
        offset += 3;
        traits.adaptability = options[(seed + 8) % 3 + offset];
        offset += 3;
        traits.initiative = options[(seed + 9) % 3 + offset];
        offset += 3;
        traits.emotionalControl = options[(seed + 10) % 3 + offset];
        offset += 3;
        traits.foresight = options[(seed + 11) % 3 + offset];
        offset += 3;
        traits.actionStyle = options[(seed + 12) % 3 + offset];
        offset += 3;
        traits.knowledgeSeeking = options[(seed + 13) % 3 + offset];
    }
}
