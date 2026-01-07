"""
Analytics API Router.

Provides comprehensive system metrics, performance analytics, and reporting endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from ..database import get_db
from ..auth import get_current_user
from ..auth_models import User
from ..analytics import (
    PerformanceEvaluator,
    CoverageAnalyzer,
    ResponseTimeTracker
)


router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system performance metrics.
    
    Returns:
    - Detection rate (detections/hour)
    - False positive rate
    - Response times (avg, p95)
    - UAV utilization
    - Mission success rate
    """
    try:
        evaluator = PerformanceEvaluator(db)
        
        # Calculate time window
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get metrics from evaluator
        metrics = evaluator.calculate_metrics(start_time, end_time)
        
        return {
            "time_window_hours": hours,
            "detection_rate": round(metrics.detection_rate, 2),
            "false_positive_rate": round(metrics.false_positive_rate, 2),
            "response_time_avg": round(metrics.response_time_avg, 2),
            "response_time_p95": round(metrics.response_time_p95, 2),
            "coverage_percentage": round(metrics.coverage_percentage, 2),
            "uav_utilization": round(metrics.uav_utilization, 2),
            "mission_success_rate": round(metrics.mission_success_rate, 2),
            "total_missions": metrics.total_missions,
            "total_detections": metrics.total_detections,
            "total_alerts": metrics.total_alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")


@router.get("/coverage", response_model=Dict[str, Any])
async def get_coverage_metrics(
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get coverage analysis metrics.
    """
    try:
        analyzer = CoverageAnalyzer(db)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        coverage = analyzer.calculate_coverage(start_time, end_time)
        
        return {
            "time_window_hours": hours,
            "total_area_km2": round(coverage.total_area_km2, 2),
            "covered_area_km2": round(coverage.covered_area_km2, 2),
            "coverage_percentage": round(coverage.coverage_percentage, 2),
            "overlap_percentage": round(coverage.overlap_percentage, 2),
            "coverage_gaps": len(coverage.gaps),
            "coverage_by_zone": coverage.coverage_by_zone
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating coverage: {str(e)}")


@router.get("/response-time", response_model=Dict[str, Any])
async def get_response_time_metrics(
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get response time analysis.
    """
    try:
        tracker = ResponseTimeTracker(db)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        response_metrics = tracker.calculate_response_times(start_time, end_time)
        
        return {
            "time_window_hours": hours,
            "alert_to_assignment": round(response_metrics.alert_to_assignment, 2),
            "assignment_to_launch": round(response_metrics.assignment_to_launch, 2),
            "launch_to_arrival": round(response_metrics.launch_to_arrival, 2),
            "total_response_time": round(response_metrics.total_response_time, 2),
            "response_time_by_priority": response_metrics.response_time_by_priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating response times: {str(e)}")


@router.get("/uav/{uav_id}/performance", response_model=Dict[str, Any])
async def get_uav_performance(
    uav_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance metrics for a specific UAV.
    """
    try:
        evaluator = PerformanceEvaluator(db)
        performance = evaluator.get_uav_performance(uav_id)
        
        if not performance:
            raise HTTPException(status_code=404, detail=f"UAV {uav_id} not found")
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating UAV performance: {str(e)}")


@router.get("/trends", response_model=Dict[str, Any])
async def get_trends(
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    interval_hours: int = Query(1, ge=1, le=24, description="Trend interval in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical trend analysis.
    """
    try:
        evaluator = PerformanceEvaluator(db)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        trends = evaluator.get_detection_trends(start_time, end_time, interval_hours)
        
        return {
            "time_window_hours": hours,
            "interval_hours": interval_hours,
            "data_points": len(trends),
            "trends": trends
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating trends: {str(e)}")
