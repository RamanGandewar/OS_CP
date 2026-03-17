from flask import Blueprint, jsonify, request

from Phase_5_Synchronization.code.mutex_manager import MutexManager, SYNC_MONITOR
from Phase_5_Synchronization.code.producer_consumer import ProducerConsumerBuffer
from Phase_5_Synchronization.code.race_condition_demo import RaceConditionDemo
from Phase_5_Synchronization.code.reader_writer_lock import ReaderWriterLock
from Phase_5_Synchronization.code.semaphore_manager import SemaphoreManager

sync_bp = Blueprint("sync", __name__)
mutex_manager = MutexManager()
semaphore_manager = SemaphoreManager()
reader_writer_lock = ReaderWriterLock()
producer_consumer = ProducerConsumerBuffer(size=50)
race_demo = RaceConditionDemo()


@sync_bp.route("/monitor", methods=["GET"])
def monitor():
    return jsonify(SYNC_MONITOR.get_monitor_payload())


@sync_bp.route("/quotation-edit", methods=["POST"])
def quotation_edit():
    payload = request.get_json() or {}
    result = mutex_manager.edit_quotation(
        quotation_id=payload["quotation_id"],
        user_id=payload["user_id"],
        data=payload.get("data", {}),
    )
    return jsonify(result)


@sync_bp.route("/inventory/reserve", methods=["POST"])
def reserve_inventory():
    payload = request.get_json() or {}
    return jsonify(
        semaphore_manager.reserve_inventory(
            product_id=payload.get("product_id", "PRODUCT_X"),
            user_id=payload.get("user_id"),
            units=int(payload.get("units", 1)),
        )
    )


@sync_bp.route("/report/read", methods=["POST"])
def report_read():
    payload = request.get_json() or {}
    result = reader_writer_lock.acquire_read(payload.get("user_id"), payload.get("report_id", "sales-report"))
    reader_writer_lock.release_read(payload.get("user_id"), payload.get("report_id", "sales-report"))
    return jsonify(result)


@sync_bp.route("/report/write", methods=["POST"])
def report_write():
    payload = request.get_json() or {}
    result = reader_writer_lock.acquire_write(payload.get("user_id"), payload.get("report_id", "sales-report"))
    reader_writer_lock.release_write(payload.get("user_id"), payload.get("report_id", "sales-report"))
    return jsonify(result)


@sync_bp.route("/producer", methods=["POST"])
def producer():
    payload = request.get_json() or {}
    return jsonify(producer_consumer.produce(payload.get("enquiry", "new-enquiry")))


@sync_bp.route("/consumer", methods=["POST"])
def consumer():
    return jsonify(producer_consumer.consume())


@sync_bp.route("/race-demo", methods=["GET"])
def race_condition():
    return jsonify(
        {
            "before_fix": race_demo.run_unsynchronized(iterations=2000),
            "after_fix": race_demo.run_synchronized(iterations=2000),
        }
    )
