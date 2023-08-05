""" This package can be used to drive the Thorlabs MDT693A piezo controller


Example :
import PyMDT
pzt = PyMDT.PZT_driver'port='COM2'
pzt.x = 45 # set the x-axis to 45 V
pzt.set_x(45) #equivalent to the command above 
print pzt.x # Display the value of the x-axis
pzt.get_info() #Display the informations about the device
"""

import serial
import sys
import re

if sys.platform.startswith('win'):
    DEFAULT_PORT = 'COM2'
else:
    DEFAULT_PORT = '/dev/ttyUSB0'



class PZT_driver(serial.Serial):
    def __init__(self, port=DEFAULT_PORT, baudrate=115200):
        serial.Serial.__init__(self,port, baudrate, timeout=0.1)

    
    def set_value(self, cmd, val):
        self.write('%s%f\r'%(cmd,val))
        
    def mon_readline(self):
        """ Reads a line which finish by '/r' or until time out"""
        a=self.read()
        if a=='':
            return ''
        while a[-1]!='\r':
            s=self.read()
            a=a+s
            if s=='':
                break
        return a

    def read_txt(self, cmd):
        """Send a command, and return the output of the command as a string"""
        self.write(cmd+'\r')
        s = self.mon_readline()
        a1 = re.search('\[(.*)\]',s)
        a2 = re.search('\*([0-9\.]+\Z)',s)
        while a1 is None and a2 is None and s!='':
            s = self.mon_readline()
            a1 = re.search('\[(.*)\]',s)
            a2 = re.search('\*([0-9\.]+\Z)',s)
        if a1 is not None:
            return a1.group(1)
        elif a2 is not None:
            return a2.group(1)
        else:
            raise Exception('No information return from command %s'%(cmd))
    
    def read_float(self, cmd):
        """Send a command, and return the result as a float"""
        s = self.read_txt(cmd)
        return float(s)

    def get_x(self):
        """Reads and returns the x axis output voltage"""
        return self.read_float('xr?')

    def get_y(self):
        """Reads and returns the y axis output voltage"""
        return self.read_float('yr?')

    def get_z(self):
        """Reads and returns the z axis output voltage"""
        return self.read_float('zr?')

    def set_all(self, val):
        """Sets all outputs to the set voltage"""
        self.set_value('AV', val)

    def set_x(self, val):
        """Sets the output voltage for the x axis"""
        self.set_value('XV', val)

    def set_y(self, val):
        """Sets the output voltage for the y axis"""
        self.set_value('YV', val)

    def set_z(self, val):
        """Sets the output voltage for the z axis"""
        self.set_value('ZV', val)

    def set_zeros(self):
        """ Sets all outputs to zero"""
        self.set_all(0)
    
    @property
    def max_out(self):
        """returns the output voltage limit setting"""
        return self.read_float('%\r')

    def get_info(self):
        """Return the product header, firmware version, etc."""
        self.write('i\r')
        return self.readlines()[0].replace('\r','\n')
    
    def set_x_min(self, val):
        """Sets the minimum output voltage limit for the x axis"""
        self.set_value('XL',val)
        
    def set_y_min(self, val):
        """Sets the minimum output voltage limit for the y axis"""
        self.set_value('YL',val)   
        
    def set_z_min(self, val):
        """Sets the minimum output voltage limit for the z axis"""
        self.set_value('ZL',val)  
 
    def get_x_min(self):
        """Return the minimum output voltage limit for the x axis"""
        return self.read_float('xl?')

    def get_y_min(self):
        """Return the minimum output voltage limit for the y axis"""
        return self.read_float('yl?')   
   
    def get_z_min(self):
        """Return the minimum output voltage limit for the z axis"""
        return self.read_float('zl?') 

    def set_x_max(self, val):
        """Sets the maximum output voltage limit for the x axis"""
        self.set_value('xh',val)
        
    def set_y_max(self, val):
        """Sets the maximum output voltage limit for the y axis"""
        self.set_value('yh',val)   
        
    def set_z_max(self, val):
        """Sets the maximum output voltage limit for the z axis"""
        self.set_value('zh',val)
        
    def get_x_max(self):
        """Return the maximum output voltage limit for the x axis"""
        return self.read_float('xh?')

    def get_y_max(self):
        """Return the maximum output voltage limit for the y axis"""
        return self.read_float('yh?')   
   
    def get_z_max(self):
        """Return the maximum output voltage limit for the z axis"""
        return self.read_float('zh?') 


    x = property(get_x, set_x)
    y = property(get_y, set_y)
    z = property(get_z, set_z)
    
    all = property(lambda self:None, set_all)

    x_min = property(get_x_min, set_x_min)
    y_min = property(get_y_min, set_y_min)
    z_min = property(get_z_min, set_z_min)
    
    x_max = property(get_x_max, set_x_max)
    y_max = property(get_y_max, set_y_max)
    z_max = property(get_z_max, set_z_max)
    

    def __del__(self):
        # close the serial port before deleting the object
        self.close()
 
 
 
     
        
        
if __name__=='__main__':
    pzt = PZT_driver()
    print '----INFO----'
    print pzt.get_info()
    print pzt.read_txt('xr?')
    print pzt.get_x()

