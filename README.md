# jpg-resizer

블로그에 사진을 올릴 때, 이미지 리사이징을 하기가 귀찮아서 만들어 봤습니다. 먼저 픽셀을 줄이고 이미지의 퀄리티를 낮추어 구현하였습니다.

## Use

### 1. images 폴더에 리사이징을 원하는 .jpg 파일을 복사한다.

### 2. 아래 스크립트를 통하여 코드를 실행한다.

```sh
make
make default
make run kb={target image size per kb} max_width={max image width pixel} max_height={max image height pixel}"
make help
make clean
```

### 3. 생성된 ./resized_images/ 폴더 안에 결과물이 생성된다.
