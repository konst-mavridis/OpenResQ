import logging

logger = logging.getLogger(__name__)

class TrustService:
    """
    Διαχειρίζεται το trust score των χρηστών.
    """
    
    BASE_SCORE = 0.5
    MIN_SCORE = 0.0
    MAX_SCORE = 1.0

    def __init__(self, db):
        """
        db: αντικείμενο για πρόσβαση στη βάση χρηστών (π.χ. Firebase ή SQLAlchemy)
        """
        self.db = db

    def get_trust(self, user_id: str) -> float:
        """Επιστρέφει το τρέχον trust score του χρήστη."""
        user = self.db.get_user(user_id)
        if not user:
            return self.BASE_SCORE
        return user.get("trust_score", self.BASE_SCORE)

    def update_trust(
        self,
        user_id: str,
        delta: float,
        reason: str = ""
    ) -> float:
        """
        Προσθέτει/αφαιρεί trust score.
        delta: +0.1/-0.2 κτλ
        """
        user = self.db.get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found, creating with base trust")
            user = {"uid": user_id, "trust_score": self.BASE_SCORE}
            self.db.create_user(user)

        new_score = max(self.MIN_SCORE, min(self.MAX_SCORE, user["trust_score"] + delta))
        self.db.update_user(user_id, {"trust_score": new_score})

        logger.info(f"[TrustService] User {user_id} trust updated: {user['trust_score']} -> {new_score} ({reason})")
        return new_score

    # =========================
    # Helpers for reports
    # =========================
    def apply_report_feedback(self, user_id: str, report_verified: bool, ai_confidence: float = 0.0):
        """
        Ενημερώνει το trust score με βάση feedback:
        - report_verified: True αν το report ήταν σωστό
        - ai_confidence: 0.0 - 1.0, AI ανίχνευση συμβατή με report
        """
        delta = 0.0
        if report_verified:
            delta += 0.05 + 0.1 * ai_confidence
        else:
            delta -= 0.1  # ψευδές report
        self.update_trust(user_id, delta, reason=f"Report verified={report_verified}, AI={ai_confidence}")

    def can_submit(self, user_id: str, event_type: str) -> bool:
        """
        Ελέγχει αν ο χρήστης μπορεί να στείλει συγκεκριμένο τύπο report
        """
        trust = self.get_trust(user_id)
        if event_type == "fire" and trust < 0.2:
            return False
        if trust < 0.1:
            return False
        return True

