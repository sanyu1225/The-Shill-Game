// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import {ERC721} from "openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";
import {ERC721Enumerable} from "openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import {Ownable} from "openzeppelin-contracts/contracts/access/Ownable.sol";
import {Traits} from "./Traits.sol";

contract Character is ERC721, ERC721Enumerable, Ownable {
    using Traits for *;

    uint256 public nextTokenId;
    mapping(uint256 => Traits.TraitSet) public tokenTraits;

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
