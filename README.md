### Test Suite for TF Saved Model (TF Object Detection)

* 개요: 텐서플로우의 이미지 인식 모델에 대한 자동화 테스트 툴

* 사용법:
```
cd ..../pyqt_tf_saved_model_testsuite/python
python3 main.py
```

* 필요 설치 패키지(Python):
```
pip3 install tensorflow or pip3 install tensorflow-gpu
pip3 install opencv-python
pip3 install PyQt5==5.9.2
```

* 테스트 데이터 구성 방법:
   1. 데스트 데이터셋은 특정 디렉토리를 지정하여 해당 디렉토리를 테스트데이터 루트디렉토리로 정한다.
   2. 루트 디렉토리내에 해당 그룹을 이름으로 하여 디렉토리를 생성하고 같은 그룹내에 속한 테스트 이미지군을 모두 넣어 한 그룹내에 위치하게 한다.
   3. 각 그룹내에는 고정된 이름의 classes.json파일이 위치하여야 하며 해당 파일에는 해당 그룹에서 인식해야할 클래스들의 라벨 목록이 작성되어야 한다.

* classes.json파일 생성은 Pascal VOC 데이터셋 구조에 기반하여 생성되며 생성 스크립트는 아래 위치한다.
   * ./python/dataset_tools/create_classes_json_for_testsuite.py
