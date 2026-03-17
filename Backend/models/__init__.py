from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .customer import Customer
from .cache_stat import CacheStat
from .deadlock_event import DeadlockEvent
from .disk_request import DiskRequest
from .enquiry import Enquiry
from .invoice import Invoice
from .lock_queue_entry import LockQueueEntry
from .lock_record import LockRecord
from .memory_page import MemoryPage
from .process_log import ProcessLog
from .process_record import ProcessRecord
from .print_queue_job import PrintQueueJob
from .quotation import Quotation
from .resource_allocation_record import ResourceAllocationRecord
from .resource_record import ResourceRecord
from .sales_order import SalesOrder
from .task_record import TaskRecord
from .thread_record import ThreadRecord
from .user import User
