PLANS = {
    "basic": {
        "price_month": 100,
        "limits": {
            "responders": 25,
            "reports_per_month": 1000,
        },
        "features": ["dashboard", "reports", "basic_responders", "map"],
    },
    "pro": {
        "price_month": 250,
        "limits": {
            "responders": 100,
            "reports_per_month": 10000,
        },
        "features": ["dashboard", "reports", "responders", "map", "ai_detection", "smart_assignment", "analytics", "heatmaps", "notifications"],
    },
    "enterprise": {
        "price_month": 1000,
        "limits": {
            # Use extremely high practical limits for enterprise so limits are effectively impossible to reach
            "responders": 999999999,
            "reports_per_month": 999999999,
        },
        "features": ["all"],
    },
}
