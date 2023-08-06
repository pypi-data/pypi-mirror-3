import logging

from plone.indexer.decorator import indexer

from interfaces import IActualHours
from interfaces import IEstimate
from interfaces import ISizeEstimate
from interfaces import IActualHoursContainer
from interfaces import IEstimateContainer

logger = logging.getLogger('xm.booking')


@indexer(IActualHoursContainer)
def actual_container(object):
    adapted = IActualHours(object, None)
    if adapted is not None:
        return adapted.actual_time
    logger.warn("Failed adapting IActualHoursContainer to IActualHours.")
    return None


@indexer(IEstimateContainer)
def duration_estimate_container(object):
    adapted = IEstimate(object, None)
    if adapted is not None:
        return adapted.estimate
    logger.warn("Failed adapting IEstimateContainer to IEstimate.")
    return None


@indexer(IActualHours)
def actual(object):
    return object.actual_time


@indexer(IEstimate)
def duration_estimate(object):
    return object.estimate


@indexer(ISizeEstimate)
def size_estimate(object):
    return object.size_estimate
