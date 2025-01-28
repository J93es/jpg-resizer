# jpg-resizer

블로그에 사진을 올릴 때, 이미지 리사이징을 하기가 귀찮아서 만들어 봤습니다. 먼저 픽셀을 줄이고 이미지의 퀄리티를 낮추어 구현하였습니다. 워터마크 또한 삽입 가능합니다.

## Use

### 1. images 폴더에 리사이징을 원하는 .jpg 파일을 복사합니다.

### 2. 아래 스크립트를 통하여 코드를 실행합니다.

```sh
make
make default
make run kb={target image size (kb)} max_width={max image width(pixel)} max_height={max image height(pixel) watermark_text={watermark text(optional)}}
make help
make clean
```

### 3. 생성된 ./resized_images/ 폴더 안에 결과물이 생성됩니다.

## Notify

- 이 서비스에는 네이버에서 제공한 나눔글꼴이 적용되어 있습니다.
