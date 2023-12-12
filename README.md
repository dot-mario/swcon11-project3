# swcon11-project3
 Project #3: Develop Your Own Game Engine

 
# **Project #3: Develop Your Own Game Engine (Report)**

## Goal

수업을 듣던 도중 이미지는 어떻게 불러올 수 있는지 궁금해져, 이미지를 불러오는 게임 엔진을 만들자고 결정했습니다.

대중적인 JPG 파일을 읽어 오는 것을 목표로 시도했지만, 이러한 파일 형식은 복잡한 이미지 압축 알고리즘을 사용했기 때문에 이 파일을 읽기 위해서는 디코딩 하는 과정을 따라야 했습니다. 이 과정이 생각보다 너무 어려웠기 때문에 압축 알고리즘을 사용하지 않는 BMP 파일 형식을 불러오는 것으로 목표를 수정했습니다.

> 제가 찾은 JPG 디코딩 기사입니다.
https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/#jpeg-decoding해당 글에서는 제가 원하는 기능을 완벽하게 구현하였지만 다양한 알고리즘에 대한 이해를 짧은 시간 안에 해내지 못할 것으로 생각되어 포기하게 되었습니다.
> 

---

## Game Engine Design & Structure

헤더 파일을 읽어 높이와 너비를 받은 다음 픽셀 정보를 읽어 저장합니다.

이후 높이,너비,픽셀 정보를 pygame을 통해서 출력합니다.

---

## Feature Description along with Code Description

### 헤더 정보 읽기

BMP 파일 포멧의 정보는 여기서 확인 할 수 있었습니다.

[https://ko.wikipedia.org/wiki/BMP_파일_포맷](https://ko.wikipedia.org/wiki/BMP_%ED%8C%8C%EC%9D%BC_%ED%8F%AC%EB%A7%B7)

https://en.wikipedia.org/wiki/BMP_file_format

| BMP 헤더 | BMP 파일에 대한 일반 정보를 담고 있다. |
| --- | --- |
| 비트맵 정보(DIB 헤더) | 비트맵 그림에 대한 자세한 정보를 담고 있다. |
| 색 팔레트 | 인덱스 컬러 비트맵에 쓰이는 색의 정의를 담고 있다. |
| 비트맵 데이터 | 화소 대 화소 단위의 실제 그림을 담고 있다. |

파일을 불러오기 위해서는 가로, 세로 픽셀과 비트맵 깊이, 압축 방식을 알아야 합니다.

BMP 헤더는 건너 뛰고, DIB 헤더에 접근해야 합니다.

| 오프셋 # | 크기 | 목적 |
| --- | --- | --- |
| 14 | 4 | 이 헤더의 크기 (40 바이트) |
| 18 | 4 | 비트맵 가로 (단위는 화소, signed integer). |
| 22 | 4 | 비트맵 세로 (단위는 화소, signed integer). |
| 26 | 2 | 사용하는 색 판(color plane)의 수. 1로 설정해야 한다. |
| 28 | 2 | 한 화소에 들어가는 비트 수이며 그림의 색 깊이를 뜻한다. 보통 값은 1, 4, 8, 16, 24, 32이다. |
| 30 | 4 | 압축 방식. 가능한 값에 대한 목록은 다음 표를 참조하라. |
| 34 | 4 | 그림 크기. 압축되지 않은 비트맵 데이터의 크기(아래 참조)이며, 파일 크기와 혼동하지 말 것. |
| 38 | 4 | 그림의 가로 해상도. (https://ko.wikipedia.org/wiki/%EB%AF%B8%ED%84%B0 당 화소, signed integer) |
| 42 | 4 | 그림의 세로 해상도. (미터 당 화소, signed integer) |
| 46 | 4 | 색 팔레트의 색 수, 또는 0에서 기본값 2n. |
| 50 | 4 | 중요한 색의 수. 모든 색이 중요할 경우 0. 일반적으로 무시. |

일반적인 V3 포멧의 헤더는 다음과 같습니다. 18 비트의 위치부터 4비트씩 가로 세로에 대한 정보가 있고, 2비트 떨어진 곳에 비트맵 깊이 정보가 있습니다.

여기서는 일반적으로 사용되는 압축되지 않은 24비트맵 깊이만을 불러오겠습니다.

```python
import struct

def load_bmp(filename):
    with open(filename, 'rb') as f:
        # BMP 파일 헤더 읽기
        f.read(18)  # 18비트 건너뛰기.
        width = struct.unpack('I', f.read(4))[0]  # 너비 읽기
        height = struct.unpack('I', f.read(4))[0]  # 높이 읽기
        f.read(2)  # 컬러 플레인 수 건너뛰기
        bit_depth = struct.unpack('H', f.read(2))[0]  # 비트 깊이 읽기
        bit_compress = struct.unpack('I', f.read(4))[0]  # 비트 압축 방식 읽기
        f.read(20)  # 나머지 헤더 부분 건너뛰기

        # 24비트 픽셀 데이터 읽기
        if bit_depth != 24 or bit_compress != 0:
            raise NotImplementedError('압축되지 않은 24비트 BMP 파일만 지원합니다.')
```

### 픽셀 데이터 읽기

24비트 BMP 파일은 각 픽셀마다 3바이트 (각각 빨강, 초록, 파랑 채널에 대한 1바이트)를 사용합니다. 따라서 이미지의 각 행을 순회하여, 각 픽셀에 대한 3바이트를 읽어야 합니다. 이 때, BMP 파일 포맷은 색상을 BGR (파랑, 초록, 빨강) 순서로 저장하므로, 읽은 각 비트 값을 RGB 순서로 바꾸어 리스트에 추가했습니다.

```python
import struct

def load_bmp(filename):
    with open(filename, 'rb') as f:
        
        ###
        
        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                b, g, r = struct.unpack('BBB', f.read(3))
                row.append((r, g, b))  # RGB 순서로 변환
            pixels.append(row)

        return pixels, width, height
```


-추가설명

`struct.unpack('I', f.read(4))[0]` 에서 `I`, `B`, `H` 와 같은 포멧 문자를 사용합니다.

- **`B`**: 부호 없는 바이트(Byte). 1바이트 크기의 자료형으로, 0에서 255까지의 값을 나타낼 수 있습니다.
- **`H`**: 부호 없는 짧은 정수(Unsigned short). 2바이트 크기의 자료형으로, 0에서 65535까지의 값을 나타낼 수 있습니다.
- **`I`**: 부호 없는 정수(Unsigned int). 4바이트 크기의 자료형으로, 0에서 4294967295까지의 값을 나타낼 수 있습니다.
- **`'BBB'`:** 연속된 세 개의 바이트를 개별적으로 읽을 수 있습니다.

### pygame을 통해 나타내기

![image](https://github.com/dot-mario/swcon11-project3/assets/74451418/2e8f3c02-446f-464d-aacf-6e2220deed83)


비트맵의 픽셀 데이터는 pygame의 좌표계와 달리 첫번째 픽셀이 좌측 하단에 존재하여 열이 위로 올라가는 형식이기 때문에 불러온 픽셀 데이터를 pygame으로 나타내기 위해서는 y좌표를 반전시켜야 합니다.

또한 인덱스는 0부터 시작하기 때문에 높이에 1을 빼야합니다.

```python
import pygame

def display_image(pixels, width, height):
    # Pygame 초기화
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    # 픽셀 데이터를 화면에 그리기
    for y in range(height):
        for x in range(width):
            screen.set_at((x, y), pixels[height - y - 1][x])  # y 좌표 반전

    pygame.display.flip()

    # 이벤트 루프
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
```

### 전체 코드

```python
import struct

def load_bmp(filename):
    with open(filename, 'rb') as f:
        # BMP 파일 헤더 읽기
        f.read(18)  # 18비트 건너뛰기.
        width = struct.unpack('I', f.read(4))[0]  # 너비 읽기
        height = struct.unpack('I', f.read(4))[0]  # 높이 읽기
        f.read(2)  # 컬러 플레인 수 건너뛰기
        bit_depth = struct.unpack('H', f.read(2))[0]  # 비트 깊이 읽기
        bit_compress = struct.unpack('I', f.read(4))[0]  # 비트 압축 방식 읽기
        f.read(20)  # 나머지 헤더 부분 건너뛰기

        # 24비트 픽셀 데이터 읽기
        if bit_depth != 24 or bit_compress != 0:
            raise NotImplementedError('압축되지 않은 24비트 BMP 파일만 지원합니다.')
        
        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                b, g, r = struct.unpack('BBB', f.read(3))
                row.append((r, g, b))  # RGB 순서로 변환
            pixels.append(row)

        return pixels, width, height
    
import pygame

def display_image(pixels, width, height):
    # Pygame 초기화
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    # 픽셀 데이터를 화면에 그리기
    for y in range(height):
        for x in range(width):
            screen.set_at((x, y), pixels[height - y - 1][x])  # y 좌표 반전

    pygame.display.flip()

    # 이벤트 루프
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

pixels, width, height = load_bmp('chair.bmp')
display_image(pixels, width, height)
```

### 결과

예시 파일인 chair.bmp 파일을 불러온 결과입니다.

![image](https://github.com/dot-mario/swcon11-project3/assets/74451418/b29bf9a0-ea56-409d-b82c-069d37c5dfad)


윈도우 기본 프로그램을 이용해 불러온 동일한 사진입니다.

![image](https://github.com/dot-mario/swcon11-project3/assets/74451418/8f208a9c-81a2-4be5-a65a-18827c43aef7)


---

## Execution Environment

pygame-ce 2.3.2 (SDL 2.26.5, Python 3.11.1)

window11

vscode
