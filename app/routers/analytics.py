from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app import models, database
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=['Dashboard Analytics'])

@router.get("/dashboard-summary")
def get_dashboard_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Determine scope: Admin sees all, Manager sees their arcade only
    is_admin = current_user.role == "administrator"
    arcade_filter = current_user.arcade_id

    # 1. Total Revenue (Sum of Recharges)
    rev_query = db.query(func.sum(models.RechargeHistory.amount))
    if not is_admin:
        # Join with Card to filter by Manager's Arcade
        rev_query = rev_query.join(models.Card).filter(models.Card.arcade_id == arcade_filter)
    total_revenue = rev_query.scalar() or 0.0

    # 2. Total Transactions (Count of Punches)
    punch_query = db.query(func.count(models.PunchHistory.id))
    if not is_admin:
        punch_query = punch_query.filter(models.PunchHistory.arcade_id == arcade_filter)
    total_punches = punch_query.scalar() or 0

    # 3. Active Players (Unique cards punched in the last 2 hours)
    time_threshold = datetime.now(datetime-timezone) - timedelta(hours=2)
    active_query = db.query(func.count(models.PunchHistory.card_id.distinct())).filter(
        models.PunchHistory.timestamp >= time_threshold
    )
    if not is_admin:
        active_query = active_query.filter(models.PunchHistory.arcade_id == arcade_filter)
    active_players = active_query.scalar() or 0

    return {
        "total_revenue": total_revenue,
        "total_transactions": total_punches,
        "active_players": active_players,
        "system_health": "Optimal"
    }

@router.get("/revenue-trends")
def get_revenue_trends(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch hourly revenue for the current day
    today = datetime.now(timezone.utc).date()
    
    query = db.query(
        func.extract('hour', models.RechargeHistory.timestamp).label('hour'),
        func.sum(models.RechargeHistory.amount).label('revenue')
    ).filter(func.date(models.RechargeHistory.timestamp) == today)

    if current_user.role != "administrator":
        query = query.join(models.Card).filter(models.Card.arcade_id == current_user.arcade_id)

    trends = query.group_by('hour').order_by('hour').all()
    
    # Format for Frontend Charts
    return [{"hour": f"{int(t.hour)}:00", "revenue": t.revenue} for t in trends]