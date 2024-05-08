import sensor, image, time, math, os, pyb, display
from pyb import UART, Pin, Timer


x0 = 47     # 블럭을 pick up하는 위치
y0 = -202
z0 = 93

z1 = 128    # pick up 하는 높이

bx = 158    # 블럭의 위치(+자선이나 이미지 인식하는 좌표로 사용됨)
by = 136

Rc = 0
Dc = 0
Gc = 0
Bc = 0
Vc = 0
NC = 0
cc = 0  # 블럭 인식 필터에 사용되는 변수

# LAB값으로 객체 인식에 필요한 범위 L최저,L최고,A최저,A최고,B최저,B최고 값
thresholds = [(60, 80, 35, 55, -25, 0),    #r
              (20, 40, 10, 50, -70, -30),    #d
              (70, 80, -50, -30, -20, 0),   #g
              (50, 65, -15, 15, -60, -40),  #b
              (65, 80, 15, 40, -50, -30)]      #v


color_roi = (bx-13, by-21, 30, 30) # 색깔을 감지하고자하는 범위
lcd_roi = (bx-64, 40, 128, 160) # LCD에 출력할 범위



tim = Timer(4, freq=1000)
Led = tim.channel(3, Timer.PWM, pin=Pin("P9"), pulse_width_percent=18)  #  pulse_width_percent 값을 기준으로 LED를 PWM제어함 (100에 가까울 수록 밝음)

def mirobot_wait_finish():
    inByte = ''
    print('wait')
    while inByte.find('>'):
        while uart.any() > 0:
            inByte = uart.readline().decode()
       #lcd.display(sensor.snapshot())
    #print(inByte)  # 打印机械臂返回数据，用于调试开发
    print('finish')



uart = UART(3, 115200)
Key = Pin('P6', Pin.IN, Pin.PULL_UP)
keyvalue = Key.value()
pyb.delay(1000)
uart.write("$40 = 1\n")
uart.write("$H\n")
mirobot_wait_finish()
pyb.delay(1000)
uart.write("M20 G90 G00 F2000\n")
uart.write("M3S0\n")
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames()
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

lcd = display.SPIDisplay()
if keyvalue==0:
    # 위치보정
    while Key.value():
        img = sensor.snapshot()
        img.draw_cross(bx, by, color = (255, 255, 255), size = 10, thickness = 1)
        img.draw_rectangle(bx-65, by-13, 130, 26, color = (255, 255, 255), thickness = 1, fill = False)
        lcd.write(img, roi = lcd_roi)
    uart.write('X'+str(x0) + 'Y'+str(y0) + 'Z'+str(z0+20) + '\n')
    pyb.delay(1000)
    while Key.value():
        img = sensor.snapshot()
        img.draw_cross(bx, by, color = (255, 255, 255), size = 10, thickness = 1)
        img.draw_rectangle(bx-65, by-13, 130, 26, color = (255, 255, 255), thickness = 1, fill = False)
        lcd.write(img, roi = lcd_roi)
    uart.write('M21G90G1X0Y0Z0A0B0C0\n')

pyb.delay(2000)

while(True):
    img = sensor.snapshot() # 카메라로 이미지 가져옴
    img.draw_cross(bx-2, by-2, color = (255, 255, 255), size = 10, thickness = 1)                      # 십자가 그리기
    img.draw_rectangle(bx-17, by-18, 30, 30, color = (255, 255, 255), thickness = 1, fill = False) # 사각형 그리기
    lcd.write(img, roi = lcd_roi)                                                                # LCD에 십자가랑 사각형 출력
    # color_roi 범위안에서 객체 찾기
    for blob in img.find_blobs(thresholds, roi = color_roi, x_stride=10, y_stride=10, area_threshold=100): # color_roi 범위안에 10x10에 해당 색깔이 존재하는지 찾기
        # 한 번만 인식하면 잘못 인식 될 수도 있으므로 여러차례 인식하고, 같은 값을 여러번 출력해야 동작하도록 하는 필터 알고리즘
        Nc = 1
        if blob.code() == 1:                              # 코드가 1이면
            Rc+= 1 # Rc에 1을 더함
            Nc = 0
            img.draw_string(blob.x(), blob.y() + 10, 'R') # 찾은 객체에 R이라는 이름을 부여
            if Rc > 10:                                    # Rc가 5초과면
                cc = 'R'                                  # cc에 R로 저장
        elif blob.code() == 2:
            Dc+= 2
            Nc = 0
            img.draw_string(blob.x(), blob.y() + 10, 'D')
            if Dc > 20:
                cc = 'D'
        elif blob.code() == 4:
            Gc+= 1
            Nc = 0
            img.draw_string(blob.x(), blob.y() + 10, 'G')
            if Gc > 5:
                cc = 'G'
        elif blob.code() == 8:
            Bc+= 1
            Nc = 0
            img.draw_string(blob.x(), blob.y() + 10, 'B')
            if Bc > 5:
                cc = 'B'
        elif blob.code() == 16:
            Vc+= 1
            Nc = 0
            img.draw_string(blob.x(), blob.y() + 10, 'V')
            if Vc > 10:
                cc = 'V'
        if Nc == 1 :
            if Dc > 0 :
                Dc-= 1
        img.draw_cross(blob.cx(), blob.cy())
        img.draw_rectangle(blob.rect())
        lcd.write(img, roi = lcd_roi)

        if cc != 0 :
                # cc가 0이 아니면 (객체가 인지되어 변수에 값이 저장되면)
                uart.write('X'+str(x0) + 'Y'+str(y0) + 'Z'+str(z0+20) + '\n')       # 로봇팔이 객체를 pick up함
                uart.write("M3S1000\n")
                uart.write('X'+str(x0) + 'Y'+str(y0) + 'Z'+str(z0) + '\n')
                uart.write("G4P0.5\n")
                uart.write('X'+str(x0) + 'Y'+str(y0) + 'Z'+str(z0+40) + '\n')
                mirobot_wait_finish()
                uart.write("X135 Y-100 Z120\n")

                # 각 색깔에 해당하는 슬롯에 넣음
                if cc == 'R':
                    uart.write("X135 Y-58" + 'Z'+str(z1)+'\n')
                    uart.write("X186 Y-58" + 'Z'+str(z1)+'\n')
                elif cc == 'D':
                    uart.write("X135 Y-32" + 'Z'+str(z1)+'\n')
                    uart.write("X186 Y-32" + 'Z'+str(z1)+'\n')
                elif cc == 'G':
                    uart.write("X135 Y-5" + 'Z'+str(z1)+'\n')
                    uart.write("X190 Y-5" + 'Z'+str(z1)+'\n')
                elif cc == 'V':
                    uart.write("X135 Y20" + 'Z'+str(z1)+'\n')
                    uart.write("X191 Y20" + 'Z'+str(z1)+'\n')
                elif cc == 'B':
                    uart.write("X135 Y47" + 'Z'+str(z1)+'\n')
                    uart.write("X190 Y47" + 'Z'+str(z1)+'\n')

                uart.write("M3S0\n")
                uart.write("Z160\n")
                uart.write("X160 Y-100 Z136\n")
                Rc = 0
                Dc= 0
                Gc = 0
                Bc = 0
                Vc = 0
                cc = 0   # 동작했으니 필터용 변수 초기화
                pyb.delay(6000)         # 동작이 완료될 때까지 기다리고 다시 반복

