// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {Character} from "../src/Character.sol";

contract CharacterTest is Test {
    Character public character;

    function setUp() public {
        character = new Character(msg.sender);
    }
}
