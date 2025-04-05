// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.22;

import {Script, console} from "forge-std/Script.sol";
import {Character} from "../src/Character.sol";

contract Deploy is Script {
    Character public character;

    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        address deployer = vm.addr(deployerPrivateKey);
        character = new Character(deployer);
        console.log("Character deployed at:", address(character));

        vm.stopBroadcast();
    }
}

// forge script script/Deploy.s.sol \
//    --rpc-url zircuit-testnet \
//    --chain 48898 \
//    --broadcast \
//    --legacy

// forge verify-contract --verifier-url https://explorer.garfield-testnet.zircuit.com/api/contractVerifyHardhat 0x4ff5A588574Bd05A2b7dD5C2Cf8a11Db2292E173 src/Character.sol:Character --root . --etherscan-api-key F672E5A31BA4CF72E7990CA49FDA7B1D96 --constructor-args

// forge script script/Deploy.s.sol \
//    --rpc-url celo-alfajores \
//    --broadcast

// forge verify-contract \
//   --rpc-url celo-alfajores \
//   0xB97919280F61C177eBE01ebc897E0BB5E8A6f6Fa \
//   src/Character.sol:Character \
//   --verifier blockscout \
//   --verifier-url https://celo-alfajores.blockscout.com/api/
