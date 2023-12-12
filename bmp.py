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
