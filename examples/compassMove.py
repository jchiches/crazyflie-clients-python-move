
#
# PS Move API - An interface for the PS Move Motion Controller
# Copyright (c) 2011 Thomas Perl <m@thp.io>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#


from __future__ import division
import sys
sys.path.append("../../../psmoveapi/build")
import psmove
import time
import math

'''
Created on Aug 19, 2014

@author: bitcraze
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CompassWidget(QWidget):

    angleChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
    
        QWidget.__init__(self, parent)
        
        self.max = -1
        self.move = psmove.PSMove()
        self.setStyleSheet("background-color:transparent;");
        self._angle = 0.0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
        self.SF = sensorFusion()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        
        painter.end()
    
    def drawMarkings(self, painter):
    
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)
        
        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)
        
        painter.setFont(font)
        
        i = 0
        while i < 360:
            if i == 0:
                painter.setPen(self.palette().color(QPalette.Highlight))
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(-metrics.width(self._pointText[i]) / 2.0, -52, self._pointText[i])
                painter.setPen(self.palette().color(QPalette.Shadow))
            elif i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(-metrics.width(self._pointText[i]) / 2.0, -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            
            painter.rotate(15)
            i += 15
        
        painter.restore()
    
    def drawNeedle(self, painter):
    
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)
        
        painter.setPen(QPen(self.palette().color(QPalette.Shadow), 2, Qt.SolidLine))
        painter.setBrush(self.palette().brush(QPalette.Shadow))
        
        '''
        painter.drawPolygon(
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                      QPoint(0, 45), QPoint(-10, 0)])
            )
        '''
        r = 8
        c = 25
        c2 = c - r / 2
        painter.drawLine(0, -c2, 0, c2)
        painter.drawLine(-c2, 0, c2, 0)
        
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(QPoint(0, c), r, r)
        painter.drawEllipse(QPoint(-c, 0), r, r)
        painter.drawEllipse(QPoint(c, 0), r, r)
        
        painter.setBrush(self.palette().brush(QPalette.Highlight))
        '''
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
                      QPoint(0, -30), QPoint(-5, -25)])
            )
        '''
        painter.drawEllipse(QPoint(0, -c), r, r)
        
        painter.restore()
    
    def sizeHint(self):
    
        return QSize(150, 150)
    
    def angle(self):
        return self._angle
    
    @pyqtSlot(float)
    def setAngle(self, angle):
    
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
    
    angle = pyqtProperty(float, angle, setAngle)
    
    @pyqtSlot(float)
    def setValue(self, angle):
        self.setAngle(angle)
        
    def movefunc(self):
        '''
        if self.move.connection_type == psmove.Conn_Bluetooth:
            print('bluetooth')
        elif self.move.connection_type == psmove.Conn_USB:
            print('usb')
        else:
            print('unknown')
        '''
        # while True:
        if self.move.poll():
            
            buttons = self.move.get_buttons()
            if buttons & psmove.Btn_MOVE:
                self.move.set_leds(0, 255, 0)
                self.move.update_leds()
                self.SF = sensorFusion()
            '''   
            trigger_value = self.move.get_trigger()
            self.move.set_leds(trigger_value, 0, 0)
            self.move.update_leds()
            '''
                
            ax, ay, az = self.move.get_accelerometer_frame(psmove.Frame_SecondHalf)
            gx, gy, gz = self.move.get_gyroscope_frame(psmove.Frame_SecondHalf)
            
            gx = gx * 180 / math.pi
            gy = gy * 180 / math.pi
            gz = gz * 180 / math.pi
            
            #print "A: %5.2f %5.2f %5.2f " % ( ax , ay , az )
            print "G: %8.2f %8.2f %8.2f " % ( gx , gy , gz )
            
            self.SF.sensfusion6UpdateQ(gx, gy, gz, ax, ay, az, 1/100)
            roll, pitch, yaw = self.SF.sensfusion6GetEulerRPY()
            self.setAngle(-yaw)
        '''
            buttons = move.get_buttons()
            if buttons & psmove.Btn_TRIANGLE:
                print('triangle pressed')
                move.set_rumble(trigger_value)
            else:
                move.set_rumble(0)
            battery = move.get_battery()
            if battery == psmove.Batt_CHARGING:
                print('battery charging via USB')
            elif battery >= psmove.Batt_MIN and battery <= psmove.Batt_MAX:
                print('battery: %d / %d' % (battery, psmove.Batt_MAX))
            else:
                print('unknown battery value:', battery)
            dt = 0.001#1ms
            #print('accel:', (move.ax, move.ay, move.az))
            #print('gyro:', (move.gx, move.gy, move.gz))
            #print('magnetometer:', (move.mx, move.my, move.mz))
            #mag max = 2048
            #acc gyro max = 16016
            #div = 2048/360  #mag
            #div = 16016/360 #acc/gyro
            #gx = pitch
            #gy = -roll
            #gz = yaw
            GYROSCOPE_SENSITIVITY = 65.536
            var = self.move.gy - self.move.gz/GYROSCOPE_SENSITIVITY*dt
            #pitch
            var = -var
            print '%5d %5.3f ' % (var, var*dt)
            angle = self.angle - var*dt
            self.setAngle(angle)
	    '''
class sensorFusion():
    
    def __init__(self):
        self.twoKp = (2.0 * 0.4)  # 2 * proportional gain
        self.twoKi = (2.0 * 0.001)  # 2 * integral gain

        self.integralFBx = 0.0
        self.integralFBy = 0.0
        self.integralFBz = 0.0  # integral error terms scaled by Ki
        
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0  # quaternion of sensor frame relative to auxiliary frame
    
    def sensfusion6UpdateQ(self, gx, gy, gz, ax, ay, az, dt):
        gx = gx * math.pi / 180
        gy = gy * math.pi / 180
        gz = gz * math.pi / 180
        
        # Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
        if(not ((ax == 0.0) and (ay == 0.0) and (az == 0.0))):
            # Normalise accelerometer measurement
            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm
           
            # Estimated direction of gravity and vector perpendicular to magnetic flux
            halfvx = self.q1 * self.q3 - self.q0 * self.q2
            halfvy = self.q0 * self.q1 + self.q2 * self.q3
            halfvz = self.q0 * self.q0 - 0.5 + self.q3 * self.q3
           
            # Error is sum of cross product between estimated and measured direction of gravity
            halfex = (ay * halfvz - az * halfvy)
            halfey = (az * halfvx - ax * halfvz)
            halfez = (ax * halfvy - ay * halfvx)
           
            # Compute and apply integral feedback if enabled
            if(self.twoKi > 0.0):
                self.integralFBx += self.twoKi * halfex * dt  # integral error scaled by Ki
                self.integralFBy += self.twoKi * halfey * dt
                self.integralFBz += self.twoKi * halfez * dt
                gx += self.integralFBx  # apply integral feedback
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                self.integralFBx = 0.0  # prevent integral windup
                self.integralFBy = 0.0
                self.integralFBz = 0.0
            # Apply proportional feedback
            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez
        # Integrate rate of change of quaternion
        gx *= (0.5 * dt)  # pre-multiply common factors
        gy *= (0.5 * dt)
        gz *= (0.5 * dt)
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)
       
        # Normalise quaternion
        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm

    def sensfusion6GetEulerRPY(self):
        # float gx, gy, gz; estimated gravity direction
        gx = 2 * (self.q1 * self.q3 - self.q0 * self.q2)
        gy = 2 * (self.q0 * self.q1 + self.q2 * self.q3)
        gz = self.q0 * self.q0 - self.q1 * self.q1 - self.q2 * self.q2 + self.q3 * self.q3
        
        if gx > 1: gx = 1
        elif gx < -1: gx = -1
        
        yaw = math.atan2(2 * (self.q0 * self.q3 + self.q1 * self.q2), self.q0 * self.q0 + self.q1 * self.q1 - self.q2 * self.q2 - self.q3 * self.q3) * 180 / math.pi
        pitch = math.asin(gx) * 180 / math.pi  # Pitch seems to be inverted
        roll = math.atan2(gy, gz) * 180 / math.pi
        return roll, pitch, yaw
    
    # Fast inverse square-root
    def invSqrt(self, x):
        return 1 / math.sqrt(x)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    window = QWidget() 
    compass = CompassWidget()    
    layout = QVBoxLayout()
    layout.addWidget(compass)
    window.setLayout(layout)
    
    window.show()
    
    timer = QTimer()
    timer.setSingleShot(False)
    timer.timeout.connect(compass.movefunc)
    timer.start(10)  # 100hz
    
    sys.exit(app.exec_())
