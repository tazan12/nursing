# ECG Rhythm Lab

PC와 휴대폰에서 사용할 수 있는 반응형 심전도 리듬 학습 PWA입니다.

## 구현 기능

- 모바일·태블릿·PC 반응형 화면
- 허혈/ST 변화, 심방성·심실성 부정맥, 전도장애 퀴즈
- 교육용 합성 ECG 파형
- 정답·오답 피드백과 간호 판단 해설
- 브라우저 학습기록 저장
- 서비스 워커 기반 오프라인 사용
- Android/데스크톱 브라우저 앱 설치 지원
- GitHub Pages 자동 배포 워크플로

## 실행

정적 파일이므로 저장소를 내려받아 `index.html`을 열거나 간단한 웹 서버로 실행할 수 있습니다.

```bash
python -m http.server 8080
```

브라우저에서 `http://localhost:8080`으로 접속합니다.

## GitHub Pages

저장소 Settings → Pages → Build and deployment의 Source를 **GitHub Actions**로 지정하면 `main` 브랜치 변경 때 자동 배포됩니다.

## 데이터와 저작권

이 인터페이스는 ECG-QA 데이터셋 구조와 교육 아이디어를 참고한 독립 구현입니다. 현재 포함된 문항과 파형은 교육용으로 새로 작성·합성했으며 실제 PTB-XL 또는 MIMIC-IV-ECG 원시 파형을 포함하지 않습니다.

ECG-QA 원본: https://github.com/Jwoo5/ecg-qa  
원본 라이선스: CC BY 4.0

실제 ECG-QA 전체 데이터와 파형을 연결하려면 PTB-XL 또는 자격 승인이 필요한 MIMIC-IV-ECG 자료를 별도로 매핑해야 합니다.

## 주의

본 앱은 교육용이며 실제 환자의 진단·치료·응급의사결정을 대신하지 않습니다.
