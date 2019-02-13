from __future__ import print_function
import sys
import time
import serial
import math
import matplotlib
import matplotlib.pyplot as plt
import signal


class HighPassFilter(object):

    def __init__(self,fcut=1.0):
        self.fcut = fcut
        self.value = None
        self.xlast = None

    def calc_alpha(self, dt):
         return 1.0/(2.0*math.pi*self.fcut + 1.0)

    def update(self, x, dt):
        if self.value is None:
            self.value = x
            self.xlast = x
        else:
            alpha = self.calc_alpha(dt)
            dx = x - self.xlast
            self.value = alpha*(self.value + dx)
            self.xlast = x
        return self.value


class LivePlot(serial.Serial):

    ResetSleepDt = 0.5
    Baudrate = 115200

    def __init__(self,port='/dev/ttyACM0',timeout=10.0):
        param = {'baudrate': self.Baudrate, 'timeout': timeout}
        super(LivePlot,self).__init__(port,**param)
        time.sleep(self.ResetSleepDt)

        self.use_high_pass = True 
        self.window_size = 10.0
        self.data_file = 'data.txt'

        self.t_init =  time.time()
        self.t_list = []
        self.volt_list = []
        self.filt_volt_list = []
        self.high_pass_filter = HighPassFilter(fcut=0.05)

        self.running = False
        signal.signal(signal.SIGINT, self.sigint_handler)

        plt.ion()
        self.fig = plt.figure(1)
        self.ax = plt.subplot(111) 
        self.line, = plt.plot([0,1], [0,1],'b')
        plt.grid('on')
        plt.xlabel('(sec)')
        plt.ylabel('(V)')
        self.ax.set_xlim(0,self.window_size)
        self.ax.set_ylim(-30,30)
        plt.title("Force Sensor  (Type=AE801)")
        self.line.set_xdata([])
        self.line.set_ydata([])
        self.fig.canvas.flush_events()


    def sigint_handler(self,signum,frame):
        self.running = False

    def run(self):

        self.write('b\n')
        self.running = True

        with open(self.data_file, 'w') as fid:
            while self.running:
                have_data = False
                while self.in_waiting > 0:
                    # Not the best - throwing points away. Maybe put points in list, process later. 
                    line = self.readline()
                    have_data = True
                if have_data:
                    line = line.strip()
                    data = line.split(' ')
                    try:
                        t = float(data[0])
                        volt = float(data[1])
                    except IndexError:
                        continue
                    except ValueError:
                        continue
                    print('{0}, {1}'.format(t,volt))


                    t_elapsed = time.time() - self.t_init
                    self.t_list.append(t_elapsed)

                    if len(self.t_list) < 2:
                        dt = None
                    else:
                        dt = self.t_list[-1] - self.t_list[-2]

                    self.volt_list.append(volt)
                    filt_volt = self.high_pass_filter.update(volt,dt)
                    self.filt_volt_list.append(filt_volt)

                    while (self.t_list[-1] - self.t_list[0]) > self.window_size:
                        self.t_list.pop(0)
                        self.volt_list.pop(0)
                        self.filt_volt_list.pop(0)

                    self.line.set_xdata(self.t_list)
                    if self.use_high_pass:
                        self.line.set_ydata(self.filt_volt_list)
                    else:
                        self.line.set_ydata(self.volt_list)

                    xmin = self.t_list[0]
                    xmax = max(self.window_size, self.t_list[-1])

                    self.ax.set_xlim(xmin,xmax)
                    self.fig.canvas.flush_events()
                    #plt.pause(0.0001)
                    fid.write('{0} {1}\n'.format(t_elapsed, volt))

        print('quiting')
        self.write('\n')



# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) > 1:
        port = sys.argv[1]

    liveplot = LivePlot(port=port)
    liveplot.run()



