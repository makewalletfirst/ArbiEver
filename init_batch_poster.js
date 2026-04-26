const { ethers } = require("ethers");
async function main() {
    const l1Provider = new ethers.providers.JsonRpcProvider("https://rpc-ether.ever-chain.xyz");
    // L1 인프라의 소유자(Admin) 권한이 필요합니다.
    const adminWallet = new ethers.Wallet("0x52a45ac3862b98c721198f08e828ea170f1787b7ed603637a327a5f687d6c520", l1Provider);
    const seqInboxAddr = "0x81187148F099342D54130Acca04b24BB97965db4";
    const sequencerAddr = "0x77101b9c3630dF9A013003A5d4757Df39212E2d6";
    const abi = ["function setIsBatchPoster(address addr, bool isBatchPoster) external"];
    const seqInbox = new ethers.Contract(seqInboxAddr, abi, adminWallet);
    console.log("Setting Sequencer as authorized BatchPoster on L1...");
    const tx = await seqInbox.setIsBatchPoster(sequencerAddr, true, { gasPrice: 10000000000, gasLimit: 200000 });
    await tx.wait();
    console.log("Success! Sequencer is now authorized to post batches to L1.");
}
main();
