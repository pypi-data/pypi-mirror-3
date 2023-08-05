from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from horae.planning import interfaces


class PositionChangedEvent(ObjectEvent):
    """ The position of an object has been changed
    """
    implements(interfaces.IPositionChangedEvent)


class EstimatedExecutionRecalculated(ObjectEvent):
    """ The estimated execution of an object has been recalculated
    """
    implements(interfaces.IEstimatedExecutionRecalculated)


class ForecastRecalculated(ObjectEvent):
    """ The forecast of an object has been recalculated
    """
    implements(interfaces.IForecastRecalculated)
