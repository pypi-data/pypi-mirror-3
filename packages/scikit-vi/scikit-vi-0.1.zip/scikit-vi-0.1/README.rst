
Scikit for Virtual Instruments
===================================

scikit-vi (aka skvi) is a scikit which provides virtual instrument objects. 
The goal of this project is to provide a centralized repository for virtual 
instruments written in python.


Examples
--------------
here is an example::

	from skvi.source_meter import Keithley236
	keith236 = Keithley236()
	keith236.set_source_function(source='v', function='sweep')
	keith236.set_compliance(level=10)
