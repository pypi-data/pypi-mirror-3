import numpy as np
from visa import GpibInstrument
from time import sleep

class Keithley236(GpibInstrument):
    '''
    Keithley 236 Source Measure Unit
    '''
    def __init__(self, address=22, is_sweeping_delay=.1, *args, **kwargs):
        '''
        Parameters
        --------------
        address : int 
            Gpib address, 22
        is_sleeping_delay : float
            time delay (in ms) to wait between asking if sweep is 
            completeed 
        *args, **kwargs : args, kwargs
            passed to GpibInstrument() initializer
        '''

        GpibInstrument.__init__(self,address,**kwargs)
        self.is_sweeping_delay = is_sweeping_delay
        
    def set_source_function(self, source, function):
        '''
        Parameters
        -----------
        source : 'v', 'i'
            voltage or current source
        function : 'dc' , 'sweep'
            dc or sweep operating function
        '''
        source_dict = {'v':'0','i':'1'}    
        function_dict = {'dc':'0','sweep':'1'}
        
        try: 
            source = source_dict[source.lower()]
            function = function_dict[function.lower()]
        except(KeyError):
            raise ValueError('ERROR: bad values for source and/or function')
        
        
        self.write('F%s,%sX'%(source,function))
    
    def get_source_function(self):
        '''
        '''
        raise (NotImplementedError)
    
    def set_compliance(self, level, range_=0):
        '''
        Parmeters
        ---------
        level : float
            compliance level. valid range is  -100 to +100 mA for 
            I-measure, and -110, to +110V for V-measure
        range_ : int
            compliance/measure range. 0 = Auto, see manual for rest.
        
        '''
        self.write('L%f,%iX'%(level, range_))
        
    def set_trigger_config(self, origin, in_, out, end):
        '''
        Set the trigger configuration. 
        This function takes strings for all arguments, the corresponding
        integers that are sent in the VISA command are given in hard 
        brackets in the comments 
        
        Parameters
        -----------
        origin : string, case in-sensitive
            Input trigger origin:
                'x'     : [0]  IEEE X 
                'get'   : [1]  IEEE GEt
                'talk'  : [2]  IEEE Talk
                'ext'   : [3]  External (TRIGGER IN pulse)
                'imm'   : [4]  Immediate only (manual key or H0X command)
        in_ : string
            Input trigger effect:
                'cont'  : [0] continuous (no trigger needed to continue s-d-m
                '^sdm'  : [1] ^SRC DLY MSR (trigger starts source)
                's^dm'  : [2] SRC^DLY MSR (trigger starts delay)
                '^s^dm' : [3] similar
                'sd^m'  : [4]
                '^sd^m' : [5]
                's^d^m' : [6]
                '^s^d^m'  : [7]
                '^single' : [8] Single Pulse
                
        out : string
            Output trigger generation:
                'none'  : [0] none during sweep
                's^dm'  : [1] (end of source)
                'sd^m'  : [2] (end of delay)
                's^d^m' : [3] 
                'sdm^'  : [4] (end of measure)
                's^dm^' : [5]
                'sd^m^' : [6]
                's^d^m^'    : [7]
                'pulse_end' : [8] Pulse end
        
        end : Boolean
            Sweep End^ trigger out:
                'disable' : [0]
                'enable' : [1]
        '''
        # dictionary's mapping input strings to integer values for 
        # gpib command
        origin_dict = {'x':0,'get':1,'talk':2,'ext':3,'imm':4}
        in_dict = {'cont':0,'^sdm':2,'^s^dm':3,'sd^m':4,'^sd^m':5,
            's^d^m':6,'^s^d^m':7,'^single':8}
        out_dict = {'none':0,'s^dm':1,'sd^m':2,'s^d^m':3,'sdm^':4,
            's^dm^':5,'sd^m^':6,'s^d^m^':7,'pulse_end':8}
        end_dict = {'disable':0,'enable':1}
        
        # lower strings so that its case insenstive
        origin = origin.lower()
        in_ = in_.lower()
        out= out.lower()
        end = end.lower()
        
        # check out input values
        if origin not in origin_dict.keys():
            raise(ValueError('bad value for origin'))
        
        if in_ not in in_dict.keys():
            raise(ValueError('bad value for in_'))
        
        if out not in out_dict.keys():
            raise(ValueError('bad value for out'))
        
        if end not in end_dict.keys():
            raise(ValueError('bad value for end'))
        
        print ('T%i,%i,%i,%iX'%(origin_dict[origin],
            in_dict[in_], out_dict[out], end_dict[end]))    
        # send comand
        self.write('T%i,%i,%i,%iX'%(origin_dict[origin],
            in_dict[in_], out_dict[out], end_dict[end]))
        
    def enable_trigger(self):
        '''
        enable input triggering 
        '''
        self.write('R1X'%value)
    def disable_trigger(self):
        '''
        '''
        self.write('R0X'%value)
    
    def trigger(self):
        '''
        cause immediate trigger
        '''
        self.write('H0X')
    
    def operate(self):
        '''
        '''
        self.write('N1X')
    def standby(self):
        '''
        '''
        self.write('N0X')
            
    def set_voltage(self):
        '''
        '''
        raise(NotImplementedError)
    
    def create_sweep_linear_stair(self, start, stop, step, range_, delay):
        '''
        '''
        self.write('Q1,%f,%f,%f,%f,%fX'%(start, stop, step, range_, 
            delay))
            
        
    
    def reset_factory_defaults(self):
        '''
        Reset to factor defaults
        '''
        self.write('J0X')
    def get_warnings(self):
        '''
        '''
        return self.ask("U9X")#.replace("WRS","")
    
    def get_data(self, items=5, format_=1, lines=2):
        '''
        items is sum of the following
        '''
        data =  np.array( self.ask_for_values('G%i,%i,%iX'%\
            (items, format_, lines)))
        data.shape = (data.size/2,2)
        return data
    
    def is_sweeping(self):
        '''
        '''
        current_point = int(self.ask('U11X')[3:])
        end_point  = int(self.ask('U8X')[3:])
        return (current_point != end_point)
    
    def run_sweep_get_data(self):
        '''
        trigger sweep, wait for it to complete, and return data. 
        '''
        self.operate()
        self.trigger()
        while self.is_sweeping():
            sleep(self.is_sweeping_delay)
        return self.get_data()
        
    def get_errors(self):
        error_dict = {\
            '00000000000000000000000000' : 'None',\
            '10000000000000000000000000' : 'Trigger Overrun',\
            '01000000000000000000000000' : 'IDDC',\
            '00100000000000000000000000' : 'IDDCO',\
            '00010000000000000000000000' : 'Interlock Present',\
            '00001000000000000000000000' : 'Illegal Measure Range',\
            '00000100000000000000000000' : 'Illegal Source Range',\
            '00000010000000000000000000' : 'Invalid Sweep Mix',\
            '00000001000000000000000000' : 'Log Cannot Cross Zero',\
            '00000000100000000000000000' : 'Autoranging Source with Pulse Sweep',\
            '00000000010000000000000000' : 'In Calibration',\
            '00000000001000000000000000' : 'In Standby',\
            '00000000000100000000000000' : 'Unit is a 236',\
            '00000000000010000000000000' : 'IOU DPRAM Failed',\
            '00000000000001000000000000' : 'IOU EEPROM Failed',\
            '00000000000000100000000000' : 'IOU Cal Checksum Error',\
            '00000000000000010000000000' : 'DPRAM Lockup',\
            '00000000000000001000000000' : 'DPRAM Link Error',\
            '00000000000000000100000000' : 'Cal ADC Zero Error',\
            '00000000000000000010000000' : 'Cal ADC Gain Error',\
            '00000000000000000001000000' : 'Cal SRC Zero Error',\
            '00000000000000000000100000' : 'Cal SRC Gain Error',\
            '00000000000000000000010000' : 'Cal Common Mode Error',\
            '00000000000000000000001000' : 'Cal Compliance Error',\
            '00000000000000000000000100' : 'Cal Value Error',\
            '00000000000000000000000010' : 'Cal Constants Error',\
            '00000000000000000000000001' : 'Cal Invalid Error',\
            
            }
        return (error_dict[self.ask("XU1X")[3:]])
'''    
#### Configure Keithly and run sweep ####

print "Initializing Keithly"
# open and clear instruments
keith = visa.instrument("GPIB::"+gpibAddress)
keith.write("J0X")

# depending on bias mode, change sweep operation and set compliance limit.
if biasSource == "I":
        keith.write("F1,1X")
        keith.write("L"+repr(voltageCompliance)+",0")
elif biasSource == "V":
        keith.write("F0,1X")
        keith.write("L"+repr(currentCompliance)+",0")

# set trigger to respond to GPIB HOX commands
keith.write("T4,0,0,1X")
# enable triggers
keith.write("R1X")
# create a linear stair sweep with parameters given above.
keith.write("Q1,"+repr(biasStart)+","+repr(biasStop)+","+repr(biasStep)+","+repr(biasRange)+","+repr(biasDelay)+"X")
# operate on 
keith.write("N1X")

# check for warnings and errors before proceeding. 
warning = int(keith.ask("U9X").replace("WRS",""))
error = int(keith.ask("U1X").replace("ERS",""))
if error != 0:
        print "There is an ERROR code, U1:ERS %i \n You can run again and watch Keithly screen, then go read the manual" % error
        raw_input("Any key will exit")
        exit()
elif warning != 0:
        print "There is a WARNING code, U9:WRS %i \n You can run again and watch Keithly screen, then go read the manual" % warning
        raw_input("Any key will exit")
        exit()

print "Waiting for Keithly"
# trigger the sweep
str1 = keith.ask("U8X").replace("DSS","SMS")
keith.write("H0X")
str2 = "SMS0000"
#Loop until the sweep is done
while(str2!=str1):
        str2 = keith.ask("U11X")
        

###### Get data, plot it, and save it ###

data = keith.ask_for_values("G5,1,2X")
# convert from type list to array 
data = array(data)
# re-shape the array
data.shape = (data.size/2,2)
# plot it
print "Plotting Results"
plot(data[:,0],data[:,1],'o-')
if biasSource == "I":
        xlabel('Current (A)')
        ylabel('Voltage (V)')
elif biasSource == "V":
        xlabel('Voltage (V)')
        ylabel('Current (A)')
title(chartTitle)


### Write output to file ###

# if output file exists delete it.
if os.access(fileOut,1):
	os.remove(fileOut)
fileHandle=open(fileOut,"w")
#write data
if biasSource == "I":
        fileHandle.write("I V\n")
elif biasSource == "V":
        fileHandle.write("V I\n")

save(fileHandle,data)
# close up shop
keith.close()
fileHandle.close()
# show figure and transfer control to GUI
show()
'''
