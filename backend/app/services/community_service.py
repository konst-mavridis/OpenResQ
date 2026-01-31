from app.firebase_config import get_db
from datetime import datetime
import hashlib
from app.utils.geo import haversine_distance_km

class CommunityService:
    def __init__(self):
        self.db = get_db()

    # ------------------------------

    def vote_report(
        self,
        report_id: str,
        voter_id: str,
        vote: int,
        ip_address: str,
        device_fp: str,
        lat: float,
        lng: float,
    ):
        if vote not in [1, -1]:
            raise Exception("Invalid vote value")

        report_ref = self.db.collection("reports").document(report_id)
        report = report_ref.get().to_dict()
        if not report:
            raise Exception("Report not found")

        # 📍 GEO CHECK
        report_lat = report.get("lat")
        report_lng = report.get("lng")
        
        distance_weight = 1.0  # default weight
        
        if report_lat is not None and report_lng is not None:
            distance_km = haversine_distance_km(
                lat,
                lng,
                report_lat,
                report_lng,
            )
            distance = distance_km * 1000  # convert to meters

            if distance > 300:
                raise Exception("You must be within 300 meters of the incident to vote")
            
            # 🧠 vote weight (πιο κοντά = πιο δυνατό)
            distance_weight = max(0.2, 1 - (distance / 300))
        else:
            distance = 0

        votes = report.get("votes", {})
        existing = votes.get(voter_id)

        voter_ref = self.db.collection("users").document(voter_id)
        voter = voter_ref.get().to_dict() or {}
        voter_trust = voter.get("trust_score", 0.5)

        creator_id = report["uid"]

        # 🚫 HARD BLOCK ίδιας ψήφου
        if existing is not None:
            existing_vote = existing["vote"] if isinstance(existing, dict) else existing
            if existing_vote == vote:
                raise Exception("You have already cast this vote")

        # 🤖 ANTI-BOT: ίδιο IP + FP από άλλο UID
        for uid, data in votes.items():
            if uid != voter_id and isinstance(data, dict):
                if data.get("ip") == ip_address and data.get("fp") == device_fp:
                    raise Exception("Bot-like behavior detected")

        # 🧠 Trust decay αν αλλάζει IP
        if existing and isinstance(existing, dict) and existing.get("ip") != ip_address:
            self.decay_voter_trust(voter_id, heavy=True)

        # 🔁 Save vote
        report_ref.update({
            f"votes.{voter_id}": {
                "vote": vote,
                "weight": distance_weight,
                "ip": ip_address,
                "fp": device_fp,
                "lat": lat,
                "lng": lng,
                "distance": round(distance, 1),
                "updated_at": datetime.utcnow(),
            },
            "updated_at": datetime.utcnow()
        })

        # 🧠 Trust decay αν αλλάζει ψήφο
        if existing:
            self.decay_voter_trust(voter_id)

        # 📊 Recalculate stats (πρέπει να λαμβάνει υπόψη weight)
        stats = self.recalculate_confidence(report_id)

        # 🧠 Update creator trust (μόνο 1η ψήφος)
        if not existing:
            self.update_creator_trust(
                creator_id,
                vote * voter_trust * distance_weight
            )

        return {
            "status": "ok",
            "your_vote": vote,
            "distance_m": round(distance, 1),
            **stats
        }


    # ------------------------------

    def recalculate_confidence(self, report_id):
        report_ref = self.db.collection("reports").document(report_id)
        report = report_ref.get().to_dict()
        votes = report.get("votes", {})

        upvotes = downvotes = 0
        total_weight = weighted_score = 0

        for uid, data in votes.items():
            # Handle both dict format and legacy int format
            if isinstance(data, dict):
                vote = data.get("vote")
            else:
                vote = data
            
            if vote is None:
                continue
                
            user = self.db.collection("users").document(uid).get().to_dict() or {}
            trust = user.get("trust_score", 0.5)

            total_weight += trust
            weighted_score += vote * trust

            if vote == 1:
                upvotes += 1
            else:
                downvotes += 1

        confidence = 0.5 if total_weight == 0 else (weighted_score / total_weight + 1) / 2

        status = "pending"
        needs_admin = False
        if confidence >= 0.8:
            status = "community_verified"
        elif confidence <= 0.2:
            status = "admin_review"
            needs_admin = True

        report_ref.update({
            "confidence": confidence,
            "status": status,
            "needs_admin_review": needs_admin,
            "votes_up": upvotes,
            "votes_down": downvotes,
            "updated_at": datetime.utcnow()
        })

        return {
            "upvotes": upvotes,
            "downvotes": downvotes,
            "confidence": round(confidence, 3)
        }

    # ------------------------------

    def update_creator_trust(self, creator_id, impact):
        ref = self.db.collection("users").document(creator_id)
        user = ref.get().to_dict() or {}

        trust = user.get("trust_score", 0.5)
        trust = max(0, min(1, trust + impact * 0.05))

        ref.update({"trust_score": trust, "updated_at": datetime.utcnow()})

    # ------------------------------

    def decay_voter_trust(self, voter_id, heavy=False):
        ref = self.db.collection("users").document(voter_id)
        user = ref.get().to_dict() or {}

        trust = user.get("trust_score", 0.5)
        decay = 0.05 if heavy else 0.02
        trust = max(0, trust - decay)

        ref.update({"trust_score": trust, "updated_at": datetime.utcnow()})
