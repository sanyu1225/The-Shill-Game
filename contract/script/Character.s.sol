// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {Character} from "../src/Character.sol";

contract CharacterScript is Script {
    Character public character;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        character = new Character(msg.sender);

        vm.stopBroadcast();
    }
}
