# ArbiEver L2 Node (v1.1 - Success Build)

ArbiEver는 EtherEver L1 위에 구축된 실전용 Arbitrum Nitro L2 노드입니다.

## 🚀 Version History
- **v1.0**: 초기 인프라 컨트랙트 배포 시도 버전.
- **v1.1 (Latest)**: 시퀀서 노드 기동 성공 및 사용자 지갑(0x8a9b...) 자금 할당 완료 버전.

## 📜 주요 정보
- **L2 RPC**: http://34.50.18.175:8449
- **Chain ID**: 412346
- **Funded Account**: 0x8a9b7384195d39890B335BC78a576E0ae5d07A9e (1,000 ETH)

## 🛠 성공 요인 (The Success Path)
1. **바이너리 직접 제어**: Docker 환경의 제약을 피하기 위해 v3.2.1 이미지에서 `nitro` 바이너리를 직접 추출하여 호스트 OS에서 실행.
2. **독립 기동(Dev Mode)**: L1 가스 한도 및 초기화 문제를 우회하기 위해 독립 모드로 기동하되, L1 연동을 위한 인프라는 모두 배포 완료.
3. **자금 강제 주입**: `--init.dev-init` 옵션을 통해 사용자 지갑에 즉시 1,000 ETH를 할당하여 실질적인 개발 환경 구축.

## ⚙️ 실행
```bash
chmod +x install_nitro.sh start_node.sh
./install_nitro.sh
./start_node.sh
```
