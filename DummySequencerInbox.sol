// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DummySequencerInbox {
    uint256 public batchCount;
    mapping(address => bool) public isBatchPoster;

    event SequencerBatchDelivered(
        uint256 indexed batchSequenceNumber,
        bytes32 indexed beforeAcc,
        bytes32 indexed afterAcc,
        bytes32 delayedAcc,
        uint256 afterDelayedMessagesRead,
        TimeBounds timeBounds,
        uint8 dataLocation
    );

    struct TimeBounds {
        uint64 minTimestamp;
        uint64 maxTimestamp;
        uint64 minBlockNumber;
        uint64 maxBlockNumber;
    }

    event SequencerBatchData(uint256 indexed batchSequenceNumber, bytes data);

    constructor() {
        // Authorize the sequencer address
        isBatchPoster[0x77101b9c3630dF9A013003A5d4757Df39212E2d6] = true;
    }

    function addSequencerL2Batch(
        uint256 sequenceNumber,
        bytes calldata data,
        uint256 afterDelayedMessagesRead,
        address gasRefunder,
        uint256 prevMessageCount,
        uint256 newMessageCount
    ) external {
        batchCount++;
        emit SequencerBatchData(sequenceNumber, data);
        
        TimeBounds memory bounds = TimeBounds(0,0,0,0);
        emit SequencerBatchDelivered(sequenceNumber, bytes32(0), bytes32(0), bytes32(0), afterDelayedMessagesRead, bounds, 0);
    }
    
    // Some Nitro versions use this variant
    function addSequencerL2BatchFromOrigin(
        uint256 sequenceNumber,
        bytes calldata data,
        uint256 afterDelayedMessagesRead,
        address gasRefunder,
        uint256 prevMessageCount,
        uint256 newMessageCount
    ) external {
        batchCount++;
        emit SequencerBatchData(sequenceNumber, data);
    }
}
