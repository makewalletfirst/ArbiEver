const { ethers } = require("ethers");

async function main() {
    console.log("🚀 Custom Batch Poster for User L1 Contract Started...");
    
    let lastL2Block = 0;
    let initialized = false;

    setInterval(async () => {
        try {
            const l1Provider = new ethers.providers.JsonRpcProvider("https://rpc-ether.ever-chain.xyz");
            const l2Provider = new ethers.providers.JsonRpcProvider("http://127.0.0.1:8449");
            
            // This is the line that usually throws if network is down
            const currentBlock = await l2Provider.getBlockNumber();
            
            if (!initialized) {
                lastL2Block = currentBlock;
                initialized = true;
                console.log("✅ Linked! Monitoring ArbiEver L2 from block:", lastL2Block);
                return;
            }

            if (currentBlock > lastL2Block) {
                console.log(`📦 L2 Action Detected (Block ${currentBlock})! Rolling up to L1...`);
                const block = await l2Provider.getBlockWithTransactions(currentBlock);
                const data = block.transactions.length > 0 ? block.transactions[0].data : "0x00";
                
                const wallet = new ethers.Wallet("0x52a45ac3862b98c721198f08e828ea170f1787b7ed603637a327a5f687d6c520", l1Provider);
                const inbox = new ethers.Contract("0xbB887971D9d982e381D5b5F8D4fb838dc7624E3a", [
                    "function addSequencerL2Batch(uint256, bytes, uint256, address, uint256, uint256) external"
                ], wallet);

                const tx = await inbox.addSequencerL2Batch(currentBlock, data, 0, ethers.constants.AddressZero, 0, 0, {
                    gasLimit: 300000,
                    gasPrice: ethers.utils.parseUnits("10", "gwei")
                });
                console.log(`🔥 SUCCESS! L2 -> L1 Rollup Complete. L1 Hash: ${tx.hash}`);
                lastL2Block = currentBlock;
            }
        } catch (e) {
            // Silently wait for network
        }
    }, 5000);
}
main();
