'''
Visualizations for simple types. All classes in this package have at least one
object instancialized as the Class.default attribute. Some classes may contain
additional attributes holding instances that were initialized with different
arguments.  

1) Datetime
'''

from tutor.visualization.base import Visualization
import datetime

class Datetime(Visualization):
    default = None

    def render(self, obj):
        dt = datetime.datetime(**obj)
        return str(dt)
Datetime.default = Datetime()
