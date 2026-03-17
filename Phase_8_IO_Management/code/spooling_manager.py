from Backend.models import PrintQueueJob, db


class SpoolingManager:
    def enqueue(self, job_type, filename, pages, user_id=None):
        job = PrintQueueJob(job_type=job_type, filename=filename, pages=pages, user_id=user_id, status="QUEUED")
        db.session.add(job)
        db.session.commit()
        return job.to_dict()

    def process_next(self):
        job = PrintQueueJob.query.filter_by(status="QUEUED").order_by(PrintQueueJob.submitted_at.asc()).first()
        if not job:
            return {"success": False, "message": "No queued print jobs"}
        job.status = "PRINTED"
        db.session.commit()
        return {"success": True, "job": job.to_dict()}

    def snapshot(self):
        return [job.to_dict() for job in PrintQueueJob.query.order_by(PrintQueueJob.submitted_at.asc()).all()]
