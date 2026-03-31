import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app import app
from Backend.models import (
    CacheStat,
    Customer,
    DeadlockEvent,
    DiskRequest,
    Enquiry,
    Invoice,
    LockQueueEntry,
    LockRecord,
    MemoryPage,
    PrintQueueJob,
    ProcessLog,
    ProcessRecord,
    Quotation,
    ResourceAllocationRecord,
    ResourceRecord,
    SalesOrder,
    TaskRecord,
    ThreadRecord,
    User,
    db,
)


def reset_database():
    db.drop_all()
    db.create_all()


def seed_users():
    users_data = [
        ("user1", "admin@salescrm.local", "admin"),
        ("user2", "nisha@salescrm.local", "sales"),
        ("user3", "arjun@salescrm.local", "sales"),
        ("user4", "fatima@salescrm.local", "manager"),
        ("user5", "rahul@salescrm.local", "sales"),
    ]
    users = []
    for username, email, role in users_data:
        user = User(username=username, email=email, role=role)
        user.set_password("password123")
        db.session.add(user)
        users.append(user)
    db.session.flush()
    return users


def seed_customers():
    customers_data = [
        ("Aarav Mehta", "aarav.mehta@meghainfra.com", "9876500011", "Megha Infra", "14 Residency Road, Bengaluru"),
        ("Nisha Kapoor", "nisha.kapoor@bluewavefoods.com", "9876500012", "BlueWave Foods", "88 Link Avenue, Mumbai"),
        ("Daniel Thomas", "daniel.thomas@northstarlogistics.com", "9876500013", "NorthStar Logistics", "27 Harbor Point, Chennai"),
        ("Fatima Sheikh", "fatima.sheikh@verdetextiles.com", "9876500014", "Verde Textiles", "5 Green Park, Surat"),
        ("Rahul Iyer", "rahul.iyer@solaredgeworks.com", "9876500015", "Solar Edge Works", "109 Lake View, Hyderabad"),
    ]
    customers = []
    for name, email, phone, company, address in customers_data:
        customer = Customer(name=name, email=email, phone=phone, company=company, address=address)
        db.session.add(customer)
        customers.append(customer)
    db.session.flush()
    return customers


def seed_enquiries(customers, users):
    statuses = ["New", "In Progress", "Closed", "New", "In Progress", "Closed", "New", "In Progress"]
    products = [
        "Industrial Pump",
        "Cold Storage Unit",
        "Fleet Tracking Suite",
        "Textile Packaging Line",
        "Solar Inverter Rack",
        "Warehouse Scanner Kit",
        "CRM Analytics Add-on",
        "Automated Billing Kiosk",
    ]
    enquiries = []
    for index, status in enumerate(statuses, start=1):
        enquiry = Enquiry(
            customer_id=customers[(index - 1) % len(customers)].id,
            product=products[index - 1],
            description=f"Customer requested pricing, implementation timeline, and support coverage for {products[index - 1]}.",
            status=status,
            assigned_to=users[index % len(users)].id,
            created_at=datetime.utcnow() - timedelta(days=12 - index, hours=index),
        )
        db.session.add(enquiry)
        enquiries.append(enquiry)
    db.session.flush()
    return enquiries


def seed_quotations(enquiries):
    quotation_statuses = ["Draft", "Sent", "Approved", "Draft", "Approved", "Sent"]
    quotations = []
    for index, status in enumerate(quotation_statuses, start=1):
        quotation = Quotation(
            enquiry_id=enquiries[index - 1].id,
            quotation_number=f"QT-2026-{index:03d}",
            amount=18500 + (index * 4250),
            valid_until=date.today() + timedelta(days=12 + index),
            status=status,
            created_at=datetime.utcnow() - timedelta(days=9 - index),
        )
        db.session.add(quotation)
        quotations.append(quotation)
    db.session.flush()
    return quotations


def seed_orders_and_invoices(quotations):
    approved_or_sent = [quotation for quotation in quotations if quotation.status in {"Approved", "Sent"}]
    orders = []
    invoices = []
    order_statuses = ["Created", "Processing", "Packed", "Dispatched"]
    payment_statuses = ["Pending", "Paid", "Pending", "Paid"]

    for index in range(4):
        order = SalesOrder(
            quotation_id=approved_or_sent[index].id,
            order_number=f"SO-2026-{index + 1:03d}",
            order_date=date.today() - timedelta(days=6 - index),
            delivery_date=date.today() + timedelta(days=5 + index),
            status=order_statuses[index],
        )
        db.session.add(order)
        orders.append(order)

    db.session.flush()

    for index, order in enumerate(orders, start=1):
        invoice = Invoice(
            sales_order_id=order.id,
            invoice_number=f"INV-2026-{index:03d}",
            amount=22400 + (index * 5100),
            due_date=date.today() + timedelta(days=7 + index),
            payment_status=payment_statuses[index - 1],
        )
        db.session.add(invoice)
        invoices.append(invoice)

    db.session.flush()
    return orders, invoices


def seed_processes(users):
    processes = []
    process_states = ["RUNNING", "READY", "WAITING", "RUNNING", "TERMINATED", "READY", "WAITING", "TERMINATED", "RUNNING", "READY"]
    task_types = ["session", "report", "quotation_pdf", "email", "session", "sync", "validation", "report", "session", "invoice"]
    operations = [
        "dashboard-session",
        "monthly-sales-report",
        "quotation-pdf",
        "email-notification",
        "customer-session",
        "data-sync",
        "background-validation",
        "quarterly-report",
        "manager-session",
        "invoice-generation",
    ]
    for index, state in enumerate(process_states, start=1):
        created_at = datetime.utcnow() - timedelta(minutes=65 - (index * 4))
        terminated_at = created_at + timedelta(minutes=10 + index) if state == "TERMINATED" else None
        process = ProcessRecord(
            pid=3200 + index,
            user_id=users[(index - 1) % len(users)].id,
            state=state,
            priority=((index - 1) % 5) + 1,
            cpu_time=round(1.8 + (index * 0.67), 2),
            created_at=created_at,
            terminated_at=terminated_at,
            parent_pid=3000 if index <= 3 else 3200 + max(1, index - 3),
            task_type=task_types[index - 1],
            operation=operations[index - 1],
        )
        db.session.add(process)
        processes.append(process)

        previous_state = "NEW" if state != "TERMINATED" else "RUNNING"
        db.session.add(
            ProcessLog(
                pid=process.pid,
                previous_state=previous_state,
                new_state=state,
                message=f"Process {process.pid} moved to {state} while handling {process.operation}.",
                logged_at=created_at + timedelta(seconds=45),
            )
        )
    db.session.flush()
    return processes


def seed_tasks(users):
    task_types = ["REPORT", "EMAIL", "PDF", "NOTIFICATION"]
    algorithms = ["FCFS", "SJF", "PRIORITY", "RR"]
    statuses = ["PENDING", "RUNNING", "COMPLETED", "PENDING", "COMPLETED"]
    tasks = []

    for index in range(1, 41):
        status = statuses[(index - 1) % len(statuses)]
        burst_time = (index % 7) + 2
        arrival = datetime.utcnow() - timedelta(minutes=110 - index)
        completion_time = arrival + timedelta(seconds=burst_time + (index % 5) + 2) if status == "COMPLETED" else None
        waiting_time = round((index % 4) + 0.5, 2) if status == "COMPLETED" else round((index % 3) + 0.25, 2)
        turnaround_time = round(waiting_time + burst_time, 2) if status == "COMPLETED" else None
        response_time = round(waiting_time / 2, 2) if status == "COMPLETED" else round(waiting_time / 3, 2)
        remaining_time = 0 if status == "COMPLETED" else max(1, burst_time - (index % 2))
        task = TaskRecord(
            task_id=f"TASK-DEMO-{index:03d}",
            task_type=task_types[(index - 1) % len(task_types)],
            burst_time=burst_time,
            priority=((index - 1) % 10) + 1,
            arrival_time=arrival,
            completion_time=completion_time,
            waiting_time=waiting_time,
            turnaround_time=turnaround_time,
            response_time=response_time,
            status=status,
            algorithm_used=algorithms[(index - 1) % len(algorithms)],
            requested_by=users[(index - 1) % len(users)].id,
            remaining_time=remaining_time,
            operation=f"demo-operation-{index:03d}",
        )
        db.session.add(task)
        tasks.append(task)
    db.session.flush()
    return tasks


def seed_threads():
    thread_specs = [
        ("daemon-notification", "DAEMON", "RUNNING"),
        ("daemon-sync", "DAEMON", "RUNNING"),
        ("session-timeout", "TIMER", "RUNNING"),
        ("autosave-101", "TIMER", "READY"),
        ("autosave-102", "TIMER", "READY"),
        ("worker-report-01", "WORKER", "RUNNING"),
        ("worker-report-02", "WORKER", "READY"),
        ("worker-sync-01", "WORKER", "COMPLETED"),
        ("worker-sync-02", "WORKER", "FAILED"),
        ("worker-validate-01", "WORKER", "RUNNING"),
        ("worker-validate-02", "WORKER", "READY"),
        ("main-ui-thread", "MAIN", "RUNNING"),
        ("daemon-cache-refresh", "DAEMON", "RUNNING"),
        ("timer-report-poller", "TIMER", "READY"),
        ("worker-export-01", "WORKER", "COMPLETED"),
    ]
    for index, (name, thread_type, status) in enumerate(thread_specs, start=1):
        created_at = datetime.utcnow() - timedelta(minutes=45 - index)
        terminated_at = created_at + timedelta(minutes=4 + index) if status in {"COMPLETED", "FAILED"} else None
        db.session.add(
            ThreadRecord(
                thread_id=f"thr-demo-{index:03d}",
                thread_name=name,
                thread_type=thread_type,
                status=status,
                created_at=created_at,
                cpu_time=round(0.8 + (index * 0.33), 2),
                memory_used=round(14 + (index * 1.7), 2),
                terminated_at=terminated_at,
            )
        )


def seed_sync(users, processes):
    lock_entries = [
        LockRecord(
            resource_type="quotation",
            resource_id="123",
            holder_user_id=users[0].id,
            holder_process_id=processes[0].pid,
            acquired_at=datetime.utcnow() - timedelta(minutes=8),
            lock_type="MUTEX",
            status="ACTIVE",
        ),
        LockRecord(
            resource_type="report",
            resource_id="monthly-sales",
            holder_user_id=users[3].id,
            holder_process_id=processes[3].pid,
            acquired_at=datetime.utcnow() - timedelta(minutes=13),
            lock_type="WRITER",
            status="ACTIVE",
        ),
    ]
    queue_entries = [
        LockQueueEntry(
            resource_type="quotation",
            resource_id="123",
            waiting_user_id=users[1].id,
            requested_at=datetime.utcnow() - timedelta(minutes=7),
            status="WAITING",
            requested_lock_type="MUTEX",
        ),
        LockQueueEntry(
            resource_type="report",
            resource_id="monthly-sales",
            waiting_user_id=users[4].id,
            requested_at=datetime.utcnow() - timedelta(minutes=5),
            status="WAITING",
            requested_lock_type="READER",
        ),
    ]
    db.session.add_all(lock_entries + queue_entries)


def seed_deadlock():
    resources = [
        ResourceRecord(resource_name="DB_CONN", resource_type="Database", total_instances=10, available_instances=4),
        ResourceRecord(resource_name="REPORT_GEN", resource_type="Report", total_instances=3, available_instances=1),
        ResourceRecord(resource_name="EMAIL_SENDER", resource_type="Email", total_instances=5, available_instances=3),
        ResourceRecord(resource_name="PDF_CREATOR", resource_type="Document", total_instances=2, available_instances=0),
    ]
    db.session.add_all(resources)
    db.session.flush()

    allocations = [
        ResourceAllocationRecord(process_id="P1", resource_id=resources[0].id, allocated_count=2, requested_count=1),
        ResourceAllocationRecord(process_id="P2", resource_id=resources[1].id, allocated_count=1, requested_count=1),
        ResourceAllocationRecord(process_id="P3", resource_id=resources[3].id, allocated_count=2, requested_count=0),
    ]
    db.session.add_all(allocations)
    db.session.add(
        DeadlockEvent(
            detected_at=datetime.utcnow() - timedelta(minutes=22),
            processes_involved="P1,P2",
            resources_involved="DB_CONN,REPORT_GEN",
            resolution_action="Rolled back P2 and released REPORT_GEN",
            resolved_at=datetime.utcnow() - timedelta(minutes=20),
        )
    )


def seed_memory():
    for page_number in range(10):
        loaded_at = datetime.utcnow() - timedelta(minutes=page_number * 3)
        in_memory = page_number % 3 != 0
        db.session.add(
            MemoryPage(
                page_number=page_number,
                loaded_at=loaded_at,
                last_accessed=loaded_at + timedelta(minutes=1),
                access_count=6 + page_number,
                in_memory=in_memory,
            )
        )

    cache_rows = [
        CacheStat(cache_type="customer", hits=72, misses=24, hit_ratio=0.75, timestamp=datetime.utcnow() - timedelta(minutes=4)),
        CacheStat(cache_type="quotation", hits=68, misses=22, hit_ratio=0.76, timestamp=datetime.utcnow() - timedelta(minutes=3)),
        CacheStat(cache_type="user_preference", hits=41, misses=18, hit_ratio=0.69, timestamp=datetime.utcnow() - timedelta(minutes=2)),
    ]
    db.session.add_all(cache_rows)


def seed_io(users):
    io_requests = [
        ("Save Quotation PDF", 45, 4, "SSTF"),
        ("Load Customer Data", 12, 3, "SSTF"),
        ("Generate Report", 78, 7, "LOOK"),
        ("Save Invoice", 23, 4, "FCFS"),
        ("Export Excel", 67, 5, "SCAN"),
    ]
    for index, (request_type, track_number, service_time, algorithm_used) in enumerate(io_requests, start=1):
        db.session.add(
            DiskRequest(
                request_type=request_type,
                track_number=track_number,
                arrival_time=datetime.utcnow() - timedelta(minutes=9 - index),
                service_time=service_time,
                algorithm_used=algorithm_used,
            )
        )

    print_jobs = [
        ("invoice", "invoice_001.pdf", 3, users[0].id, "QUEUED"),
        ("report", "monthly_sales.pdf", 8, users[3].id, "QUEUED"),
        ("quotation", "quotation_approved.pdf", 2, users[1].id, "PRINTED"),
    ]
    for index, (job_type, filename, pages, user_id, status) in enumerate(print_jobs, start=1):
        db.session.add(
            PrintQueueJob(
                job_type=job_type,
                filename=filename,
                pages=pages,
                user_id=user_id,
                submitted_at=datetime.utcnow() - timedelta(minutes=12 - index),
                status=status,
            )
        )


with app.app_context():
    reset_database()
    users = seed_users()
    customers = seed_customers()
    enquiries = seed_enquiries(customers, users)
    quotations = seed_quotations(enquiries)
    seed_orders_and_invoices(quotations)
    processes = seed_processes(users)
    seed_tasks(users)
    seed_threads()
    seed_sync(users, processes)
    seed_deadlock()
    seed_memory()
    seed_io(users)
    db.session.commit()
    print("SalesCRM demo database seeded successfully.")
