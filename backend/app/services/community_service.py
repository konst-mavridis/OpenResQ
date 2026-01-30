from app.firebase_config import get_db
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

class CommunityService:
    def __init__(self):
        self.db = get_db()

    def vote_report(self, report_id: str, voter_id: str, vote: int):
        """
        vote = 1  -> upvote
        vote = -1 -> downvote
        """

        if vote not in [1, -1]:
            raise ValueError("Vote must be 1 or -1")

        report_ref = self.db.collection("reports").document(report_id)
        user_ref = self.db.collection("users").document(voter_id)

        voter = user_ref.get().to_dict()
        if not voter:
            raise ValueError("Voter not found")

        voter_trust = voter.get("trust_score", 0.5)

        def transaction_update(transaction, report_ref, voter_id, vote, voter_trust):
            report_snapshot = report_ref.get(transaction=transaction)
            report = report_snapshot.to_dict()
            if not report:
                raise ValueError("Report not found")

            votes = report.get("votes", {})

            # 🔹 Καταχώρηση ψήφου με trust και timestamp
            votes[voter_id] = {
                "vote": vote,
                "trust": voter_trust,
                "timestamp": datetime.utcnow().timestamp()
            }

            # Υπολογισμός νέας confidence
            total_weight = sum(v["trust"] for v in votes.values()) or 0.001
            total_score = sum(v["vote"] * v["trust"] for v in votes.values())
            confidence = (total_score / total_weight + 1) / 2  # 0..1

            # Λογική status
            new_status = "pending"
            needs_admin = False
            if confidence >= 0.8:
                new_status = "community_verified"
            elif confidence < 0.2:
                new_status = "admin_review"
                needs_admin = True

            logging.info(f"[Vote] report {report_id} new confidence: {confidence:.2f}, status: {new_status}")

            transaction.update(report_ref, {
                "votes": votes,
                "confidence": confidence,
                "status": new_status,
                "needs_admin_review": needs_admin,
                "updated_at": datetime.utcnow()
            })

            # Ενημέρωση trust του creator
            creator_id = report["uid"]
            creator_ref = self.db.collection("users").document(creator_id)
            creator_snapshot = creator_ref.get(transaction=transaction)
            creator = creator_snapshot.to_dict()
            old_trust = creator.get("trust_score", 0.5)
            new_trust = max(0, min(1, old_trust + vote * voter_trust * 0.05))
            transaction.update(creator_ref, {
                "trust_score": new_trust,
                "updated_at": datetime.utcnow()
            })
            logging.info(f"[Vote] creator {creator_id} trust updated: {old_trust:.2f} -> {new_trust:.2f}")

        # 🔹 Εκτέλεση transaction
        self.db.transaction()(transaction_update)(report_ref, voter_id, vote, voter_trust)

        return {"status": "ok", "your_vote": vote, "voter_trust": voter_trust}

