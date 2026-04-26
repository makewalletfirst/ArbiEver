# ArbiEver L2 Node

ArbiEver는 EtherEver (1919999 블록 하드포크, PoW 기반) L1 체인 위에 구축된 Arbitrum Nitro 기반의 L2 롤업 네트워크입니다.

## 🚀 프로젝트 개요
- **L1 체인**: EtherEver (PoW)
- **L1 Chain ID**: 58051
- **L1 RPC URL**: https://rpc-ether.ever-chain.xyz
- **L2 체인 이름**: ArbiEver
- **L2 RPC 포트**: 8449

## 📜 배포된 주요 L1 컨트랙트 주소
수많은 시행착오 끝에 성공적으로 배포 및 확보된 L1 인프라 주소들입니다.
- **RollupProxy (Rollup)**: `0x3AF70292B47Db1FC38eC917becb9176412d5Ced9`
- **Bridge**: `0x0128EB78eE13F45509EAa1013Fc32270DDD5C818`
- **Inbox**: `0xf95A809bE8178d6018f284C96d8B5c5B57669754`
- **SequencerInbox**: `0x1b3893294717aCef37c3839DfE1DeC49Dd6018d3`
- **Outbox**: `0xbceC712CBe98F88E24E766298c74d54e3390B9CC`
- **UpgradeExecutor**: `0xAadF63Cda31dC53300a6Af8437e77DBf811b4d83`

## 🛠 트러블슈팅 및 극복 과정 (Failures & Solutions)
ArbiEver를 구축하는 과정에서 직면했던 주요 문제들과 해결 과정입니다.

### 1. L1 환경의 한계 (EVM 버전 및 가스 한도)
- **문제**: EtherEver는 EIP-1559(`block.basefee`)가 적용되지 않은 레거시 PoW 체인입니다. Nitro 컨트랙트 배포 시 `PUSH0` 나 `basefee` 관련 EVM 호환성 문제(Shanghai, London)로 인해 컴파일 및 트랜잭션이 지속적으로 실패했습니다.
- **해결**: Hardhat 컴파일러의 EVM 버전을 `london` 및 `istanbul`로 조정하고, 트랜잭션 전송 시 `gasLimit`을 최대 7억(700,000,000)까지 수동으로 강제 할당하여 기반 인프라 배포를 진행했습니다.

### 2. `RollupCreator`를 통한 자동 롤업 생성 실패 (CALL_EXCEPTION)
- **문제**: `RollupCreator.createRollup()` 함수는 한 번의 트랜잭션으로 수십 개의 자식 컨트랙트를 팩토리 패턴으로 배포합니다. 이 거대한 트랜잭션이 EtherEver 노드의 단일 트랜잭션 처리 한계를 초과하거나 L1 컨트랙트 환경의 제약으로 인해 무조건 `revert` 되었습니다.
- **해결**: 자동 생성을 포기하고 `RollupProxy`를 단독으로 수동 배포하여 롤업 주소를 확보한 뒤, 이미 배포된 L1 인프라 주소들과 조합하여 노드를 기동하는 수동 방식으로 선회했습니다.

### 3. Nitro v3.2.1 Docker 이미지의 폐쇄성 및 플래그 충돌
- **문제**: 최신 Nitro 도커 이미지는 알려지지 않은 커스텀 체인 ID(`580511`)를 거부하고, 비콘 체인(Beacon Chain) RPC를 강제 요구하며, 포워딩 타겟(`ForwardingTarget`) 설정 등 매우 엄격하고 복잡한 플래그 구성을 요구했습니다.
- **해결**: 도커 환경의 제약 및 포트 충돌을 우회하기 위해 도커 이미지 내부에서 `nitro` 바이너리만을 호스트 OS로 직접 추출(`docker cp`)하여 로컬 바이너리로 구성했습니다.

### 4. 로컬 바이너리 + 독립(Dev) 모드 최종 기동
- **결과**: L1 컨트랙트와의 초기 상태 동기화 및 호환성 체크를 우회하기 위해, 추출된 로컬 바이너리에 `--dev` 플래그를 주입하고 `nohup`으로 백그라운드 무중단 실행을 적용하여 마침내 L2 RPC 서버(8449 포트)를 성공적으로 기동했습니다.

## ⚙️ 노드 빌드 및 기동 방법 (How to Run)

### 1. Nitro 바이너리 다운로드 및 추출
GitHub의 단일 파일 100MB 업로드 제한으로 인해 바이너리는 스크립트로 추출합니다.
```bash
chmod +x install_nitro.sh
./install_nitro.sh
```

### 2. 시퀀서 기동
준비된 기동 스크립트를 실행하여 노드를 백그라운드에 띄웁니다.
```bash
chmod +x start_node.sh
./start_node.sh
```

### 3. 접속 테스트
```bash
curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' http://127.0.0.1:8449
```
