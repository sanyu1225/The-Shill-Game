// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import {Strings} from "openzeppelin-contracts/contracts/utils/Strings.sol";
import {Base64} from "openzeppelin-contracts/contracts/utils/Base64.sol";
import {ERC721} from "openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";
import {ERC721Enumerable} from "openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import {Ownable} from "openzeppelin-contracts/contracts/access/Ownable.sol";
import {Traits} from "./Traits.sol";

contract Character is ERC721, ERC721Enumerable, Ownable {
    struct GameHistoryEntry {
        string description;
        uint256 timestamp;
    }

    using Traits for *;

    uint256 public nextTokenId;
    mapping(uint256 => Traits.TraitSet) public tokenTraits;
    mapping(uint256 => GameHistoryEntry[]) public gameHistories;

    event GameHistoryAdded(uint256 indexed tokenId, string description, uint256 timestamp);

    constructor(address initialOwner) ERC721("Character", "CHAR") Ownable(initialOwner) {}

    function mint() public {
        uint256 tokenId = nextTokenId;
        _safeMint(msg.sender, tokenId);

        // Use Pseudo-random for demo
        uint256 seed =
            uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender, tokenId, blockhash(block.number - 1))));

        Traits.TraitSet memory traits = Traits.generateRandomTraits(seed);
        tokenTraits[tokenId] = traits;

        nextTokenId++;
    }

    function getTraits(uint256 tokenId) public view returns (Traits.TraitSet memory) {
        require(_ownerOf(tokenId) != address(0), "Character: token does not exist");
        return tokenTraits[tokenId];
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        Traits.TraitSet memory traits = tokenTraits[tokenId];

        string memory attributes = string.concat(
            '{"trait_type":"Sociability","value":"',
            _bytes32ToString(traits.sociability),
            '"},',
            '{"trait_type":"Thinking","value":"',
            _bytes32ToString(traits.thinking),
            '"},',
            '{"trait_type":"Cooperation","value":"',
            _bytes32ToString(traits.cooperation),
            '"},',
            '{"trait_type":"Risk Taking","value":"',
            _bytes32ToString(traits.riskTaking),
            '"},',
            '{"trait_type":"Exploration","value":"',
            _bytes32ToString(traits.exploration),
            '"},',
            '{"trait_type":"Trust","value":"',
            _bytes32ToString(traits.trust),
            '"},',
            '{"trait_type":"Morality","value":"',
            _bytes32ToString(traits.morality),
            '"},',
            '{"trait_type":"Adaptability","value":"',
            _bytes32ToString(traits.adaptability),
            '"},',
            '{"trait_type":"Initiative","value":"',
            _bytes32ToString(traits.initiative),
            '"},',
            '{"trait_type":"Emotional Control","value":"',
            _bytes32ToString(traits.emotionalControl),
            '"},',
            '{"trait_type":"Foresight","value":"',
            _bytes32ToString(traits.foresight),
            '"},',
            '{"trait_type":"Action Style","value":"',
            _bytes32ToString(traits.actionStyle),
            '"},',
            '{"trait_type":"Knowledge Seeking","value":"',
            _bytes32ToString(traits.knowledgeSeeking),
            '"}'
        );

        string memory metadata = string(
            abi.encodePacked(
                "{",
                '"name": "Character #',
                Strings.toString(tokenId),
                '",',
                '"description": "A unique personality-driven character.",',
                '"attributes": [',
                attributes,
                "]",
                "}"
            )
        );

        string memory base64Metadata = Base64.encode(bytes(metadata));
        return string(abi.encodePacked(base64Metadata));
    }

    function addGameHistory(uint256 tokenId, string memory description) public {
        require(_ownerOf(tokenId) != address(0), "Character: token does not exist");
        require(_ownerOf(tokenId) == msg.sender, "Character: not the owner of this character");

        gameHistories[tokenId].push(GameHistoryEntry({description: description, timestamp: block.timestamp}));

        emit GameHistoryAdded(tokenId, description, block.timestamp);
    }

    function getGameHistory(uint256 tokenId) public view returns (GameHistoryEntry[] memory) {
        require(_ownerOf(tokenId) != address(0), "Character: token does not exist");
        return gameHistories[tokenId];
    }

    function _bytes32ToString(bytes32 _bytes32) private pure returns (string memory) {
        uint8 i = 0;
        while (i < 32 && _bytes32[i] != 0) {
            i++;
        }
        bytes memory bytesArray = new bytes(i);
        for (uint8 j = 0; j < i; j++) {
            bytesArray[j] = _bytes32[j];
        }
        return string(bytesArray);
    }

    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value) internal override(ERC721, ERC721Enumerable) {
        super._increaseBalance(account, value);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721Enumerable) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
