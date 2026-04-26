const { ethers } = require("ethers");

async function main() {
    const l1Provider = new ethers.providers.JsonRpcProvider("https://rpc-ether.ever-chain.xyz");
    const l2Provider = new ethers.providers.JsonRpcProvider("http://127.0.0.1:8449");
    const wallet = new ethers.Wallet("0x52a45ac3862b98c721198f08e828ea170f1787b7ed603637a327a5f687d6c520", l1Provider);
    
    const inboxAddr = "0xbB887971D9d982e381D5b5F8D4fb838dc7624E3a";
    const inbox = new ethers.Contract(inboxAddr, ["function addSequencerL2Batch(uint256, bytes, uint256, address, uint256, uint256) external"], wallet);

    console.log("Reading L2 Block #4 data...");
    const block = await l2Provider.getBlockWithTransactions(4);
    const data = block.transactions[0].data;

    console.log("Rolling up to L1 (0xbB88...) with L2 block data...");
    const tx = await inbox.addSequencerL2Batch(4, data, 0, ethers.constants.AddressZero, 0, 0, {
        gasLimit: 300000,
        gasPrice: ethers.utils.parseUnits("10", "gwei")
    });

    console.log("✅ TRANSACTION SENT!");
    console.log("L1 Hash:", tx.hash);
    await tx.wait();
    console.log("🔥 ROLLUP CONFIRMED ON L1 BLOCK EXPLORER!");
}
main();
