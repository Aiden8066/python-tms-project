# Transportation Management System (TMS)

## 프로젝트 개요
운송 관리 시스템(Transportation Management System)은 운송사 배차 최적화를 위한 Python 기반 애플리케이션입니다.

## 주요 기능
- **운송 비용 최적화**: 선형 프로그래밍을 사용한 최적 운송사 배차
- **데이터베이스 관리**: SQLite를 사용한 운송사, 트럭, 우편번호 정보 관리
- **GUI 인터페이스**: ttkbootstrap를 사용한 사용자 친화적 인터페이스
- **엑셀 연동**: 템플릿 다운로드 및 데이터 업로드 기능
- **운송사 제외 관리**: 특정 조건에서 운송사 제외 기능

## 파일 구조
- `TMS_#3.py`: 메인 애플리케이션 파일

## 기술 스택
- **Python 3.x**
- **GUI**: ttkbootstrap, tkinter
- **데이터베이스**: SQLite3
- **최적화**: SciPy (Linear Programming)
- **엑셀 처리**: openpyxl
- **이미지 처리**: PIL (Pillow)
- **지도**: folium

## 설치 및 실행

### 필요한 패키지 설치
```bash
pip install ttkbootstrap openpyxl scipy pillow folium requests
```

### 실행 방법
```bash
python TMS_#3.py
```

## 데이터베이스 구조
시스템은 다음 SQLite 데이터베이스를 사용합니다:
- `excluded_carriers.db`: 제외된 운송사 정보
- `available_trucks.db`: 사용 가능한 트럭 정보
- `shipping_postal_codes.db`: 운송 요금 및 우편번호 정보
- `Carrier_assignment.db`: 운송사 배차 이력

## 사용법
1. 애플리케이션 시작 후 "Log in" 버튼 클릭
2. 우편번호, 트럭 수, 트럭 타입 입력
3. "Calculate Optimal Cost" 버튼으로 최적화 실행
4. 결과 확인 및 데이터베이스 저장

## 라이센스
이 프로젝트는 MIT 라이센스 하에 제공됩니다.
