from __future__ import print_function
import sys
import time
import serial
import matplotlib
import matplotlib.pyplot as plt
import signal


class LivePlot(serial.Serial):

    ResetSleepDt = 0.5
    Baudrate = 115200

    def __init__(self,port='/dev/ttyACM0',timeout=10.0):
        param = {'baudrate': self.Baudrate, 'timeout': timeout}
        super(LivePlot,self).__init__(port,**param)
        time.sleep(self.ResetSleepDt)


        self.window_size = 10.0
        self.data_file = 'data.txt'

        self.t_init =  time.time()
        self.t_list = []
        self.line_list = []

        self.running = False
        signal.signal(signal.SIGINT, self.sigint_handler)

        plt.ion()
        self.fig = plt.figure(1)
        self.ax = plt.subplot(111) 
        self.line, = plt.plot([0,1], [0,1],'b')
        plt.grid('on')
        plt.xlabel('t (sec)')
        plt.ylabel('angle (deg)')
        self.ax.set_xlim(0,self.window_size)
        self.ax.set_ylim(-2.1,2.1)
        plt.title("Load Cell (20g FSR)")
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
                        t = data[0]
                        val = data[1]
                    except IndexError:
                        continue
                    except ValueError:
                        continue
                    print('{0}, {1}'.format(t,val))


                    t_elapsed = time.time() - self.t_init
                    self.t_list.append(t_elapsed)
                    self.line_list.append(val)

                    while (self.t_list[-1] - self.t_list[0]) > self.window_size:
                        self.t_list.pop(0)
                        self.line_list.pop(0)

                    self.line.set_xdata(self.t_list)
                    self.line.set_ydata(self.line_list)

                    xmin = self.t_list[0]
                    xmax = max(self.window_size, self.t_list[-1])

                    self.ax.set_xlim(xmin,xmax)
                    self.fig.canvas.flush_events()
                    #plt.pause(0.0001)
                    fid.write('{0} {1}\n'.format(t_elapsed, val))

        print('quiting')
        self.write('\n')



# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) > 1:
        port = sys.argv[1]

    liveplot = LivePlot(port=port)
    liveplot.run()



